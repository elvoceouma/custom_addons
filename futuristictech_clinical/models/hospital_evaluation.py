from odoo import _, api, fields, models

class HospitalEvaluation(models.Model):
    _name = 'hospital.evaluation'
    _description = 'Hospital Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Evaluation ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')



class HospitalGynacology(models.Model):
    _name = 'hospital.gynecology'
    _description = 'Hospital Gynacology'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Gynacology ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
