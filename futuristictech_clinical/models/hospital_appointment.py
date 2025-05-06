from odoo import _, api, fields, models

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Appointment ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    appointment_date = fields.Datetime(string='Appointment Date', required=True)
    appointment_type_id = fields.Many2one('hospital.appointment.type', string='Appointment Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
    appointment_type_id = fields.Many2one('hospital.appointment.type', string='Appointment Type')
    