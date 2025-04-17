from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalDepartment(models.Model):
    _name = 'medical.department'
    _description = 'Hospital Department'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Department Name', required=True, tracking=True)
    code = fields.Char(string='Department Code', required=True, tracking=True)
    hospital_id = fields.Many2one(
        'medical.hospital', string='Hospital', required=True, tracking=True)
    head_doctor_id = fields.Many2one(
        'medical.doctor', string='Head Doctor', tracking=True)
    doctor_ids = fields.One2many(
        'medical.doctor', 'department_id', string='Doctors')
    patient_ids = fields.One2many(
        'medical.patient', 'department_id', string='Patients')
    active = fields.Boolean(string='Active', default=True)
    note = fields.Text(string='Notes')
    service_ids = fields.Many2many(
        'product.product', string='Services',
        domain=[('type', '=', 'service')])

    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code, hospital_id)',
         'Department code must be unique per hospital!'),
    ]

    @api.constrains('head_doctor_id')
    def _check_head_doctor(self):
        for department in self:
            if department.head_doctor_id and department.head_doctor_id.department_id != department:
                raise ValidationError(
                    _('Head doctor must belong to this department!'))