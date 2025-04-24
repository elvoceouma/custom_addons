from odoo import models, fields

class MedicalLabtestTypes(models.Model):
    _name = 'medical.labtest.types'
    _description = 'Medical Lab Test Types'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Test Name', required=True, tracking=True)
    code = fields.Char(string='Test Code', required=True, tracking=True)
    description = fields.Text(string='Description')
    test_charge = fields.Float(string='Test Charge')
    product_id = fields.Many2one('product.product', string='Related Product')
    active = fields.Boolean(string='Active', default=True)

    _sql_constraints = [
        ('code_unique', 
         'UNIQUE(code)',
         'Test code must be unique!')
    ]