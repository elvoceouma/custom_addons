from odoo import models, fields, api, _

class CustomerActivity(models.Model):
    _name = 'customer.activity'
    _description = 'Customer Activity'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    lead_id = fields.Many2one('crm.lead', string='Lead')
    reference_id = fields.Char(string='Reference ID')
    patient_internal_id = fields.Char(string='Patient Internal ID')
    campus_id = fields.Many2one('campus.master', string='Campus')
    reference = fields.Char(string='Reference')
    date = fields.Date(string='Date')
    mrn_no = fields.Char(string='MRN No')
    type = fields.Selection([
        ('visit', 'Visit'),
        ('admission', 'Admission'),
        ('consultation', 'Consultation'),
        ('treatment', 'Treatment')
    ], string='Type')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status')
    value = fields.Float(string='Value')