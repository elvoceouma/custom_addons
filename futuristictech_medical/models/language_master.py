from odoo import models, fields

class LanguageMaster(models.Model):
    _name = 'language.master'
    _description = 'Language Master'

    name = fields.Char(string='Language', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)