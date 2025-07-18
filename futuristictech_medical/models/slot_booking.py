# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class SlotBooking(models.Model):
    _name = 'slot.booking'
    _description = 'Appointment Slot Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Appointment Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    available_slot_id = fields.Many2one('available.slot', string='Available Slot', 
                                        help='Reference to the time slot configuration that generated this slot')
    lead_id = fields.Many2one('crm.lead', string='Lead', tracking=True,
                              domain="[('active', '=', True)]")
    caller_name = fields.Char(string='Caller Name', tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    
    # Doctor and Campus Information
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    sub_campus_id = fields.Many2one('hospital.hospital', string='Sub Campus', tracking=True,
                                    domain="[('parent_id', '=', campus_id)]")
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True, tracking=True,
                                domain="[('active_doctor', '=', True), ('is_company', '=', False), "
                                       "('doctor', '=', True), ('book_appointments', '=', True)]")
    doctor_external_id = fields.Char(string='Doctor External ID', related='doctor_id.doctor_external_id', readonly=True)
    
    speciality_id = fields.Many2one('hospital.physician.speciality', string='Speciality')
    
    start_datetime = fields.Datetime(string='Start Date Time', required=True, tracking=True)
    stop_datetime = fields.Datetime(string='End Date Time', required=True, tracking=True)
    
    consultation_type_ids = fields.Many2many(
        'consultation.type', 
        'slot_consultation_type_rel',  # Explicit table name
        'slot_id', 
        'consultation_type_id',
        string='Consultation Types'
    )
    consultation_type = fields.Selection([
        ('In-person Consultation', 'In-person Consultation'),
        ('Virtual Consultation', 'Virtual Consultation'),
        ('Home-Based Consultation', 'Home-Based Consultation')
    ], string='Consultation Type', required=True, tracking=True)
    
    # Virtual Consultation Fields
    virtual_consultation_url = fields.Char(string='Virtual Consultation URL', 
                                           help='URL for virtual consultation meeting')
    zegocloud_uuid = fields.Char(string='ZegoCloud UUID')
    
    geo_location = fields.Char(string='Geographic Location', 
                               help='Location for home-based consultation')
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    payment_mode = fields.Selection([
        ('cash', 'Cash'),
        ('online', 'Online'),
        ('card', 'Card'),
        ('insurance', 'Insurance')
    ], string='Payment Mode', required=True, default='cash', tracking=True)
    online_payment_url = fields.Char(string='Online Payment URL')
    free_screening = fields.Boolean(string='Free Screening', default=False, tracking=True)
    
    # Payment Details
    customer = fields.Char(string='Customer Name')
    payment_date = fields.Date(string='Payment Date')
    payment_method = fields.Char(string='Payment Method')
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True, default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Status and Workflow
    availability = fields.Selection([
        ('open', 'Open'),
        ('booked', 'Booked'),
        ('confirm', 'Confirmed'),
        ('rescheduled', 'Rescheduled'),
        ('checked_in', 'Checked In'),
        ('consulting', 'Consulting'),
        ('completed', 'Completed'),
        ('inactive', 'Inactive'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled')
    ], string='Availability', default='open', required=True, tracking=True)
    
    # Additional Information
    notes = fields.Text(string='Notes')
    slot_booking_user_id = fields.Many2one('res.users', string='Booked By', 
                                           default=lambda self: self.env.user, readonly=True)
    slot_booked_at = fields.Datetime(string='Booked At', default=fields.Datetime.now, readonly=True)
    
    # Patient Indications - Fixed Many2many field with explicit table name
    patient_indication_ids = fields.Many2many(
        'patient.indication', 
        'slot_patient_indication_rel',  # Explicit table name
        'slot_id', 
        'indication_id',
        string='Patient Indications'
    )
    
    # Feedback
    consultation_feedback_score_new = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Fair'),
        ('3', '3 - Good'),
        ('4', '4 - Very Good'),
        ('5', '5 - Excellent')
    ], string='Consultation Feedback')
    
    # Cancellation Details
    medium_id = fields.Many2one('utm.medium', string='Cancellation Medium', readonly=True)
    cancel_reason = fields.Text(string='Cancellation Reason', readonly=True)
    set_open_bool = fields.Boolean(string='Can Set to Open', readonly=True)
    
    # Registration Form
    registration_count = fields.Integer(string='Registration Count', compute='_compute_registration_count')
    
    # Duration field for display
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    
    # Link to created clinical psychologist session
    clinical_session_id = fields.Many2one('clinical.psychologist.session', string='Clinical Session', readonly=True)
    
    @api.depends('start_datetime', 'stop_datetime')
    def _compute_duration(self):
        for record in self:
            if record.start_datetime and record.stop_datetime:
                delta = record.stop_datetime - record.start_datetime
                record.duration = delta.total_seconds() / 3600  # Convert to hours
            else:
                record.duration = 0.0
    
    @api.depends('lead_id')
    def _compute_registration_count(self):
        for record in self:
            if record.lead_id:
                record.registration_count = self.env['medical.registration.form'].search_count([
                    ('lead_id', '=', record.lead_id.id)
                ])
            else:
                record.registration_count = 0
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('slot.booking') or _('New')
        return super(SlotBooking, self).create(vals)
    
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """Update speciality based on doctor selection"""
        if self.doctor_id and hasattr(self.doctor_id, 'speciality_id'):
            self.speciality_id = self.doctor_id.speciality_id
    
    @api.onchange('consultation_type')
    def _onchange_consultation_type(self):
        """Generate virtual consultation URL for virtual consultations"""
        if self.consultation_type == 'Virtual Consultation':
            # Generate a unique meeting URL (you can customize this logic)
            self.virtual_consultation_url = f"https://meeting.hospital.com/room/{self.id or 'new'}"
    
    @api.onchange('free_screening')
    def _onchange_free_screening(self):
        """Set amount to 0 for free screening"""
        if self.free_screening:
            self.amount = 0.0
    
    @api.constrains('start_datetime', 'stop_datetime')
    def _check_datetime_consistency(self):
        """Ensure start datetime is before stop datetime"""
        for record in self:
            if record.start_datetime and record.stop_datetime:
                if record.start_datetime >= record.stop_datetime:
                    raise ValidationError(_("Start date time must be before end date time."))
    
    @api.constrains('start_datetime', 'doctor_id')
    def _check_doctor_availability(self):
        """Check if doctor is available at the selected time"""
        for record in self:
            if record.start_datetime and record.doctor_id and record.availability in ['booked', 'confirm']:
                # Check for overlapping appointments
                overlapping = self.search([
                    ('doctor_id', '=', record.doctor_id.id),
                    ('availability', 'in', ['booked', 'confirm', 'checked_in', 'consulting']),
                    ('id', '!=', record.id),
                    ('start_datetime', '<', record.stop_datetime),
                    ('stop_datetime', '>', record.start_datetime)
                ])
                if overlapping:
                    raise ValidationError(_("Doctor %s is not available at the selected time. "
                                          "There is a conflicting appointment.") % record.doctor_id.name)
    
    def book_slot(self):
        """Book the slot"""
        self.ensure_one()
        if self.availability != 'open':
            raise UserError(_("Only open slots can be booked."))
        self.availability = 'booked'
        self.slot_booked_at = fields.Datetime.now()
        return True
    
    def act_confirm(self):
        """Confirm the appointment"""
        self.ensure_one()
        if self.availability != 'booked':
            raise UserError(_("Only booked appointments can be confirmed."))
        self.availability = 'confirm'
        return True
    
    def check_in(self):
        """Check in the patient and create clinical psychologist session"""
        self.ensure_one()
        if self.availability not in ['booked', 'confirm']:
            raise UserError(_("Only confirmed appointments can be checked in."))
        
        # Update availability to checked_in
        self.availability = 'checked_in'
        
        # Create clinical psychologist session
        session_vals = self._prepare_clinical_session_values()
        clinical_session = self.env['clinical.psychologist.session'].create(session_vals)
        
        # Link the created session to this slot booking
        self.clinical_session_id = clinical_session.id
        
        # Log the check-in and session creation
        self.message_post(
            body=_("Patient checked in. Clinical Psychologist Session created: %s") % clinical_session.name,
            subtype_xmlid="mail.mt_note"
        )
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Clinical Psychologist Session'),
            'res_model': 'clinical.psychologist.session',
            'res_id': clinical_session.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _prepare_clinical_session_values(self):
        """Prepare values for creating clinical psychologist session"""
        self.ensure_one()
        
        # Get patient from lead or create if needed
        patient_id = False
        if self.lead_id:
            # Try to find existing patient partner
            patient_partner = self.env['res.partner'].search([
                ('name', '=', self.patient_name),
                ('is_company', '=', False)
            ], limit=1)
            
            if not patient_partner:
                # Create patient partner if not exists
                patient_partner = self.env['res.partner'].create({
                    'name': self.patient_name,
                    'is_company': False,
                    'customer_rank': 1,
                    'phone': getattr(self.lead_id, 'phone', False),
                    'email': getattr(self.lead_id, 'email_from', False),
                })
            
            patient_id = patient_partner.id
        
        # Determine consultation type based on slot consultation type
        consultation_type_mapping = {
            'In-person Consultation': 'clinic',
            'Virtual Consultation': 'virtual',
            'Home-Based Consultation': 'home'
        }
        
        consultation_type = consultation_type_mapping.get(self.consultation_type, 'clinic')
        
        # Determine type (ip/op) - assuming outpatient by default
        # You can modify this logic based on your business rules
        session_type = 'op'
        
        session_vals = {
            'type': session_type,
            'patient_id': patient_id,
            'date': self.start_datetime.date(),
            'consultation_type': consultation_type,
            'check_in_datetime': fields.Datetime.now(),
            'state': 'started',  # Auto start the session upon check-in
            # Map doctor to clinical psychologist if applicable
            'clinical_psychologist_id': self._get_clinical_psychologist(),
            # Add virtual consultation URL if applicable
            'virtual_consultation_url': self.virtual_consultation_url if consultation_type == 'virtual' else False,
            'geo_location': self.geo_location if consultation_type == 'home' else False,
        }
        
        # Add inpatient/outpatient specific fields if available
        if session_type == 'ip':
            # Add inpatient admission logic here if needed
            pass
        else:
            # For outpatient, you might want to create or link to an OP visit
            # session_vals['op_visit_id'] = self._get_or_create_op_visit()
            pass
        
        return session_vals
    
    def _get_clinical_psychologist(self):
        """Get the clinical psychologist user ID"""
        # If the doctor is a clinical psychologist, return their user
        if self.doctor_id:
            # Try to find user associated with the doctor
            user = self.env['res.users'].search([
                ('partner_id', '=', self.doctor_id.id)
            ], limit=1)
            if user:
                return user.id
        
        # Return current user as fallback
        return self.env.user.id
    
    def start_consultation(self):
        """Start the consultation"""
        self.ensure_one()
        if self.availability != 'checked_in':
            raise UserError(_("Patient must be checked in before starting consultation."))
        self.availability = 'consulting'
        return True
    
    def finish_consultation(self):
        """Finish the consultation"""
        self.ensure_one()
        if self.availability != 'consulting':
            raise UserError(_("Consultation must be started before finishing."))
        self.availability = 'completed'
        
        # Complete the linked clinical session if exists
        if self.clinical_session_id and self.clinical_session_id.state != 'completed':
            self.clinical_session_id.action_complete()
        
        return True
    
    def re_schedule_appointment(self):
        """Re-schedule the appointment"""
        self.ensure_one()
        if self.availability not in ['booked', 'confirm']:
            raise UserError(_("Only booked or confirmed appointments can be rescheduled."))
        
        return {
            'name': _('Reschedule Appointment'),
            'type': 'ir.actions.act_window',
            'res_model': 'appointment.reschedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_appointment_id': self.id}
        }
    
    def act_no_show(self):
        """Mark as no show"""
        self.ensure_one()
        if self.availability not in ['booked', 'confirm']:
            raise UserError(_("Only booked or confirmed appointments can be marked as no show."))
        self.availability = 'no_show'
        return True
    
    def action_inactive(self):
        """Mark as inactive"""
        self.ensure_one()
        if self.availability != 'open':
            raise UserError(_("Only open slots can be marked as inactive."))
        self.availability = 'inactive'
        return True
    
    def reset_to_draft(self):
        """Reset to open status"""
        self.ensure_one()
        if self.availability != 'cancelled' or self.set_open_bool:
            raise UserError(_("Cannot reset this appointment to open status."))
        self.availability = 'open'
        return True
    
    def action_view_registration(self):
        """View registration forms"""
        self.ensure_one()
        return {
            'name': _('Registration Forms'),
            'type': 'ir.actions.act_window',
            'res_model': 'medical.registration.form',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.lead_id.id)] if self.lead_id else [],
            'context': {'default_lead_id': self.lead_id.id} if self.lead_id else {}
        }
    
    def action_view_clinical_session(self):
        """View the linked clinical psychologist session"""
        self.ensure_one()
        if not self.clinical_session_id:
            raise UserError(_("No clinical session has been created for this appointment."))
        
        return {
            'name': _('Clinical Psychologist Session'),
            'type': 'ir.actions.act_window',
            'res_model': 'clinical.psychologist.session',
            'res_id': self.clinical_session_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def unlink(self):
        """Prevent deletion of non-draft appointments"""
        for record in self:
            if record.availability not in ['open', 'cancelled']:
                raise UserError(_("You cannot delete appointments that are not in open or cancelled state."))
        return super(SlotBooking, self).unlink()


class PatientIndication(models.Model):
    _name = 'patient.indication'
    _description = 'Patient Indication'
    _rec_name = 'name'

    name = fields.Char(string='Indication Name', required=True, help='Name of the patient indication')
    description = fields.Text(string='Description', help='Detailed description of the indication')

    slot_booking_ids = fields.Many2many(
        'slot.booking',
        'slot_patient_indication_rel',  # Explicit table name
        'indication_id',
        'slot_id',
        string='Slot Bookings'
    )
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'The indication name must be unique.')
    ]