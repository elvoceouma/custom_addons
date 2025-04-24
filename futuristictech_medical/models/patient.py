from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalPatient(models.Model):
    _name = 'medical.patient'
    _description = 'Patient Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one(
        'res.partner', string='Related Partner', required=True,
        tracking=True, ondelete='restrict')
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
    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender')
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    emergency_contact = fields.Many2one(
        'res.partner', string='Emergency Contact',
        domain=[('is_emergency_contact', '=', True)],  ondelete='set null')
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
    lead_id = fields.Many2one('crm.lead', string='Lead')
    nationality = fields.Many2one(
        'res.country', string='Nationality', tracking=True)
    religion = fields.Many2one(
        'religion.master', string='Religion', tracking=True)
    marital_status = fields.Selection([
        ('single', 'Single'), ('married', 'Married'),
        ('divorced', 'Divorced'), ('widowed', 'Widowed')],
        string='Marital Status', tracking=True)
    
    has_allergies = fields.Boolean(string='Has Allergies', default=False)
    has_children = fields.Boolean(string='Has Children', default=False)
    number_of_children = fields.Integer(
        string='Number of Children', default=0)
    languages_known = fields.Many2many(
        'language.master', 'patient_language_rel',
        'patient_id', 'language_id', string='Languages Known')
    education_qualification = fields.Many2one(
        'education.master', string='Education Qualification', tracking=True)
    occupation = fields.Char(string='Occupation', tracking=True)
    concerns_problems = fields.Text(
        string='Concerns/Problems', tracking=True)
    do_not_call = fields.Boolean(
        string='Do Not Call', default=False, tracking=True)
    whatsapp_updates = fields.Boolean(
        string='WhatsApp Updates', default=False, tracking=True)
    aadhar_verification = fields.Boolean(
        string='Aadhar Verification', default=False, tracking=True)
    aadhar_number = fields.Integer(
        string='Aadhar Number', tracking=True)
    previous_treatment_history = fields.Text(
        string='Previous Treatment History', tracking=True)

    consulted_psychiatrist = fields.Boolean(
        string='Consulted Psychiatrist', default=False)
    consulted_counsellor = fields.Boolean(
        string='Consulted Counsellor', default=False)
    treated_at_hospitals = fields.Many2many(
        'medical.hospital', 'patient_hospital_rel',
        'patient_id', 'hospital_id', string='Treated at Hospitals')
    managed_at_home = fields.Boolean(
        string='Managed at Home', default=False)
    managed_at_home_details = fields.Text(
        string='Managed at Home Details', tracking=True)
    treated_in_rehab = fields.Boolean(
        string='Treated in Rehab', default=False)
    referral = fields.Many2one(
        'res.partner', string='Referral',
     )
    total_consultations = fields.Integer(string='Total Consultations', default=0)
    consultations_missed = fields.Integer(string='Consultations Missed', default=0)
    consultations_rescheduled = fields.Integer(string='Consultations Rescheduled', default=0)
    consultations_cancelled = fields.Integer(string='Consultations Cancelled', default=0)
    consultation_ids = fields.One2many(
        'medical.consultation', 'patient_id', string='Consultations')
    clinical_trail_ids = fields.One2many(
        'medical.clinical.trail', 'patient_id', string='Clinical Trails')
    
    _sql_constraints = [
        ('registration_number_unique',
         'UNIQUE(registration_number)',
         'Patient registration number must be unique!'),
    ]


    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                birth_date = fields.Date.from_string(record.date_of_birth)
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                record.age = age
            else:
                record.age = 0
    @api.model
    def create(self, vals):
        patient = super(MedicalPatient, self).create(vals)
        if patient.partner_id:
            patient.partner_id.write({'is_patient': True})  # Fixed field reference
        return patient

    def write(self, vals):
        res = super(MedicalPatient, self).write(vals)
        if 'partner_id' in vals:
            self.partner_id.write({'is_patient': True})  # Fixed field reference
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
     
class MedicalConsultation(models.Model):
    _name = 'medical.consultation'
    _description = 'Medical Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Consultation Reference')
    notes = fields.Text(string='Notes')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    consultation_type = fields.Selection([
        ('in_person', 'In Person'),
        ('telephonic', 'Telephonic'),
        ('video', 'Video')], string='Consultation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')], string='Status', default='draft')
    feedback_score = fields.Selection([
        ('1', '1 - Very Poor'),
        ('2', '2 - Poor'),
        ('3', '3 - Average'),
        ('4', '4 - Good'),
        ('5', '5 - Excellent')], string='Feedback Score')
    subject = fields.Char(string='Subject')
    speciality = fields.Many2one('medical.speciality', string='Speciality', required=True)
    is_free_screening = fields.Boolean(string='Free Screening', default=False)
    consultation_date = fields.Datetime(string='Consultation Date', default=fields.Datetime.now)
    duration = fields.Float(string='Duration (in minutes)')
    doctor_id = fields.Many2one('medical.doctor', string='Doctor', required=True)
    prescription_ids = fields.One2many('medical.prescription', 'consultation_id', string='Prescriptions')
    patient_id = fields.Many2one('medical.patient', string='Patient', required=True)
    campus_id = fields.Many2one('campus.master', string='Campus')
    appointment_id = fields.Many2one('medical.appointment', string='Appointment')