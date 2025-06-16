# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AppointmentBookingWizard(models.TransientModel):
    _name = 'appointment.booking.wizard'
    _description = 'Appointment Booking Wizard'

    # Lead Information
    lead_id = fields.Many2one('crm.lead', string='Lead', required=True, readonly=True)
    caller_name = fields.Char(string='Caller Name')
    patient_name = fields.Char(string='Patient Name')
    
    # Date and Time
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    time_slots = fields.Many2one('slot.booking', string='Available Time Slots', 
                                domain="[('availability', '=', 'open'), ('start_datetime', '>=', date)]")
    
    # Appointment Details
    appointment_type = fields.Selection([
        ('individual', 'Individual Appointment'),
        ('group', 'Group Appointment'),
        ('family', 'Family Appointment'),
        ('emergency', 'Emergency Appointment')
    ], string='Appointment Type', required=True, default='individual')
    
    package_name = fields.Many2one('medical.package', string='Package Name')
    product = fields.Many2one('product.product', string='Product')
    
    # Location and Doctor
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True)
    sub_campus_id = fields.Many2one('hospital.hospital', string='Sub Campus')
    speciality = fields.Many2one('hospital.physician.speciality', string='Speciality', required=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor',
                               domain="[('active_doctor', '=', True), ('is_company', '=', False), "
                                      "('doctor', '=', True), ('book_appointments', '=', True)]")
    
    # Consultation Type
    consultation_type = fields.Selection([
        ('In-person Consultation', 'In-person Consultation'),
        ('Virtual Consultation', 'Virtual Consultation'),
        ('Home-Based Consultation', 'Home-Based Consultation')
    ], string='Consultation Type', required=True, default='In-person Consultation')
    
    # Payment
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('online', 'Online'),
        ('card', 'Card'),
        ('insurance', 'Insurance')
    ], string='Payment Mode', required=True, default='cash')
    
    free_screening = fields.Boolean(string='Free Screening', default=False)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    
    # Additional fields for location
    geo_location = fields.Char(string='Geographic Location')
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super(AppointmentBookingWizard, self).default_get(fields_list)
        
        # Get lead from context
        lead_id = self.env.context.get('active_id')
        if lead_id and self.env.context.get('active_model') == 'crm.lead':
            lead = self.env['crm.lead'].browse(lead_id)
            res.update({
                'lead_id': lead_id,
                'caller_name': lead.caller_name or lead.name,
                'patient_name': lead.patient_name or lead.name,
                'campus_id': lead.campus_id.id if hasattr(lead, 'campus_id') and lead.campus_id else False,
            })
        
        return res
    
    @api.onchange('speciality', 'campus_id', 'date', 'doctor_id', 'consultation_type')
    def _onchange_filter_time_slots(self):
        """Filter available time slots based on selected criteria"""
        domain = [
            ('availability', '=', 'open'),
            ('start_datetime', '>=', fields.Datetime.now())  # Only future slots
        ]
        
        # Filter by date if provided
        if self.date:
            date_start = datetime.combine(self.date, datetime.min.time())
            date_end = datetime.combine(self.date, datetime.max.time())
            domain.extend([
                ('start_datetime', '>=', date_start),
                ('start_datetime', '<=', date_end)
            ])
        
        # Filter by campus
        if self.campus_id:
            domain.append(('campus_id', '=', self.campus_id.id))
        
        # Filter by sub campus
        if self.sub_campus_id:
            domain.append(('sub_campus_id', '=', self.sub_campus_id.id))
        
        # Filter by doctor
        if self.doctor_id:
            domain.append(('doctor_id', '=', self.doctor_id.id))
        
        # Filter by speciality (through doctor)
        if self.speciality:
            domain.append(('speciality_id', '=', self.speciality.id))
        
        # Filter by consultation type
        if self.consultation_type:
            domain.append(('consultation_type', '=', self.consultation_type))
        
        # Clear time_slots if no matching criteria
        if not (self.date and self.campus_id):
            self.time_slots = False
        
        return {'domain': {'time_slots': domain}}
    
    @api.onchange('doctor_id', 'speciality')
    def _onchange_doctor_speciality(self):
        """Update speciality when doctor is selected, or filter doctors by speciality"""
        if self.doctor_id and hasattr(self.doctor_id, 'speciality_id') and self.doctor_id.speciality_id:
            if not self.speciality:
                self.speciality = self.doctor_id.speciality_id
        
        # Return domain for doctor filtering
        domain = [
            ('active_doctor', '=', True),
            ('is_company', '=', False),
            ('doctor', '=', True),
            ('book_appointments', '=', True)
        ]
        
        if self.speciality:
            domain.append(('speciality_id', '=', self.speciality.id))
        
        if self.campus_id:
            # Assuming doctors are linked to campuses
            domain.append(('campus_ids', 'in', [self.campus_id.id]))
        
        return {'domain': {'doctor_id': domain}}
    
    @api.onchange('campus_id')
    def _onchange_campus(self):
        """Update sub campus domain and clear related fields"""
        self.sub_campus_id = False
        self.doctor_id = False
        self.time_slots = False
        
        if self.campus_id:
            return {
                'domain': {
                    'sub_campus_id': [('parent_id', '=', self.campus_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'sub_campus_id': []
                }
            }
    
    @api.onchange('time_slots')
    def _onchange_time_slots(self):
        """Auto-populate fields from selected time slot"""
        if self.time_slots:
            slot = self.time_slots
            
            # Auto-fill fields from the selected slot
            if not self.doctor_id:
                self.doctor_id = slot.doctor_id
            if not self.campus_id:
                self.campus_id = slot.campus_id
            if not self.sub_campus_id and slot.sub_campus_id:
                self.sub_campus_id = slot.sub_campus_id
            if not self.speciality and slot.speciality_id:
                self.speciality = slot.speciality_id
            if not self.consultation_type and slot.consultation_type:
                self.consultation_type = slot.consultation_type
            
            # Set amount from slot if available
            if slot.amount and not self.amount:
                self.amount = slot.amount
    
    @api.onchange('free_screening')
    def _onchange_free_screening(self):
        """Set amount to 0 for free screening"""
        if self.free_screening:
            self.amount = 0.0
    
    @api.onchange('consultation_type')
    def _onchange_consultation_type(self):
        """Handle consultation type changes"""
        if self.consultation_type == 'Home-Based Consultation':
            # Enable location fields for home consultation
            pass
        elif self.consultation_type == 'Virtual Consultation':
            # Disable location fields for virtual consultation
            self.geo_location = False
    
    def book_appointment(self):
        """Book the selected appointment slot"""
        self.ensure_one()
        
        if not self.time_slots:
            raise UserError(_("Please select a time slot."))
        
        if self.time_slots.availability != 'open':
            raise UserError(_("The selected time slot is no longer available."))
        
        # Update the selected slot with booking information
        booking_values = {
            'lead_id': self.lead_id.id,
            'caller_name': self.caller_name,
            'patient_name': self.patient_name,
            'payment_mode': self.payment_mode,
            'free_screening': self.free_screening,
            'amount': self.amount,
            'availability': 'booked',
            'geo_location': self.geo_location if self.consultation_type == 'Home-Based Consultation' else False,
            'slot_booking_user_id': self.env.user.id,
            'slot_booked_at': fields.Datetime.now(),
        }
        
        # Create virtual consultation URL if needed
        if self.consultation_type == 'Virtual Consultation':
            booking_values['virtual_consultation_url'] = f"https://meeting.hospital.com/room/{self.time_slots.id}"
        
        # Update the slot with booking information
        self.time_slots.write(booking_values)
        
        # Update lead status if needed
        if self.lead_id.state == 'lead':
            self.lead_id.state = 'opportunity'
        
        # Log the booking in chatter
        try:
            self.time_slots.message_post(
                body=_("Appointment booked for %s (Patient: %s) via booking wizard.") % 
                     (self.caller_name, self.patient_name),
                subtype_xmlid="mail.mt_note"
            )
        except Exception as e:
            # If message_post fails, just log it but don't break the booking process
            _logger.warning("Could not post message to slot booking: %s", str(e))
        
        # Return action to view the booked appointment
        return {
            'name': _('Appointment Booked'),
            'type': 'ir.actions.act_window',
            'res_model': 'slot.booking',
            'res_id': self.time_slots.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_availability': 'booked'}
        }
    
    def cancel(self):
        """Cancel the booking wizard"""
        return {'type': 'ir.actions.act_window_close'}