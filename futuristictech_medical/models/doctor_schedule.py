from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, time

class DoctorSchedule(models.Model):
    _name = 'doctor.schedule'
    _description = 'Doctor Schedule'
    _order = 'day_of_week, start_time'

    # Changed field to support both models with a reference field
    doctor_id = fields.Many2one(
        'res.partner', string='Doctor', required=True, ondelete='cascade',
        domain=[('is_doctor', '=', True)])
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday')],
        string='Day of Week', required=True)
    start_time = fields.Float(string='Start Time', required=True)
    end_time = fields.Float(string='End Time', required=True)
    is_working_day = fields.Boolean(string='Working Day', default=True)
    appointment_duration = fields.Float(
        string='Appointment Duration (minutes)', default=30.0)

    @api.constrains('start_time', 'end_time')
    def _check_time_range(self):
        for schedule in self:
            if schedule.start_time >= schedule.end_time:
                raise ValidationError(
                    _('End time must be after start time!'))
            if schedule.start_time < 0 or schedule.start_time > 24:
                raise ValidationError(
                    _('Start time must be between 0 and 24!'))
            if schedule.end_time < 0 or schedule.end_time > 24:
                raise ValidationError(
                    _('End time must be between 0 and 24!'))

    @api.constrains('doctor_id', 'day_of_week')
    def _check_unique_schedule(self):
        for schedule in self:
            existing = self.search([
                ('doctor_id', '=', schedule.doctor_id.id),
                ('day_of_week', '=', schedule.day_of_week),
                ('id', '!=', schedule.id)
            ])
            if existing:
                raise ValidationError(
                    _('Doctor already has a schedule for this day!'))

    def get_available_slots(self, date):
        self.ensure_one()
        if not self.is_working_day:
            return []
        
        slots = []
        start_dt = datetime.combine(date, time(0, 0))
        start_time = self.start_time
        end_time = self.end_time
        
        while start_time < end_time:
            slot_start = start_time
            slot_end = min(start_time + (self.appointment_duration / 60.0), end_time)
            
            slots.append({
                'start': slot_start,
                'end': slot_end,
                'start_datetime': start_dt.replace(
                    hour=int(slot_start),
                    minute=int((slot_start - int(slot_start)) * 60)),
                'end_datetime': start_dt.replace(
                    hour=int(slot_end),
                    minute=int((slot_end - int(slot_end)) * 60)),
            })
            
            start_time = slot_end
        
        return slots