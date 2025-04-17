from odoo import models, fields, api, _
from odoo import tools
from odoo.exceptions import ValidationError

class MedicalHospital(models.Model):
    _name = 'medical.hospital'
    _description = 'Hospital Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Hospital Name', required=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner', string='Related Partner', required=True,
        domain=[('is_company', '=', True)], tracking=True)
    registration_number = fields.Char(
        string='Registration Number', required=True, tracking=True)
    license_number = fields.Char(
        string='License Number', required=True, tracking=True)
    image = fields.Binary(string='Hospital Image')
    active = fields.Boolean(string='Active', default=True)
    street = fields.Char(string='Street')
    street2 = fields.Char(string='Street2')
    zip = fields.Char(string='Zip')
    city = fields.Char(string='City')
    state_id = fields.Many2one(
        'res.country.state', string='State', ondelete='restrict')
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    department_ids = fields.One2many(
        'medical.department', 'hospital_id', string='Departments')
    doctor_ids = fields.One2many(
        'medical.doctor', 'hospital_id', string='Doctors')
    patient_ids = fields.One2many(
        'medical.patient', 'hospital_id', string='Patients')
    note = fields.Text(string='Notes')

    _sql_constraints = [
        ('registration_number_unique',
         'UNIQUE(registration_number)',
         'Hospital registration number must be unique!'),
        ('license_number_unique',
         'UNIQUE(license_number)',
         'Hospital license number must be unique!'),
    ]

    @api.constrains('email')
    def _check_email(self):
        for hospital in self:
            if hospital.email and not tools.single_email_re.match(hospital.email):
                raise ValidationError(_('Invalid email address!'))

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.registration_number})"
            result.append((record.id, name))
        return result
    
    def action_view_departments(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_department').read()[0]
        action['domain'] = [('hospital_id', '=', self.id)]
        return action
    
    def action_view_doctors(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_doctor').read()[0]
        action['domain'] = [('hospital_id', '=', self.id)]
        return action
    
    def action_view_patients(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_patient').read()[0]
        action['domain'] = [('hospital_id', '=', self.id)]
        return action