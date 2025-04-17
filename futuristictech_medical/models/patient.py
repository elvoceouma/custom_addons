from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _description = 'Patient Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one(
        'res.partner', string='Related Partner', required=True,
        domain=[('is_patient', '=', True)], tracking=True)
    registration_number = fields.Char(
        string='Registration Number', required=True, tracking=True)
    department_id = fields.Many2one(
        'medical.department', string='Department', tracking=True)
    hospital_id = fields.Many2one(
        'medical.hospital', string='Hospital',
        related='department_id.hospital_id', store=True)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')], string='Blood Group')
    emergency_contact = fields.Many2one(
        'res.partner', string='Emergency Contact',
        domain=[('is_emergency_contact', '=', True)])
    active = fields.Boolean(string='Active', default=True)
    case_ids = fields.One2many(
        'medical.case', 'patient_id', string='Medical Cases')
    appointment_ids = fields.One2many(
        'medical.appointment', 'patient_id', string='Appointments')
    prescription_ids = fields.One2many(
        'medical.prescription', 'patient_id', string='Prescriptions')
    payment_ids = fields.One2many(
        'medical.payment', 'patient_id', string='Payments')
    note = fields.Text(string='Notes')

    _sql_constraints = [
        ('registration_number_unique',
         'UNIQUE(registration_number)',
         'Patient registration number must be unique!'),
    ]

    @api.model
    def create(self, vals):
        patient = super(MedicalPatient, self).create(vals)
        if patient.partner_id:
            patient.partner_id.write({'is_patient': True})
        return patient

    def write(self, vals):
        res = super(MedicalPatient, self).write(vals)
        if 'partner_id' in vals:
            self.partner_id.write({'is_patient': True})
        return res

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.partner_id.name} ({record.registration_number})"
            result.append((record.id, name))
        return result
    
    def action_view_cases(self):
        action = self.env.ref('futuristictech_medical.action_medical_case').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        return action
    def action_view_appointments(self):
        action = self.env.ref('futuristictech_medical.action_medical_appointment').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        return action
    
    def action_view_prescriptions(self):
        action = self.env.ref('futuristictech_medical.action_medical_prescription').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        return action
    
    def action_view_payments(self):
        action = self.env.ref('futuristictech_medical.action_medical_payment').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        return action
    
class ResPartner(models.Model): 
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Is Patient', default=False)
    is_emergency_contact = fields.Boolean(string='Is Emergency Contact', default=False)
    patient_ids = fields.One2many(
        'medical.patient', 'partner_id', string='Patients')
    emergency_contact_ids = fields.One2many(
        'medical.patient', 'emergency_contact', string='Emergency Contacts')
   