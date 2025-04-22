from odoo import models, fields

class CampusMaster(models.Model):
    _name = 'campus.master'
    _description = 'Campus Master'

    name = fields.Char(string='Campus', required=True)
    code = fields.Char(string='Code')
    address = fields.Text(string='Address')
    active = fields.Boolean(string='Active', default=True)