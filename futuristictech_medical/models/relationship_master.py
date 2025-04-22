from odoo import models, fields

class RelationshipMaster(models.Model):
    _name = 'relationship.master'
    _description = 'Relationship Master'

    name = fields.Char(string='Relationship', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)