from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalDoctor(models.Model):
    _name = 'medical.doctor'
    _description = 'Doctor Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        domain=[('is_doctor', '=', True)], tracking=True)
    department_id = fields.Many2one(
        'medical.department', string='Department', tracking=True)
    hospital_id = fields.Many2one(
        'medical.hospital', string='Hospital',
        related='department_id.hospital_id', store=True)
    specialization = fields.Char(string='Specialization', tracking=True)
    license_number = fields.Char(
        string='License Number', required=True, tracking=True)
    active = fields.Boolean(string='Active', default=True)
    schedule_ids = fields.One2many(
        'doctor.schedule', 'doctor_id', string='Schedules')
    appointment_ids = fields.One2many(
        'medical.appointment', 'doctor_id', string='Appointments')
    case_ids = fields.One2many(
        'medical.case', 'doctor_id', string='Medical Cases')
    note = fields.Text(string='Notes')

    _sql_constraints = [
        ('license_number_unique',
         'UNIQUE(license_number)',
         'Doctor license number must be unique!'),
    ]

    @api.model
    def create(self, vals):
        doctor = super(MedicalDoctor, self).create(vals)
        if doctor.employee_id:
            doctor.employee_id.write({'is_doctor': True})
        return doctor

    def write(self, vals):
        res = super(MedicalDoctor, self).write(vals)
        if 'employee_id' in vals:
            self.employee_id.write({'is_doctor': True})
        return res

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.employee_id.name} ({record.specialization})"
            result.append((record.id, name))
        return result
    
    def action_view_schedules(self):
        action = self.env.ref('futuristictech_medical.action_doctor_schedule').read()[0]
        action['domain'] = [('doctor_id', '=', self.id)]
        return action
    
    def action_view_appointments(self): 
        action = self.env.ref('futuristictech_medical.action_medical_appointment').read()[0]
        action['domain'] = [('doctor_id', '=', self.id)]
        return action
    
    def action_view_cases(self):
        action = self.env.ref('futuristictech_medical.action_medical_case').read()[0]
        action['domain'] = [('doctor_id', '=', self.id)]
        return action
    
    
    
    
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_doctor = fields.Boolean(string='Is Doctor', default=False)
    is_patient = fields.Boolean(string='Is Patient', default=False)
    is_emergency_contact = fields.Boolean(string='Is Emergency Contact', default=False)
    doctor_ids = fields.One2many(
        'medical.doctor', 'employee_id', string='Doctors')
    