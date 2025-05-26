from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    speciality_id = fields.Many2one(
        'partner.speciality',
        string='Speciality',
        help='Partner speciality or profession'
    )


class PartnerSpeciality(models.Model):
    _name = 'partner.speciality'
    _description = 'Partner Speciality'
    _order = 'name'

    name = fields.Char(
        string='Speciality Name',
        required=True,
        translate=True
    )
    code = fields.Char(
        string='Code',
        help='Short code for the speciality'
    )
    description = fields.Text(
        string='Description',
        translate=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    _sql_constraints = [
        ('unique_code', 'unique(code)', 'Speciality code must be unique!')
    ]