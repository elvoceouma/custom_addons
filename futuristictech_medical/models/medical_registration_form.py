from odoo import models, fields, api, _

class MedicalRegistrationForm(models.Model):
    _name = 'medical.registration.form'
    _description = 'Medical Registration Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, default='/')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    patient_id = fields.Many2one('medical.patient', string='Patient')
    date = fields.Date(string='Date', default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.registration.form') or '/'
        return super(MedicalRegistrationForm, self).create(vals)