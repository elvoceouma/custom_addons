# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CancellationRejectionWizard(models.TransientModel):
    _name = 'cancellation.rejection.wizard'
    _description = 'Cancellation Request Rejection Wizard'

    cancellation_request_id = fields.Many2one('cancellation.request', string='Cancellation Request', required=True)
    rejection_reason = fields.Text(string='Rejection Reason', required=True,
                                   placeholder="Please provide a reason for rejecting this cancellation request...")

    def action_reject(self):
        """Reject the cancellation request with the provided reason"""
        self.ensure_one()
        
        if not self.rejection_reason:
            raise ValidationError(_("Rejection reason is required."))
        
        self.cancellation_request_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason
        })
        
        # Send notification to the requester
        self.cancellation_request_id.message_post(
            body=_("Cancellation request rejected. Reason: %s") % self.rejection_reason,
            subtype_xmlid="mail.mt_note",
            partner_ids=[self.cancellation_request_id.requested_by.partner_id.id]
        )
        
        return {'type': 'ir.actions.act_window_close'}


class AppointmentRescheduleWizard(models.TransientModel):
    _name = 'appointment.reschedule.wizard'
    _description = 'Appointment Reschedule Wizard'

    appointment_id = fields.Many2one('slot.booking', string='Current Appointment', required=True)
    new_start_datetime = fields.Datetime(string='New Start Date Time', required=True)
    new_stop_datetime = fields.Datetime(string='New End Date Time', required=True)
    reschedule_reason = fields.Text(string='Reschedule Reason', required=True)
    apply_reschedule_fee = fields.Boolean(string='Apply Reschedule Fee', default=False)
    reschedule_fee = fields.Monetary(string='Reschedule Fee', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

    @api.onchange('new_start_datetime', 'appointment_id')
    def _onchange_new_start_datetime(self):
        """Auto-calculate end time based on original duration"""
        if self.new_start_datetime and self.appointment_id:
            original_duration = self.appointment_id.stop_datetime - self.appointment_id.start_datetime
            self.new_stop_datetime = self.new_start_datetime + original_duration

    @api.constrains('new_start_datetime', 'new_stop_datetime')
    def _check_datetime_consistency(self):
        """Ensure new start datetime is before new stop datetime"""
        for record in self:
            if record.new_start_datetime and record.new_stop_datetime:
                if record.new_start_datetime >= record.new_stop_datetime:
                    raise ValidationError(_("New start date time must be before new end date time."))

    def action_reschedule(self):
        """Reschedule the appointment"""
        self.ensure_one()
        
        # Check if doctor is available at new time
        overlapping = self.env['slot.booking'].search([
            ('doctor_id', '=', self.appointment_id.doctor_id.id),
            ('availability', 'in', ['booked', 'confirm', 'checked_in', 'consulting']),
            ('id', '!=', self.appointment_id.id),
            ('start_datetime', '<', self.new_stop_datetime),
            ('stop_datetime', '>', self.new_start_datetime)
        ])
        
        if overlapping:
            raise ValidationError(_("Doctor %s is not available at the selected time. "
                                  "There is a conflicting appointment.") % self.appointment_id.doctor_id.name)
        
        # Update appointment
        self.appointment_id.write({
            'start_datetime': self.new_start_datetime,
            'stop_datetime': self.new_stop_datetime,
            'availability': 'rescheduled',
            'notes': (self.appointment_id.notes or '') + f"\n\nRescheduled: {self.reschedule_reason}"
        })
        
        # Apply reschedule fee if applicable
        if self.apply_reschedule_fee and self.reschedule_fee > 0:
            self.appointment_id.amount += self.reschedule_fee
        
        # Log the reschedule
        self.appointment_id.message_post(
            body=_("Appointment rescheduled from %s to %s. Reason: %s") % (
                self.appointment_id.start_datetime.strftime('%Y-%m-%d %H:%M'),
                self.new_start_datetime.strftime('%Y-%m-%d %H:%M'),
                self.reschedule_reason
            ),
            subtype_xmlid="mail.mt_note"
        )
        
        return {'type': 'ir.actions.act_window_close'}