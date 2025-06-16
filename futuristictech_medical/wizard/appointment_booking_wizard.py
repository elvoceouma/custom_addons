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
   
    time_slots = fields.Selection(selection='_get_available_time_slots', string='Time Slots', required=True)
    
    @api.model
    def _get_available_time_slots(self):
        slots = []
        if self.doctor_id and self.date:
            schedule = self.env['doctor.schedule'].search([
                ('doctor_id', '=', self.doctor_id.id),
                ('day_of_week', '=', str(self.date.weekday())),
                ('is_working_day', '=', True)
            ], limit=1)
            if schedule:
                return [(str(schedule.start_time), f"{int(schedule.start_time):02d}:00"),
                        (str(schedule.end_time), f"{int(schedule.end_time):02d}:00")]
        return slots
    
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
    campus_id = fields.Many2one('medical.hospital', string='Campus', required=True)
    sub_campus_id = fields.Many2one('medical.hospital', string='Sub Campus',
                                    )
    speciality = fields.Many2one('hospital.physician.speciality', string='Speciality', required=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor',
                               )
    
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
                'caller_name': lead.contact_name or lead.name,
                'patient_name': lead.patient_name or lead.name,
                'campus_id': lead.campus_id.id if lead.campus_id else False,
            })
        
        return res
    
    @api.onchange('speciality', 'campus_id', 'date')
    def _onchange_filter_doctors(self):
        """Filter doctors based on speciality and campus"""
        domain = [
            ('active_doctor', '=', True),
            ('is_company', '=', False),
            ('doctor', '=', True),
            ('book_appointments', '=', True)
        ]
        
        if self.speciality:
            domain.append(('speciality_id', '=', self.speciality.id))
        
        if self.campus_id:
            domain.append(('campus_ids', 'in', [self.campus_id.id]))
        
        return {'domain': {'doctor_id': domain}}
    
    @api.onchange('doctor_id', 'date')
    def _onchange_generate_time_slots(self):
        """Generate available time slots for the selected doctor and date"""
        if not self.doctor_id or not self.date:
            self.time_slots = False
            return
        
        # Get doctor's schedule for the selected date
        weekday = self.date.weekday()  # 0=Monday, 6=Sunday
        
        # Find doctor schedule
        schedule = self.env['doctor.schedule'].search([
            ('doctor_id', '=', self.doctor_id.id),
            ('day_of_week', '=', str(weekday)),
            ('is_working_day', '=', True)
        ], limit=1)
        
        if not schedule:
            self.time_slots = False
            return
        
        # Generate time slots (example: 30-minute intervals)
        slots = []
        start_time = schedule.start_time
        end_time = schedule.end_time
        slot_duration = 0.5  # 30 minutes
        
        current_time = start_time
        while current_time < end_time:
            # Convert float time to datetime
            hour = int(current_time)
            minute = int((current_time - hour) * 60)
            
            # Create datetime for checking availability
            slot_datetime = datetime.combine(self.date, datetime.min.time().replace(hour=hour, minute=minute))
            
            # Check if slot is available
            existing_appointments = self.env['slot.booking'].search([
                ('doctor_id', '=', self.doctor_id.id),
                ('start_datetime', '=', slot_datetime),
                ('availability', 'in', ['booked', 'confirm', 'checked_in', 'consulting'])
            ])
            
            if not existing_appointments:
                time_str = f"{hour:02d}:{minute:02d}"
                slots.append((str(current_time), time_str))
            
            current_time += slot_duration
        
        # Update selection field
        self.time_slots = False
        field = self._fields['time_slots']
        field.selection = slots
    
    @api.onchange('free_screening')
    def _onchange_free_screening(self):
        """Set amount to 0 for free screening"""
        if self.free_screening:
            self.amount = 0.0
    
    @api.onchange('consultation_type')
    def _onchange_consultation_type(self):
        """Handle consultation type changes"""
        if self.consultation_type == 'Home-Based Consultation':
            # You might want to enable location fields
            pass
        elif self.consultation_type == 'Virtual Consultation':
            # You might want to disable location fields
            self.geo_location = False
    
    def book_appointment(self):
        """Create the appointment booking"""
        self.ensure_one()
        
        if not self.time_slots:
            raise UserError(_("Please select a time slot."))
        
        # Parse the selected time slot
        selected_time = float(self.time_slots)
        hour = int(selected_time)
        minute = int((selected_time - hour) * 60)
        
        # Create start and end datetime
        start_datetime = datetime.combine(self.date, datetime.min.time().replace(hour=hour, minute=minute))
        end_datetime = start_datetime + timedelta(minutes=30)  # Default 30-minute appointment
        
        # Prepare values for slot booking
        vals = {
            'lead_id': self.lead_id.id,
            'caller_name': self.caller_name,
            'patient_name': self.patient_name,
            'campus_id': self.campus_id.id,
            'sub_campus_id': self.sub_campus_id.id if self.sub_campus_id else False,
            'doctor_id': self.doctor_id.id,
            'speciality_id': self.speciality.id,
            'start_datetime': start_datetime,
            'stop_datetime': end_datetime,
            'consultation_type': self.consultation_type,
            'payment_mode': self.payment_mode,
            'free_screening': self.free_screening,
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'availability': 'booked',
            'geo_location': self.geo_location if self.consultation_type == 'Home-Based Consultation' else False,
        }
        
        # Create virtual consultation URL if needed
        if self.consultation_type == 'Virtual Consultation':
            vals['virtual_consultation_url'] = f"https://meeting.hospital.com/room/{self.lead_id.id}"
        
        # Create the slot booking
        slot_booking = self.env['slot.booking'].create(vals)
        
        # Update lead status if needed
        if self.lead_id.state == 'lead':
            self.lead_id.state = 'opportunity'
        
        # Return action to view the created appointment
        return {
            'name': _('Appointment Booked'),
            'type': 'ir.actions.act_window',
            'res_model': 'slot.booking',
            'res_id': slot_booking.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def cancel(self):
        """Cancel the booking wizard"""
        return {'type': 'ir.actions.act_window_close'}