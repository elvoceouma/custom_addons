from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class MedicalAppointment(models.Model):
    _name = 'medical.appointment'
    _description = 'Medical Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, id desc'

    name = fields.Char(string='Appointment Reference', required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'medical.patient', string='Patient', required=True, tracking=True)
    doctor_id = fields.Many2one(
        'medical.doctor', string='Doctor', required=True, tracking=True)
    department_id = fields.Many2one(
        'medical.department', string='Department',
        related='doctor_id.department_id', store=True)
    hospital_id = fields.Many2one(
        'medical.hospital', string='Hospital',
        related='department_id.hospital_id', store=True)
    appointment_date = fields.Datetime(
        string='Appointment Date', required=True, tracking=True)
    end_time = fields.Datetime(string='End Time', compute='_compute_end_time', store=True)
    duration = fields.Float(string='Duration (minutes)', default=30.0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    purpose = fields.Text(string='Appointment Purpose')
    case_id = fields.Many2one('medical.case', string='Medical Case')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or _('New')
        return super(MedicalAppointment, self).create(vals)

    @api.depends('appointment_date', 'duration')
    def _compute_end_time(self):
        for appointment in self:
            if appointment.appointment_date:
                duration_timedelta = timedelta(minutes=appointment.duration)
                appointment.end_time = appointment.appointment_date + duration_timedelta
            else:
                appointment.end_time = False

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})
        # Create a case if this is a new patient encounter
        if not self.case_id:
            case_vals = {
                'patient_id': self.patient_id.id,
                'doctor_id': self.doctor_id.id,
                'symptoms': self.purpose,
            }
            case = self.env['medical.case'].create(case_vals)
            self.write({'case_id': case.id})
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        if self.doctor_id:
            self.department_id = self.doctor_id.department_id.id

    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        for appointment in self:
            if appointment.appointment_date and appointment.appointment_date < fields.Datetime.now():
                raise ValidationError(_('Cannot schedule appointments in the past!'))

    def check_availability(self):
        """Check if the doctor is available at the selected time"""
        self.ensure_one()
        if not (self.doctor_id and self.appointment_date):
            return False
            
        # Convert appointment date to day of week (0-6, Monday is 0)
        day_of_week = str(self.appointment_date.weekday())
        
        # Find doctor schedule for this day
        schedule = self.env['doctor.schedule'].search([
            ('doctor_id', '=', self.doctor_id.id),
            ('day_of_week', '=', day_of_week),
            ('is_working_day', '=', True)
        ], limit=1)
        
        if not schedule:
            return False
            
        # Check if time is within doctor's working hours
        app_time = self.appointment_date.hour + self.appointment_date.minute / 60.0
        if app_time < schedule.start_time or app_time > schedule.end_time:
            return False
            
        # Check for overlapping appointments
        end_time = self.end_time or (self.appointment_date + timedelta(minutes=self.duration))
        overlapping = self.search([
            ('doctor_id', '=', self.doctor_id.id),
            ('state', 'in', ['confirmed', 'done']),
            ('id', '!=', self.id),
            '|',
            '&', ('appointment_date', '<=', self.appointment_date), ('end_time', '>', self.appointment_date),
            '&', ('appointment_date', '<', end_time), ('appointment_date', '>=', self.appointment_date)
        ])
        
        return not overlapping