from odoo import models, fields

class PhysicalCondition(models.Model):
    _name = 'physical.condition'
    _description = 'Physical Condition'

    name = fields.Char(string='Condition', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)