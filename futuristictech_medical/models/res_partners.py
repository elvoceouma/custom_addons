from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_doctor = fields.Boolean(string='Is Doctor', default=False)
    # Patient fields
    
    avalara_show_address_validation = fields.Boolean(string='Show Address Validation', default=False)
    avatax_unique_code = fields.Char(string='Unique Code')
    avalara_partner_code = fields.Char(string='Avalara Partner Code')
    avalara_exemption_id = fields.Char(string='Avalara Exemption ID')
    language_preference = fields.Many2many('language.master',
    'res_partner_language_rel',  
    'partner_id',  
    'language_id',  
    string="Language Preference")

    # Doctor fields
    doctor_license_number = fields.Char(string='Doctor License Number', required=False)
    doctor_department_id = fields.Many2one('medical.department', string='Department')
    doctor_hospital_id = fields.Many2one(
        'medical.hospital', string='Campus',
        related='doctor_department_id.hospital_id', store=True, readonly=False)
    specialization = fields.Char(string='Specialization')
    
    # Fix for the relationship to the correct model
    schedule_ids = fields.One2many('doctor.schedule', 'doctor_id', string='Schedules')
    doctor_appointment_ids = fields.One2many('medical.appointment', 'doctor_id', string='Doctor Appointments')
    doctor_case_ids = fields.One2many('medical.case', 'doctor_id', string='Doctor Cases')

    doctor_note = fields.Text(string='Doctor Notes')
    doctor_product_ids = fields.Many2many(
        'product.product', 
        'doctor_product_rel',
        'doctor_id',
        'product_id',
        string='Doctor Products',
        domain=[('type', '=', 'service')],  # Limiting to service type products
        help="Products/Services associated with this doctor"
    )
    doctor_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('suspended', 'Suspended'),
        ('retired', 'Retired')
    ], string='Doctor Status', default='active', tracking=True)
    # Comparision fields 
    doctor = fields.Boolean('Is a Doctor', help="Check this box if this contact is a doctor.")
    book_appointments = fields.Boolean('Book Appointments?')
    active_doctor = fields.Boolean('Active')
    waiting_approval = fields.Boolean('Waiting')
    speciality_id = fields.Many2one('doctor.speciality', string="Speciality") 
    # speciality = fields.Many2one('medical.speciality', string='Speciality', required=True)
    doctor_external_id = fields.Char('Doctor External ID')
    campus_ids = fields.Many2many('hospital.hospital','res_partner_campus_rel','partner_id','campus_id',string="Campus")
    lead_id = fields.Many2one('crm.lead','Lead')
    track_uid = fields.Char("Track UID", store=True)
    illness_treated = fields.Many2many(
    'primary.tag', 
    'res_partner_primary_rel',  
    'partner_id',  
    'primary_id',  
    string="Illness Treated"
)
    gender_aff = fields.Selection([('yes','Yes'),('no','No')], string="Gender Affirmation", store=True)
    cns_preference = fields.Many2many(
    'cns.preference',
    'res_partner_cns_rel',  
    'partner_id',  
    'cns_id',     
    string="CNS"
)
    # age_preference = fields.Many2many('age.preference','doctor_age_rel', string="Age Preference")
    age_preference = fields.Many2many(
        'age.preference',
        'doctor_age_rel',
        'res_partner_id',  # Use the existing column name
        '_unknown_id',  # Use the existing column name
        string='Age Preferences'
    )

    def action_view_cases(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_case').read()[0]
        action['domain'] = [('doctor_id', '=', self.id)]
        return action
    
    def action_view_appointments(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_appointment').read()[0]
        action['domain'] = [('doctor_id', '=', self.id)]
        return action
    
    def action_view_prescriptions(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_prescription').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        return action
    
    def action_view_payments(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_payment').read()[0]
        action['domain'] = [('patient_id', '=', self.id)]
        return action   
    
    def action_view_schedules(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_doctor_schedule').read()[0]
        action['domain'] = [('doctor_id', '=', self.id)]
        return action
    
    def action_set_active(self):
        self.write({'doctor_status': 'active'})

    def action_set_inactive(self):
        self.write({'doctor_status': 'inactive'})

    def action_set_on_leave(self):
        self.write({'doctor_status': 'on_leave'})

    def action_set_suspended(self):
        self.write({'doctor_status': 'suspended'})

    def action_set_retired(self):
        self.write({'doctor_status': 'retired'})