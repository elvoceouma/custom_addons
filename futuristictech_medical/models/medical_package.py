from odoo import models, fields, api, _

class MedicalPackage(models.Model):
    _name = 'medical.package'
    _description = 'Medical Package'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Package Name', required=True)
    reference = fields.Char(string='Reference', readonly=True, default='/')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    patient_id = fields.Many2one('medical.patient', string='Patient')
    package_type = fields.Selection([
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('vip', 'VIP')
    ], string='Package Type', default='standard')
    price = fields.Float(string='Price')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('reference', '/') == '/':
            vals['reference'] = self.env['ir.sequence'].next_by_code('medical.package') or '/'
        return super(MedicalPackage, self).create(vals)