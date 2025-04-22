from odoo import models, fields

class PrimaryTag(models.Model):
    _name = 'primary.tag'
    _description = 'Primary Tags for CRM Leads'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

class SecondaryTag(models.Model):
    _name = 'secondary.tag'
    _description = 'Secondary Tags for CRM Leads'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

class TertiaryTag(models.Model):
    _name = 'tertiary.tag'
    _description = 'Tertiary Tags for CRM Leads'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)

class DiscardTag(models.Model):
    _name = 'discard.tag'
    _description = 'Discard Tags for CRM Leads'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)