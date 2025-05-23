from odoo import _, api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    related_doctor_id = fields.Many2one('hospital.physician', string='Related Doctor')