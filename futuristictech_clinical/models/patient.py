# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    image = fields.Binary(string='Image')
    reference = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    mrn_no = fields.Char(string='MRN', readonly=True)
    
    # Basic information
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    dob = fields.Date(string='Date of Birth')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated')
    ], string='Marital Status', tracking=True)
    
    # Medical Information
    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string='Blood Group', tracking=True)
    
    # Contact Information
    mobile = fields.Char(string='Mobile', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    fax = fields.Char(string='Fax')
    
    # Address Fields
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    state_id = fields.Char(string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Char(string='Country')
    website = fields.Char(string='Website')
    
    # Referral Information
    referred_by = fields.Many2one('res.partner', string='Referred by')
    
    # Occupation Information
    occupation_id = fields.Many2one('hospital.patient.occupation', string='Occupation')
    
    # User and Company
    user_id = fields.Many2one('res.users', string='User')
    company_id = fields.Many2one('res.company', string='Company')
    
    # Medical conditions
    illness_tag_ids = fields.Many2many('hospital.illness.tag', string='Illness Tags')
    
    # Related Records
    family_member_ids = fields.One2many('hospital.family.member', 'patient_id', string='Family Members')
    registration_ids = fields.One2many('hospital.registration.form', 'patient_id', string='Registration Forms')
    prescription_ids = fields.One2many('hospital.prescription.line', 'patient_id', string='Prescriptions')
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string='Appointments')
    admission_ids = fields.One2many('hospital.admission', 'patient_id', string='Admissions')
    document_ids = fields.One2many('hospital.patient.document', 'patient_id', string='Documents')
    vaccine_ids = fields.One2many('hospital.patient.vaccine', 'patient_id', string='Vaccines')
    op_visit_ids = fields.One2many('op.visits', 'patient_id', string='OP Visits')
    evaluation_ids = fields.One2many('hospital.evaluation', 'patient_id', string='Evaluations')
    lab_test_ids = fields.One2many('hospital.lab.test', 'patient_id', string='Lab Tests')
    crm_document_ids = fields.One2many('crm.document', 'patient_id', string='CRM Documents')
    
    # Insurance Information
    insurance_id = fields.Many2one('hospital.insurance', string='Insurance')
    medicine_register_ids = fields.One2many('medicine.register', 'patient_id', string='Medicine Registers')
    date_of_birth = fields.Date(string='Date of Birth')


    patient_id = fields.Char(string='Patient ID', readonly=True, copy=False, default=lambda self: _('New'))
   
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
            if not vals.get('mrn_no'):
                vals['mrn_no'] = self.env['ir.sequence'].next_by_code('hospital.patient.mrn_no') or 'MRN00000'
        return super(Patient, self).create(vals_list)

    def action_view_case_history(self):
        return {
            'name': _('Case History'),
            'view_mode': 'form',
            'res_model': 'case.history',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_patient_id': self.id}
        }
    
    def  action_view_registrations(self):
        return {
            'name': _('Registrations'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.registration.form',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def  action_view_appointments(self):
        return {
            'name': _('Appointments'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.appointment',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_view_prescriptions(self):
        return {
            'name': _('Descriptions'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.description',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_view_admissions(self):
        return {
            'name': _('Admissions'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.admission',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_view_vaccines(self):
        return {
            'name': _('Vaccines'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.patient.vaccine',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_view_op_visits(self):
        return {
            'name': _('OP Visits'),
            'view_mode': 'tree,form',
            'res_model': 'op.visits',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id}
        }
    
    def action_hospital_patient(self):
        return {
            'name': _('Patients'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.patient',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', self.id)],
        }
    
    def action_print_registration_form(self):
        """Print patient registration form"""
        return self.env.ref('futuristictech_clinical.action_report_hospital_patient').report_action(self)


class FamilyMember(models.Model):
    _name = 'hospital.family.member'
    _description = 'Family Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex', tracking=True)
    relation = fields.Selection([
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('other', 'Other')
    ], string='Relation', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    notes = fields.Text(string='Notes')


class PatientDocument(models.Model):
    _name = 'hospital.patient.document'
    _description = 'Patient Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    document_type_id = fields.Many2one('hospital.document.type', string='Document Type')
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Name')
    note = fields.Text(string='Notes')
    date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    
    def save(self):
        # Save the document and return to the list view
        self.ensure_one()
        if not self.file:
            raise ValidationError(_('Please upload a file.'))
        if not self.file_name:
            raise ValidationError(_('Please provide a file name.'))
        self.write({'file_name': self.file_name})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class LabTest(models.Model):
    _name = 'hospital.lab.test'
    _description = 'Lab Test'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Lab Test #', required=True, readonly=True, default=lambda self: 'New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    test_type_id = fields.Many2one('hospital.lab.test.type', string='Test Type', tracking=True)
    pathologist_id = fields.Many2one('res.partner', string='Pathologist')
    test_type = fields.Selection([
        ('blood', 'Blood Test'),
        ('urine', 'Urine Test'),
        ('stool', 'Stool Test'),
        ('xray', 'X-Ray'),
        ('ct_scan', 'CT Scan'),
        ('mri', 'MRI'),
        ('ultrasound', 'Ultrasound'),
        ('other', 'Other')
    ], string='Test Type', default='other')
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    pysician_id = fields.Many2one('hospital.physician', string='Physician', tracking=True)
    # requisition_id = fields.Many2one('hospital.lab.requisition', string='Requisition ID')
    doctor_id = fields.Many2one('hospital.physician', string='Doctor who requested the test', tracking=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.context_today, tracking=True)
    request_date = fields.Date(string='Date requested', default=fields.Date.context_today, tracking=True)
    analysis_date = fields.Date(string='Date of the Analysis', tracking=True)
    urgency = fields.Selection([
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'Stat')
    ], string='Urgency', default='routine') 
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('inprogress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', tracking=True)
    sample_type = fields.Selection([
        ('blood', 'Blood Sample'),
        ('urine', 'Urine Sample'),
        ('stool', 'Stool Sample'),
        ('other', 'Other')
    ], string='Sample Type', default='other')
    sample_collection_date = fields.Datetime(string='Sample Collection Date', default=fields.Datetime.now)
    sample_collection_time = fields.Datetime(string='Sample Collection Time', default=fields.Datetime.now)
    sample_collection_location = fields.Char(string='Sample Collection Location')
    sample_collection_notes = fields.Text(string='Sample Collection Notes')
    sample_received_date = fields.Datetime(string='Sample Received Date', default=fields.Datetime.now)
    sample_received_time = fields.Datetime(string='Sample Received Time', default=fields.Datetime.now)
    sample_received_location = fields.Char(string='Sample Received Location')
    sample_received_notes = fields.Text(string='Sample Received Notes')
    collected_by = fields.Many2one('res.users', string='Collected By', default=lambda self: self.env.user)
    results = fields.Text(string='Results')
    normal_range = fields.Text(string='Normal Range')
    conclusion = fields.Text(string='Conclusion')
    notes = fields.Text(string='Notes')
    interpretation = fields.Text(string='Interpretation')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.lab.test') or 'New'
        return super(LabTest, self).create(vals)

class CRMDocument(models.Model):
    _name = 'crm.document'
    _description = 'CRM Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Document Name', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    upload_date = fields.Date(string='Uploaded On', default=fields.Date.context_today, tracking=True)
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Name')
    document_category = fields.Selection([
        ('consent', 'Consent Forms'),
        ('id', 'ID Proofs'),
        ('insurance', 'Insurance Documents'),
        ('medical', 'Medical Reports'),
        ('other', 'Other')
    ], string='Document Category', default='other', tracking=True)
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True, tracking=True)
    
    user_id = fields.Many2one('res.users', string='Uploaded By', default=lambda self: self.env.user, tracking=True)


class IllnessTag(models.Model):
    _name = 'hospital.illness.tag'
    _description = 'Illness Tag'
    
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')


class PatientOccupation(models.Model):
    _name = 'hospital.patient.occupation'
    _description = 'Patient Occupation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)


class Insurance(models.Model):
    _name = 'hospital.insurance'
    _description = 'Patient Insurance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Insurance Plan', required=True, tracking=True)
    provider = fields.Char(string='Provider', tracking=True)
    policy_number = fields.Char(string='Policy Number', tracking=True)
    member_id = fields.Char(string='Member ID', tracking=True)
    group_number = fields.Char(string='Group Number', tracking=True)
    
    coverage_start_date = fields.Date(string='Coverage Start Date')
    coverage_end_date = fields.Date(string='Coverage End Date')
    
    # Contact details
    contact_name = fields.Char(string='Contact Name')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    
    coverage_details = fields.Text(string='Coverage Details')
    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True, tracking=True)
    
    patient_ids = fields.One2many('hospital.patient', 'insurance_id', string='Patients')




class IllnessTag(models.Model):
    _name = 'hospital.illness.tag'
    _description = 'Illness Tag'
    
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')


class DocumentType(models.Model):
    _name = 'hospital.document.type'
    _description = 'Document Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The document type name must be unique!')
    ]


class HospitalPatientEthnicGroup(models.Model):
    _name = 'oeh.medical.ethnicity'
    _description = 'Hospital Patient'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'          

    name = fields.Char(string='Name', required=True, tracking=True)
    
class HospitalPatientGeneticRisk(models.Model):
    _name = 'oeh.medical.genetics'
    _description = 'Hospital Patient Genetic Risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    long_name = fields.Char(string='Complete Name', tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    
    # Fields from form view that weren't in the original model
    chromosome = fields.Char(string='Chromosome', tracking=True)
    dominance = fields.Selection([
        ('dominant', 'Dominant'),
        ('recessive', 'Recessive')
    ], string='Dominance', tracking=True)
    gene_id = fields.Char(string='Gene ID', tracking=True)
    location = fields.Char(string='Location', tracking=True)
    info = fields.Html(string='Additional Information')
    
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')


class HospitalPatientRecreationalDrug(models.Model):
    _name = 'hospital.patient.recreational.drug'
    _description = 'Hospital Patient Recreational Drug'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Drug Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')
    
    # Fields from the form view
    street_name = fields.Char(string='Street Name', tracking=True)
    
    # General section fields
    toxicity = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('extreme', 'Extreme')
    ], string='Toxicity', tracking=True)
    
    legal_status = fields.Selection([
        ('legal', 'Legal'),
        ('illegal', 'Illegal'),
        ('restricted', 'Restricted')
    ], string='Legal Status', tracking=True)
    
    addiction_level = fields.Selection([
        ('none', 'None'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('extreme', 'Extreme')
    ], string='Addiction Level', tracking=True)
    
    category = fields.Selection([
        ('opioid', 'Opioid'),
        ('stimulant', 'Stimulant'),
        ('depressant', 'Depressant'),
        ('hallucinogen', 'Hallucinogen'),
        ('cannabis', 'Cannabis'),
        ('inhalant', 'Inhalant'),
        ('other', 'Other')
    ], string='Category', tracking=True)
    
    # DEA Schedule Level fields
    dea_schedule_i = fields.Boolean(string='Schedule I', tracking=True)
    dea_schedule_ii = fields.Boolean(string='Schedule II', tracking=True)
    dea_schedule_iii = fields.Boolean(string='Schedule III', tracking=True)
    dea_schedule_iv = fields.Boolean(string='Schedule IV', tracking=True)
    dea_schedule_v = fields.Boolean(string='Schedule V', tracking=True)
    
    # Henningfield Rating fields
    withdrawal_level = fields.Integer(string='Withdrawal', tracking=True, help='Level between 1 and 6 (1=highest and 6=lowest)')
    tolerance_level = fields.Integer(string='Tolerance', tracking=True, help='Level between 1 and 6 (1=highest and 6=lowest)')
    intoxication_level = fields.Integer(string='Intoxication', tracking=True, help='Level between 1 and 6 (1=highest and 6=lowest)')
    reinforcement_level = fields.Integer(string='Reinforcement', tracking=True, help='Level between 1 and 6 (1=highest and 6=lowest)')
    dependence_level = fields.Integer(string='Dependence', tracking=True, help='Level between 1 and 6 (1=highest and 6=lowest)')
    
    # Administration Routes fields
    route_oral = fields.Boolean(string='Oral', tracking=True)
    route_popping = fields.Boolean(string='Popping', tracking=True)
    route_injection = fields.Boolean(string='Injection', tracking=True)
    route_inhaling = fields.Boolean(string='Inhaling', tracking=True)
    route_sniffing = fields.Boolean(string='Sniffing', tracking=True)
    
    # Additional Info
    info = fields.Html(string='Additional Information and Effects')
    
    @api.constrains('withdrawal_level', 'tolerance_level', 'intoxication_level', 'reinforcement_level', 'dependence_level')
    def _check_henningfield_rating(self):
        """Validate that Henningfield ratings are between 1 and 6"""
        for record in self:
            fields_to_check = [
                'withdrawal_level', 'tolerance_level', 'intoxication_level',
                'reinforcement_level', 'dependence_level'
            ]
            
            for field in fields_to_check:
                value = getattr(record, field, False)
                if value and (value < 1 or value > 6):
                    raise models.ValidationError(f"{field.replace('_', ' ').title()} must be between 1 and 6")

class HospitalAwsFileType(models.Model):
    _name = 'hospital.aws.file.type'
    _description = 'Hospital AWS File Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'          

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')