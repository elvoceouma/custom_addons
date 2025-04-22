from odoo import models, fields

class ServicesMaster(models.Model):
    _name = 'services.master'
    _description = 'Services Master'

    name = fields.Char(string='Service', required=True)
    code = fields.Char(string='Code')
    child_ids = fields.One2many('service.child.master', 'parent_id', string='Child Services')
    active = fields.Boolean(string='Active', default=True)

class ServiceChildMaster(models.Model):
    _name = 'service.child.master'
    _description = 'Service Child Master'

    name = fields.Char(string='Service', required=True)
    code = fields.Char(string='Code')
    parent_id = fields.Many2one('services.master', string='Parent Service')
    type = fields.Selection([
        ('deaddiction', 'De Addiction'),
        ('mental illness', 'Mental Illness'),
        ('mental retardation', 'Mental Retardation'),
        ('old age physiatric problem', 'Old Age Psychiatric Problem')
    ], string='Type')
    active = fields.Boolean(string='Active', default=True)