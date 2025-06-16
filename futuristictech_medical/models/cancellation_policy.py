# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CancellationPolicy(models.Model):
    _name = 'cancellation.policy'
    _description = 'Appointment Cancellation Policy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char(string='Policy Name', required=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    
    # Policy Configuration
    policy_type = fields.Selection([
        ('time_based', 'Time Based'),
        ('fixed_fee', 'Fixed Fee'),
        ('percentage', 'Percentage Based'),
        ('no_refund', 'No Refund')
    ], string='Policy Type', required=True, default='time_based', tracking=True)
    
    description = fields.Text(string='Policy Description')
    
    # Time-based Configuration
    hours_before = fields.Integer(string='Hours Before Appointment', 
                                  help='Minimum hours before appointment for cancellation')
    
    # Fee Configuration
    cancellation_fee = fields.Monetary(string='Cancellation Fee', currency_field='currency_id')
    refund_percentage = fields.Float(string='Refund Percentage', digits=(5, 2),
                                     help='Percentage of amount to refund (0-100)')
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Applicability
    consultation_type_ids = fields.Many2many(
        'consultation.type',
        'policy_consultation_type_rel',
        'policy_id',
        'consultation_type_id',
        string='Applicable for Consultation Types',
        help='Leave empty to apply to all consultation types'
    )
    
    campus_ids = fields.Many2many(
        'hospital.hospital',
        'policy_campus_rel',
        'policy_id',
        'campus_id',
        string='Applicable for Campuses',
        help='Leave empty to apply to all campuses'
    )
    
    doctor_ids = fields.Many2many(
        'res.partner',
        'policy_doctor_rel',
        'policy_id',
        'doctor_id',
        string='Applicable for Doctors',
        domain="[('doctor', '=', True)]",
        help='Leave empty to apply to all doctors'
    )
    
    # Policy Rules
    allow_rescheduling = fields.Boolean(string='Allow Rescheduling', default=True)
    max_reschedules = fields.Integer(string='Maximum Reschedules', default=2)
    reschedule_fee = fields.Monetary(string='Rescheduling Fee', currency_field='currency_id')
    
    # Terms and Conditions
    terms_and_conditions = fields.Html(string='Terms and Conditions')
    
    @api.constrains('refund_percentage')
    def _check_refund_percentage(self):
        for record in self:
            if record.policy_type == 'percentage' and (record.refund_percentage < 0 or record.refund_percentage > 100):
                raise ValidationError(_("Refund percentage must be between 0 and 100."))
    
    @api.constrains('hours_before')
    def _check_hours_before(self):
        for record in self:
            if record.policy_type == 'time_based' and record.hours_before < 0:
                raise ValidationError(_("Hours before appointment cannot be negative."))
    
    def calculate_refund_amount(self, appointment_amount, hours_before_cancellation):
        """Calculate refund amount based on policy"""
        self.ensure_one()
        
        if self.policy_type == 'no_refund':
            return 0.0
        
        elif self.policy_type == 'fixed_fee':
            refund = appointment_amount - self.cancellation_fee
            return max(0.0, refund)
        
        elif self.policy_type == 'percentage':
            return appointment_amount * (self.refund_percentage / 100)
        
        elif self.policy_type == 'time_based':
            if hours_before_cancellation >= self.hours_before:
                # Full refund if cancelled within policy time
                return appointment_amount - self.cancellation_fee
            else:
                # Partial or no refund if cancelled too late
                return appointment_amount * (self.refund_percentage / 100)
        
        return 0.0
    
    def is_applicable_for_appointment(self, appointment):
        """Check if this policy is applicable for the given appointment"""
        self.ensure_one()
        
        # Check consultation type
        if self.consultation_type_ids:
            if not any(ct.id in appointment.consultation_type_ids.ids for ct in self.consultation_type_ids):
                return False
        
        # Check campus
        if self.campus_ids and appointment.campus_id.id not in self.campus_ids.ids:
            return False
        
        # Check doctor
        if self.doctor_ids and appointment.doctor_id.id not in self.doctor_ids.ids:
            return False
        
        return True


class CancellationRequest(models.Model):
    _name = 'cancellation.request'
    _description = 'Appointment Cancellation Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    appointment_id = fields.Many2one('slot.booking', string='Appointment', required=True, tracking=True)
    policy_id = fields.Many2one('cancellation.policy', string='Applied Policy', tracking=True)
    
    # Request Details
    cancellation_reason = fields.Text(string='Cancellation Reason', required=True)
    requested_by = fields.Many2one('res.users', string='Requested By', 
                                   default=lambda self: self.env.user, readonly=True)
    request_date = fields.Datetime(string='Request Date', default=fields.Datetime.now, readonly=True)
    
    # Calculation Details
    original_amount = fields.Monetary(string='Original Amount', currency_field='currency_id', readonly=True)
    cancellation_fee = fields.Monetary(string='Cancellation Fee', currency_field='currency_id', readonly=True)
    refund_amount = fields.Monetary(string='Refund Amount', currency_field='currency_id', readonly=True)
    hours_before_appointment = fields.Float(string='Hours Before Appointment', readonly=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Approval Details
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True)
    rejection_reason = fields.Text(string='Rejection Reason')
    
    @api.depends('appointment_id')
    def _compute_display_name(self):
        for record in self:
            if record.appointment_id:
                record.display_name = f"Cancellation - {record.appointment_id.name}"
            else:
                record.display_name = "New Cancellation Request"
    
    @api.model
    def create(self, vals):
        # Auto-calculate refund details when creating
        if 'appointment_id' in vals:
            appointment = self.env['slot.booking'].browse(vals['appointment_id'])
            policy = self._get_applicable_policy(appointment)
            
            if policy:
                vals['policy_id'] = policy.id
                vals['original_amount'] = appointment.amount
                
                # Calculate hours before appointment
                if appointment.start_datetime:
                    delta = appointment.start_datetime - fields.Datetime.now()
                    hours_before = delta.total_seconds() / 3600
                    vals['hours_before_appointment'] = hours_before
                    
                    # Calculate refund
                    refund = policy.calculate_refund_amount(appointment.amount, hours_before)
                    vals['refund_amount'] = refund
                    vals['cancellation_fee'] = appointment.amount - refund
        
        return super(CancellationRequest, self).create(vals)
    
    def _get_applicable_policy(self, appointment):
        """Find the most specific applicable policy for an appointment"""
        policies = self.env['cancellation.policy'].search([('active', '=', True)], order='sequence')
        
        for policy in policies:
            if policy.is_applicable_for_appointment(appointment):
                return policy
        
        return False
    
    def action_submit(self):
        """Submit the cancellation request"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_("Only draft requests can be submitted."))
        self.state = 'submitted'
        return True
    
    def action_approve(self):
        """Approve the cancellation request"""
        self.ensure_one()
        if self.state != 'submitted':
            raise ValidationError(_("Only submitted requests can be approved."))
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approval_date': fields.Datetime.now()
        })
        return True
    
    def action_reject(self):
        """Reject the cancellation request"""
        self.ensure_one()
        if self.state != 'submitted':
            raise ValidationError(_("Only submitted requests can be rejected."))
        
        return {
            'name': _('Rejection Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'cancellation.rejection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_cancellation_request_id': self.id}
        }
    
    def action_process(self):
        """Process the approved cancellation"""
        self.ensure_one()
        if self.state != 'approved':
            raise ValidationError(_("Only approved requests can be processed."))
        
        # Cancel the appointment
        self.appointment_id.write({
            'availability': 'cancelled',
            'cancel_reason': self.cancellation_reason,
            'medium_id': self.env.ref('utm.utm_medium_website').id  # or appropriate medium
        })
        
        # Create refund record if applicable
        if self.refund_amount > 0:
            self._create_refund_record()
        
        self.state = 'processed'
        
        # Log message
        self.message_post(
            body=_("Cancellation processed. Appointment cancelled and refund of %s initiated.") % self.refund_amount,
            subtype_xmlid="mail.mt_note"
        )
        
        return True
    
    def _create_refund_record(self):
        """Create a refund record (placeholder - implement based on your payment system)"""
        # This is a placeholder. Implement according to your payment processing system
        refund_vals = {
            'appointment_id': self.appointment_id.id,
            'amount': self.refund_amount,
            'reason': 'Appointment Cancellation',
            'processed_by': self.env.user.id,
            'processed_date': fields.Datetime.now()
        }
        # self.env['payment.refund'].create(refund_vals)
        pass