from odoo import models, fields, api, _

class AppointmentSlotLink(models.Model):
    _name = 'appointment.slot.link'
    _description = 'Appointment Slot Link'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    lead_id = fields.Many2one('crm.lead', string='Lead')
    appointment_subject = fields.Char(string='Appointment Subject')
    doctor_id = fields.Many2one('res.partner', string='Doctor', domain="[('is_doctor', '=', True)]")
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    speciality = fields.Char(string='Speciality')
    consultation_type = fields.Selection([
        ('in_person', 'In-Person'),
        ('virtual', 'Virtual'),
        ('home', 'Home Visit'),
        ('free_screening', 'Free Screening')
    ], string='Consultation Type')
    free_screening = fields.Boolean(string='Free Screening')
    start_datetime = fields.Datetime(string='Start Datetime')