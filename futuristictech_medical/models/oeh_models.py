from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

# ======================================================
# Models referenced in consultation.py but not in codebase
# ======================================================

class OehMedicalInpatient(models.Model):
    _name = 'oeh.medical.inpatient'
    _description = 'Inpatient Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='IP Number', required=True, readonly=True, default=lambda self: _('New'))
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, tracking=True)
    admission_date = fields.Datetime(string='Admission Date', default=fields.Datetime.now, required=True)
    discharge_date = fields.Datetime(string='Discharge Date')
    attending_physician = fields.Many2one('hr.employee', string='Attending Physician', domain=[('team_role', '=', 'psychiatrist')])
    bed = fields.Many2one('oeh.medical.health.center.beds', string='Bed', required=True)
    counsellor = fields.Many2one('hr.employee', string='Counsellor', domain=[('team_role', '=', 'counsellor')])
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Admitted', 'Admitted'),
        ('Discharged', 'Discharged'),
        ('Cancelled', 'Cancelled')
    ], string='Status', default='Draft', tracking=True)
    consultation_ids = fields.One2many('consultation.consultation', 'inpatient_admission_id', string='Consultations')
    vital_assessment_ids = fields.One2many('vital.physical.assessment', 'name', string='Vital Assessments')

    def  action_view_consultations(self):
        return {
            'name': 'Consultations',
            'view_mode': 'tree,form',
            'res_model': 'consultation.consultation',
            'type': 'ir.actions.act_window',
            'domain': [('inpatient_admission_id', '=', self.id)],
        }
    
    def action_view_vitals(self):
        return {
            'name': 'Vital Assessments',
            'view_mode': 'tree,form',
            'res_model': 'vital.physical.assessment',
            'type': 'ir.actions.act_window',
            'domain': [('name', '=', self.id)],
        }
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.inpatient') or _('New')
        return super(OehMedicalInpatient, self).create(vals)
    
    def action_admit(self):
        self.state = 'Admitted'
        
    def action_discharge(self):
        self.state = 'Discharged'
        self.discharge_date = fields.Datetime.now()
        
    def action_cancel(self):
        self.state = 'Cancelled'


class OehMedicalPatient(models.Model):
    _name = 'oeh.medical.patient'
    _description = 'Patient Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    identification_code = fields.Char(string='Patient ID', required=True, readonly=True, default=lambda self: _('New'))
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True)
    date_of_birth = fields.Date(string='Date of Birth')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    blood_group = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], string='Blood Group')
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    referred_by = fields.Many2one('res.partner', string='Referred By', domain=[('doctor', '=', True)])
    consultation_ids = fields.One2many('consultation.consultation', 'patient_id', string='Consultations')
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('identification_code', _('New')) == _('New'):
            vals['identification_code'] = self.env['ir.sequence'].next_by_code('oeh.medical.patient') or _('New')
        return super(OehMedicalPatient, self).create(vals)
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                born = fields.Date.from_string(record.date_of_birth)
                record.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                record.age = 0


class OPVisits(models.Model):
    _name = 'op.visits'
    _description = 'Outpatient Visits'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='OP Reference', required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now, required=True)
    purpose = fields.Text(string='Purpose of Visit')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], string='Status', default='Draft', tracking=True)
    consultation_ids = fields.One2many('consultation.consultation', 'op_visit_id', string='Consultations')
    vital_assessment_ids = fields.One2many('vital.physical.assessment', 'op_visit_id', string='Vital Assessments')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('op.visits') or _('New')
        return super(OPVisits, self).create(vals)
    
    def action_start(self):
        self.state = 'In Progress'
        
    def action_complete(self):
        self.state = 'Completed'
        
    def action_cancel(self):
        self.state = 'Cancelled'


class VitalPhysicalAssessment(models.Model):
    _name = 'vital.physical.assessment'
    _description = 'Vital and Physical Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Many2one('oeh.medical.inpatient', string='Inpatient')
    op_visit_id = fields.Many2one('op.visits', string='OP Visit')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    bp = fields.Integer(string='BP in (mmHg)')
    bp2 = fields.Integer(string='BP2')
    weight = fields.Float(string='Weight (kg)')
    height = fields.Float(string='Height (cm)')
    bmi = fields.Float(string='BMI', compute='_compute_bmi', store=True)
    temperature = fields.Float(string='Temperature (°C)')
    pulse_rate = fields.Integer(string='Pulse Rate (bpm)')
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    spo_2 = fields.Integer(string='SPO2 (%)')
    grbs = fields.Integer(string='GRBS (mg/dl)')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], string='Status', default='Draft', tracking=True)
    user_id = fields.Many2one('res.users', string='Checked By', default=lambda self: self.env.user)
    
    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.weight and record.height:
                height_in_meters = record.height / 100
                record.bmi = record.weight / (height_in_meters * height_in_meters)
            else:
                record.bmi = 0
    
    def action_complete(self):
        self.state = 'Completed'
        
    def action_cancel(self):
        self.state = 'Cancelled'


class CPPurpose(models.Model):
    _name = 'cp.purpose'
    _description = 'Counsellor and Clinical Psychologist Purpose'
    
    name = fields.Char(string='Purpose', required=True)
    description = fields.Text(string='Description')
    type = fields.Selection([
        ('counsellor', 'Counsellor'),
        ('clinical_psychologist', 'Clinical Psychologist'),
        ('both', 'Both')
    ], string='Applicable To', default='both')
    active = fields.Boolean(string='Active', default=True)


class MedicalSpeciality(models.Model):
    _name = 'medical.speciality'
    _description = 'Medical Speciality'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Speciality Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         'Speciality code must be unique!')
    ]


class FollowupType(models.Model):
    _name = 'followup.type'
    _description = 'Follow-up Type'
    
    name = fields.Char(string='Name', required=True)
    product_id = fields.Many2one('product.product', string='Related Service', domain=[('type', '=', 'service')])
    team_role = fields.Selection([
        ('psychiatrist', 'Psychiatrist'),
        ('clinical_psychologist', 'Clinical Psychologist'),
        ('counsellor', 'Counsellor'),
        ('any', 'Any Role')
    ], string='Team Role', default='any')
    type = fields.Selection([
        ('ip', 'IP'),
        ('op', 'OP'),
        ('both', 'Both')
    ], string='Applicable To', default='both')
    billable = fields.Boolean(string='Billable', default=True)
    payout = fields.Boolean(string='Generate Payout', default=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class OehMedicalPrescription(models.Model):
    _name = 'oeh.medical.prescription'
    _description = 'Medical Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Prescription Number', readonly=True, default=lambda self: _('New'))
    patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True, tracking=True)
    patient_id = fields.Char(related='patient.identification_code', string='Patient ID', store=True)
    prescription_date = fields.Datetime(string='Prescription Date', default=fields.Datetime.now)
    doctor = fields.Many2one('res.partner', string='Doctor', domain=[('doctor', '=', True)], required=True)
    prescription_line = fields.One2many('oeh.medical.prescription.line', 'prescription_id', string='Prescription Lines')
    notes = fields.Text(string='Prescription Notes')
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Confirm', 'Confirmed'),
        ('Cancelled', 'Cancelled')
    ], string='Status', default='Draft', tracking=True)
    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='Inpatient')
    op_visit_id = fields.Many2one('op.visits', string='OP Visit')
    prescription_type = fields.Selection([
        ('ip', 'IP'),
        ('op', 'OP')
    ], string='Type', required=True, default='op')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(string='Active', default=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.prescription') or _('New')
        return super(OehMedicalPrescription, self).create(vals)
    
    def action_prescription_confirm(self):
        self.state = 'Confirm'
    
    def action_prescription_cancel(self):
        self.state = 'Cancelled'


class OehMedicalPrescriptionLine(models.Model):
    _name = 'oeh.medical.prescription.line'
    _description = 'Prescription Line'
    
    prescription_id = fields.Many2one('oeh.medical.prescription', string='Prescription', ondelete='cascade')
    doctor = fields.Many2one('res.partner', string='Doctor', required=True)
    speciality = fields.Many2one('medical.speciality', string='Speciality')
    name = fields.Many2one('product.product', string='Medicine', required=True, domain=[('type', '=', 'product')])
    prescription_type = fields.Selection([
        ('SOS', 'SOS'),
        ('Definite', 'Definite'),
        ('Repetitive', 'Repetitive')
    ], string='Type', required=True)
    start_treatment = fields.Datetime(string='Start Date')
    end_treatment = fields.Datetime(string='End Date')
    mrgn = fields.Float(string='Morning')
    noon = fields.Float(string='Noon')
    evng = fields.Float(string='Evening')
    night = fields.Float(string='Night')
    dose_form = fields.Many2one('product.form', string='Form')
    product_uom = fields.Many2one('uom.uom', string='UOM')
    indication = fields.Many2one('oeh.medical.pathology', string='Indication')
    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency')
    take = fields.Selection([
        ('After Food', 'After Food'),
        ('Before Food', 'Before Food')
    ], string='Take')


class ProductForm(models.Model):
    _name = 'product.form'
    _description = 'Product Dosage Form'
    
    name = fields.Char(string='Form', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class OehMedicalDosage(models.Model):
    _name = 'oeh.medical.dosage'
    _description = 'Medical Dosage'
    
    name = fields.Char(string='Frequency', required=True)
    abbreviation = fields.Char(string='Abbreviation')
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)


class OehMedicalPathology(models.Model):
    _name = 'oeh.medical.pathology'
    _description = 'Diseases and Medical Conditions'
    
    name = fields.Char(string='Disease Name', required=True)
    code = fields.Char(string='Code', required=True)
    category = fields.Many2one('oeh.medical.pathology.category', string='Category')
    chronic = fields.Boolean(string='Chronic Disease')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         'The disease code must be unique!')
    ]


class OehMedicalPathologyCategory(models.Model):
    _name = 'oeh.medical.pathology.category'
    _description = 'Disease Categories'
    
    name = fields.Char(string='Category Name', required=True)
    parent_id = fields.Many2one('oeh.medical.pathology.category', string='Parent Category')
    active = fields.Boolean(string='Active', default=True)


class OutsideConsultation(models.Model):
    _name = 'outside.consultation'
    _description = 'Outside Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', tracking=True)
    speciality_id = fields.Many2one('medical.speciality', string='Speciality', required=True, tracking=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', domain=[('doctor', '=', True)], tracking=True)
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='Inpatient')
    op_visit_id = fields.Many2one('op.visits', string='OP Visit')
    type = fields.Selection([
        ('ip', 'IP'),
        ('op', 'OP')
    ], string='Type', required=True, default='op')
    psychiatrist_id = fields.Many2one('hr.employee', string='Referring Doctor', domain=[('team_role', '=', 'psychiatrist')])
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency')
    ], string='Priority', default='low', tracking=True)
    note = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('outside.consultation') or _('New')
        return super(OutsideConsultation, self).create(vals)
    
    def action_request(self):
        self.state = 'requested'
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class LabTestRequisition(models.Model):
    _name = 'labtest.requisition'
    _description = 'Lab Test Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', related='patient_id.name', store=True)
    type = fields.Selection([
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient')
    ], string='Patient Type', required=True, default='outpatient')
    op_visit_id = fields.Many2one('op.visits', string='OP Visit')
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    doctor_id = fields.Many2one('res.partner', string='Referring Doctor', domain=[('doctor', '=', True)])
    purpose = fields.Text(string='Purpose')
    requested_date = fields.Date(string='Requested Date', default=fields.Date.context_today, required=True)
    requisition_line_ids = fields.One2many('labtest.requisition.line', 'requisition_id', string='Requisition Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('tested', 'Tested'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('labtest.requisition') or _('New')
        return super(LabTestRequisition, self).create(vals)
    
    def action_confirm(self):
        self.state = 'confirmed'
    
    def action_tested(self):
        self.state = 'tested'
    
    def action_cancel(self):
        self.state = 'cancelled'


class LabTestRequisitionLine(models.Model):
    _name = 'labtest.requisition.line'
    _description = 'Lab Test Requisition Line'
    
    requisition_id = fields.Many2one('labtest.requisition', string='Requisition', ondelete='cascade')
    labtest_type_id = fields.Many2one('medical.labtest.types', string='Test Type', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    result = fields.Text(string='Result')
    normal_range = fields.Char(string='Normal Range')
    unit = fields.Char(string='Unit')


class OehMedicalLabtestTypes(models.Model):
    _name = 'oeh.medical.labtest.types'
    _description = 'Lab Test Types'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Test Name', required=True, tracking=True)
    code = fields.Char(string='Test Code', required=True, tracking=True)
    test_charge = fields.Float(string='Test Charge')
    product_id = fields.Many2one('product.product', string='Related Product')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         'Test code must be unique!')
    ]


class PatientDocument(models.Model):
    _name = 'patient.document'
    _description = 'Patient Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Document Name', required=True)
    oeh_medical_patient = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    document_type = fields.Selection([
        ('lab_report', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('discharge_summary', 'Discharge Summary'),
        ('other', 'Other')
    ], string='Document Type', required=True)
    document_file = fields.Binary(string='Document', attachment=True, required=True)
    document_filename = fields.Char(string='Filename')
    notes = fields.Text(string='Notes')
    upload_date = fields.Date(string='Upload Date', default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='Uploaded By', default=lambda self: self.env.user)


class PsychiatristEvaluationForm(models.Model):
    _name = 'psychiatrist.evaluation.form'
    _description = 'Psychiatrist Evaluation Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True, tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    psychiatrist_id = fields.Many2one('hr.employee', string='Psychiatrist', domain=[('team_role', '=', 'psychiatrist')], required=True)
    chief_complaint = fields.Text(string='Chief Complaint', required=True)
    history_present_illness = fields.Text(string='History of Present Illness')
    past_psychiatric_history = fields.Text(string='Past Psychiatric History')
    medical_history = fields.Text(string='Medical History')
    family_history = fields.Text(string='Family History')
    personal_history = fields.Text(string='Personal History')
    substance_use = fields.Text(string='Substance Use History')
    mental_status_examination = fields.Text(string='Mental Status Examination')
    diagnosis = fields.Text(string='Diagnosis')
    treatment_plan = fields.Text(string='Treatment Plan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('psychiatrist.evaluation.form') or _('New')
        return super(PsychiatristEvaluationForm, self).create(vals)
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class IllnessTag(models.Model):
    _name = 'illness.tag'
    _description = 'Illness Tags'
    
    name = fields.Char(string='Illness', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)


class ICDCoding(models.Model):
    _name = 'icd.coding'
    _description = 'ICD-10 Coding'
    
    name = fields.Char(string='Description', required=True)
    code = fields.Char(string='Code', required=True)
    category_id = fields.Many2one('icd.category', string='Category')
    active = fields.Boolean(string='Active', default=True)
    
    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         'ICD code must be unique!')
    ]


class ICDCategory(models.Model):
    _name = 'icd.category'
    _description = 'ICD Category'
    
    name = fields.Char(string='Category', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)


class AdmissionReferralConfig(models.Model):
    _name = 'admission.referral.config'
    _description = 'Admission Referral Configuration'
    
    name = fields.Char(string='Package Name', required=True)
    referral_items_ids = fields.One2many('admission.referral.items', 'referral_config_id', string='Referral Items')
    scale_ids = fields.One2many('admission.referral.scales', 'referral_config_id', string='Scales')
    active = fields.Boolean(string='Active', default=True)


class AdmissionReferralItems(models.Model):
    _name = 'admission.referral.items'
    _description = 'Admission Referral Items'
    
    referral_config_id = fields.Many2one('admission.referral.config', string='Referral Config')
    product_id = fields.Many2one('product.product', string='Product/Service', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')


class AdmissionReferralScales(models.Model):
    _name = 'admission.referral.scales'
    _description = 'Admission Referral Scales'
    
    referral_config_id = fields.Many2one('admission.referral.config', string='Referral Config')
    scale_type = fields.Selection([
        ('assist_who', 'ASSIST - WHO'),
        ('basis_32', 'BASIS - 32'),
        ('dtcq_8_alcohol', 'DTCQ 8 - ALCOHOL'),
        ('dtcq_8_drugs', 'DTCQ 8 - DRUGS'),
        ('socrates', 'SOCRATES'),
        ('pss', 'PSS'),
        ('treatment_entry', 'Treatment Entry'),
        ('cross_cutting_symptom_measure', 'Cross - Cutting Symptom Measure'),
        ('disability_assessment_who_proxy', 'Disability Assessment WHO Proxy'),
        ('disability_assessment_who_self', 'Disability Assessment WHO Self'),
        ('mania_adult_dsm', 'Mania Adult - DSM'),
        ('personality_inventory_brief_self', 'Personality Inventory Brief Self'),
        ('repetitive_thoughts_behaviours', 'Repetitive Thoughts and Behaviours'),
        ('depression_adult_dsm', 'Depression - Adult DSM'),
        ('psychosis_symptom_severity', 'Psychosis Symptom Severity'),
        ('casig_therapist', 'CASIG Therapist')
    ], string='Scale Type', required=True)


class OehMedicalHealthCenterWard(models.Model):
    _name = 'oeh.medical.health.center.ward'
    _description = 'Hospital Ward'
    
    name = fields.Char(string='Name', required=True)
    building = fields.Many2one('oeh.medical.health.center.building', string='Building')
    floor = fields.Integer(string='Floor Number')
    private = fields.Boolean(string='Private')
    bio_hazard = fields.Boolean(string='Bio Hazard')
    price_tag = fields.Many2one('product.pricelist', string='Price Tag')
    capacity = fields.Integer(string='Capacity')
    state = fields.Selection([
        ('available', 'Available'),
        ('full', 'Full'),
        ('inactive', 'Inactive')
    ], string='Status', default='available')
    notes = fields.Text(string='Notes')
    beds = fields.One2many('oeh.medical.health.center.beds', 'ward', string='Beds')

    def action_view_beds(self):
        return {
            'name': 'Beds',
            'view_mode': 'tree,form',
            'res_model': 'oeh.medical.health.center.beds',
            'type': 'ir.actions.act_window',
            'domain': [('ward', '=', self.id)],
        }


class OehMedicalHealthCenterBeds(models.Model):
    _name = 'oeh.medical.health.center.beds'
    _description = 'Hospital Beds'
    
    name = fields.Char(string='Bed Number', required=True)
    ward = fields.Many2one('oeh.medical.health.center.ward', string='Ward', required=True)
    building = fields.Many2one('oeh.medical.health.center.building', related='ward.building', store=True, string='Building')
    institution = fields.Many2one('oeh.medical.health.center', related='building.institution', store=True, string='Institution')
    product_id = fields.Many2one('product.product', string='Service', domain=[('type', '=', 'service')])
    bed_type = fields.Selection([
        ('gatch', 'Gatch Bed'),
        ('electric', 'Electric'),
        ('stretcher', 'Stretcher'),
        ('low', 'Low Bed'),
        ('low_air_loss', 'Low Air Loss'),
        ('air_fluidized', 'Air Fluidized'),
        ('circular', 'Circular Bed'),
        ('clinitron', 'Clinitron'),
        ('floatation', 'Floatation'),
        ('kinair', 'Kinair'),
        ('stryker_frame', 'Stryker Frame'),
        ('homecare', 'Homecare Bed'),
        ('other', 'Other')
    ], string='Bed Type', default='gatch')
    telephone_number = fields.Char(string='Telephone Number')
    state = fields.Selection([
        ('free', 'Free'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('na', 'Not Available')
    ], string='Status', default='free')
    extra_info = fields.Text(string='Extra Info')


class OehMedicalHealthCenterBuilding(models.Model):
    _name = 'oeh.medical.health.center.building'
    _description = 'Medical Buildings'
    
    name = fields.Char(string='Name', required=True)
    institution = fields.Many2one('oeh.medical.health.center', string='Health Center', required=True)
    code = fields.Char(string='Code')
    extra_info = fields.Text(string='Extra Info')
    wards = fields.One2many('oeh.medical.health.center.ward', 'building', string='Wards')

    def action_view_wards(self):
        return {
            'name': 'Wards',
            'view_mode': 'tree,form',
            'res_model': 'oeh.medical.health.center.ward',
            'type': 'ir.actions.act_window',
            'domain': [('building', '=', self.id)],
        }

class OehMedicalHealthCenter(models.Model):
    _name = 'oeh.medical.health.center'
    _description = 'Health Centers'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    institution_type = fields.Selection([
        ('doctor_office', 'Doctor Office'),
        ('primary_care', 'Primary Care Center'),
        ('clinic', 'Clinic'),
        ('hospital', 'Hospital'),
        ('nursing_home', 'Nursing Home'),
        ('other', 'Other')
    ], string='Type', default='hospital')
    extra_info = fields.Text(string='Extra Info')
    buildings = fields.One2many('oeh.medical.health.center.building', 'institution', string='Buildings')

    def action_view_buildings(self):
        return {
            'name': 'Buildings',
            'view_mode': 'tree,form',
            'res_model': 'oeh.medical.health.center.building',
            'type': 'ir.actions.act_window',
            'domain': [('institution', '=', self.id)],
        }
    
    def action_view_wards(self):
        return {
            'name': 'Wards',
            'view_mode': 'tree,form',
            'res_model': 'oeh.medical.health.center.ward',
            'type': 'ir.actions.act_window',
            'domain': [('building.institution', '=', self.id)],
        }
    



class MedicalLabtest(models.Model):
    _name = 'medical.labtest'
    _description = 'Medical Lab Test Results'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Test ID', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True, tracking=True)
    test_type_id = fields.Many2one('medical.labtest.types', string='Test Type', required=True, tracking=True)
    date_requested = fields.Datetime(string='Date Requested', default=fields.Datetime.now)
    date_analysis = fields.Datetime(string='Date of Analysis')
    pathologist = fields.Many2one('res.partner', string='Pathologist', domain=[('doctor', '=', True)])
    requesting_physician = fields.Many2one('res.partner', string='Requesting Physician', domain=[('doctor', '=', True)])
    results = fields.Text(string='Results')
    diagnosis = fields.Text(string='Diagnosis')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('tested', 'Tested'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.labtest') or _('New')
        return super(MedicalLabtest, self).create(vals)
    
    def action_test_complete(self):
        self.state = 'tested'
        self.date_analysis = fields.Datetime.now()
    
    def action_cancel(self):
        self.state = 'cancelled'


class PayoutConfig(models.Model):
    _name = 'payout.config'
    _description = 'Doctor Payout Configuration'
    
    partner_id = fields.Many2one('res.partner', string='Doctor', domain=[('doctor', '=', True)], required=True)
    product_category_id = fields.Many2one('product.category', string='Service Category', required=True)
    type = fields.Selection([
        ('base', 'Base Price'),
        ('matrix', 'Price Matrix')
    ], string='Payout Type', default='base', required=True)
    consultation_percentage = fields.Float(string='Consultation Percentage (%)')
    referral_percentage = fields.Float(string='Referral Percentage (%)')
    active = fields.Boolean(string='Active', default=True)


class DoctorPayout(models.Model):
    _name = 'doctor.payout'
    _description = 'Doctor Payout'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True, domain=[('doctor', '=', True)])
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    payout_line_ids = fields.One2many('doctor.payout.line', 'doctor_payout_id', string='Payout Lines')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='new', tracking=True)
    payment_date = fields.Date(string='Payment Date')
    notes = fields.Text(string='Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('doctor.payout') or _('New')
        return super(DoctorPayout, self).create(vals)
    
    @api.depends('payout_line_ids.price_subtotal')
    def _compute_total_amount(self):
        for payout in self:
            payout.total_amount = sum(line.price_subtotal for line in payout.payout_line_ids)
    
    def action_confirm(self):
        self.state = 'confirmed'
    
    def action_pay(self):
        self.state = 'paid'
        self.payment_date = fields.Date.today()
    
    def action_cancel(self):
        self.state = 'cancelled'


class DoctorPayoutLine(models.Model):
    _name = 'doctor.payout.line'
    _description = 'Doctor Payout Line'
    
    doctor_payout_id = fields.Many2one('doctor.payout', string='Payout', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Service', required=True)
    name = fields.Char(string='Description')
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient')
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    date = fields.Date(string='Date', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    reference = fields.Char(string='Reference')
    internal_reference = fields.Char(string='Internal Reference')
    type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')
    ], string='Type', default='credit')
    
    @api.depends('quantity', 'price_unit', 'type')
    def _compute_price_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.price_unit
            if line.type == 'debit':
                subtotal = -subtotal
            line.price_subtotal = subtotal


class DebitNote(models.Model):
    _name = 'debit.note'
    _description = 'Debit Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number', required=True)
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', related='inpatient_admission_id.patient', store=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    bed_id = fields.Many2one('oeh.medical.health.center.beds', string='Bed')
    ward_id = fields.Many2one('oeh.medical.health.center.ward', string='Ward')
    building_id = fields.Many2one('oeh.medical.health.center.building', string='Building')
    health_center_id = fields.Many2one('oeh.medical.health.center', string='Health Center')
    debit_line_ids = fields.One2many('debit.note.line', 'debit_id', string='Debit Lines')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice')
    notes = fields.Text(string='Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('debit.note') or _('New')
        return super(DebitNote, self).create(vals)
    
    @api.depends('debit_line_ids.price_subtotal')
    def _compute_total_amount(self):
        for debit in self:
            debit.total_amount = sum(line.price_subtotal for line in debit.debit_line_ids)
    
    def action_confirm(self):
        self.state = 'confirmed'
    
    def action_cancel(self):
        self.state = 'cancelled'
    
    def action_create_invoice(self):
        # Invoice creation logic
        self.state = 'invoiced'


class DebitNoteLine(models.Model):
    _name = 'debit.note.line'
    _description = 'Debit Note Line'
    
    debit_id = fields.Many2one('debit.note', string='Debit Note', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Service', required=True)
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    reference = fields.Char(string='Reference')
    date = fields.Date(string='Date', required=True)
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit


class BillEstimation(models.Model):
    _name = 'bill.estimation'
    _description = 'Bill Estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    bed_type = fields.Many2one('oeh.medical.health.center.ward', string='Bed Category')
    rate_plan = fields.Many2one('product.pricelist', string='Rate Plan')
    estimation_date = fields.Date(string='Estimation Date', default=fields.Date.context_today)
    estimation_line_ids = fields.One2many('bill.estimation.line', 'bill_estimation_id', string='Estimation Lines')
    total_estimated = fields.Float(string='Total Estimated Amount', compute='_compute_total_estimated', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('estimation_line_ids.subtotal')
    def _compute_total_estimated(self):
        for estimation in self:
            estimation.total_estimated = sum(line.subtotal for line in estimation.estimation_line_ids)
    
    def action_confirm(self):
        self.state = 'confirmed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class BillEstimationLine(models.Model):
    _name = 'bill.estimation.line'
    _description = 'Bill Estimation Line'
    
    bill_estimation_id = fields.Many2one('bill.estimation', string='Bill Estimation', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Service', required=True)
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    discount = fields.Float(string='Discount (%)')
    subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    
    @api.depends('quantity', 'unit_price', 'discount')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price * (1 - line.discount / 100)
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            pricelist = self.bill_estimation_id.rate_plan
            if pricelist:
                self.unit_price = self.product_id.with_context(pricelist=pricelist.id).price
            else:
                self.unit_price = self.product_id.list_price
            self.description = self.product_id.name


class AssistConsultations(models.Model):
    _name = 'assist.consultations'
    _description = 'ASSIST WHO Scale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    type = fields.Selection([
        ('ip', 'IP'),
        ('op', 'OP')
    ], string='Type', required=True, default='op')
    inpatient_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference')
    counsellor = fields.Many2one('hr.employee', string='Counsellor')
    datetime = fields.Datetime(string='Date & Time', default=fields.Datetime.now)
    tobacco_use = fields.Integer(string='Tobacco Use')
    alcohol_use = fields.Integer(string='Alcohol Use')
    cannabis_use = fields.Integer(string='Cannabis Use')
    cocaine_use = fields.Integer(string='Cocaine Use')
    amphetamine_use = fields.Integer(string='Amphetamine Use')
    inhalants_use = fields.Integer(string='Inhalants Use')
    sedatives_use = fields.Integer(string='Sedatives Use')
    hallucinogens_use = fields.Integer(string='Hallucinogens Use')
    opioids_use = fields.Integer(string='Opioids Use')
    other_use = fields.Integer(string='Other Substance Use')
    other_substance = fields.Char(string='Specify Other Substance')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class ClinicalPsychologistSession(models.Model):
    _name = 'clinical.psychologist.session'
    _description = 'Clinical Psychologist Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference')
    psychologist_id = fields.Many2one('hr.employee', string='Clinical Psychologist', domain=[('team_role', '=', 'clinical_psychologist')])
    session_date = fields.Datetime(string='Session Date', default=fields.Datetime.now)
    duration = fields.Float(string='Duration (hours)')
    problems_identified = fields.Text(string='Problems Identified')
    intervention = fields.Text(string='Intervention')
    outcome = fields.Text(string='Outcome')
    recommendations = fields.Text(string='Recommendations')
    next_session_plan = fields.Text(string='Next Session Plan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    type = fields.Selection([
        ('individual', 'Individual Session'),
        ('group', 'Group Session'),
        ('op', 'OP Session'),
        ('family', 'Family Session'),
        ('crisis', 'Crisis Intervention'),
        ('other', 'Other')
    ], string='Session Type', default='individual')

    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('clinical.psychologist.session') or _('New')
        return super(ClinicalPsychologistSession, self).create(vals)
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class ClinicalPsychologistScreening(models.Model):
    _name = 'clinical.psychologist.screening'
    _description = 'Clinical Psychologist Screening'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference')
    psychologist_id = fields.Many2one('hr.employee', string='Clinical Psychologist', domain=[('team_role', '=', 'clinical_psychologist')])
    screening_date = fields.Datetime(string='Screening Date', default=fields.Datetime.now)
    chief_complaint = fields.Text(string='Chief Complaint')
    history = fields.Text(string='History')
    mental_status = fields.Text(string='Mental Status')
    impression = fields.Text(string='Impression')
    recommendations = fields.Text(string='Recommendations')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    type = fields.Selection([
        ('individual', 'Individual Screening'),
        ('group', 'Group Screening'),
        ('family', 'Family Screening'),
        ('crisis', 'Crisis Screening'),
        ('other', 'Other')
    ], string='Screening Type', default='individual')
    notes = fields.Text(string='Notes')
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('clinical.psychologist.screening') or _('New')
        return super(ClinicalPsychologistScreening, self).create(vals)
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class CounsellorSession(models.Model):
    _name = 'counsellor.session'
    _description = 'Counsellor Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference')
    counsellor_id = fields.Many2one('hr.employee', string='Counsellor', domain=[('team_role', '=', 'counsellor')])
    session_date = fields.Datetime(string='Session Date', default=fields.Datetime.now)
    duration = fields.Float(string='Duration (hours)')
    session_type = fields.Selection([
        ('individual', 'Individual Counselling'),
        ('group', 'Group Counselling'),
        ('family', 'Family Counselling'),
        ('crisis', 'Crisis Intervention'),
        ('other', 'Other')
    ], string='Session Type', default='individual')
    present_concerns = fields.Text(string='Present Concerns')
    intervention = fields.Text(string='Intervention')
    progress = fields.Text(string='Progress')
    plan = fields.Text(string='Plan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    type = fields.Selection([
        ('individual', 'Individual Session'),
        ('group', 'Group Session'),
        ('family', 'Family Session'),
        ('crisis', 'Crisis Intervention'),
        ('other', 'Other')
    ], string='Session Type', default='individual')
    notes = fields.Text(string='Notes')
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('counsellor.session') or _('New')
        return super(CounsellorSession, self).create(vals)
    
    def action_complete(self):
        self.state = 'completed'
    
    def action_cancel(self):
        self.state = 'cancelled'


class CRMSimpleRegistration(models.Model):
    _name = 'crm.simple.registration'
    _description = 'CRM Simple Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True)
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference')
    registration_date = fields.Date(string='Registration Date', default=fields.Date.context_today)
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    type = fields.Selection([
        ('individual', 'Individual Registration'),
        ('group', 'Group Registration'),
        ('family', 'Family Registration'),
        ('crisis', 'Crisis Registration'),
        ('other', 'Other')
    ], string='Registration Type', default='individual')
    notes = fields.Text(string='Notes')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.simple.registration') or _('New')
        return super(CRMSimpleRegistration, self).create(vals)
    
    def action_register(self):
        self.state = 'registered'
    
    def action_cancel(self):
        self.state = 'cancelled'

class ServiceList(models.Model):
    _name = 'service.list'
    _description = 'Service List'
    _order = 'sequence, name'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    
    # Optional fields for integration with products
    product_id = fields.Many2one('product.product', string='Related Product')
    price = fields.Float(string='Price', related='product_id.list_price', readonly=True)
    
    # Optional categorization fields
    category_id = fields.Many2one('service.list.category', string='Category')
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Service name must be unique!'),
        ('code_unique', 'unique(code)', 'Service code must be unique!')
    ]


class ServiceListCategory(models.Model):
    _name = 'service.list.category'
    _description = 'Service List Category'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    
    service_ids = fields.One2many('service.list', 'category_id', string='Services')
    service_count = fields.Integer(compute='_compute_service_count', string='Service Count')
    
    @api.depends('service_ids')
    def _compute_service_count(self):
        for category in self:
            category.service_count = len(category.service_ids)
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Category name must be unique!'),
        ('code_unique', 'unique(code)', 'Category code must be unique!')
    ]


class CrmPrimaryTag(models.Model):
    _name = 'crm.primary.tag'
    _description = 'CRM Primary Tag'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    
    lead_ids = fields.Many2many('crm.lead', 'crm_lead_primary_tag_rel', 'tag_id', 'lead_id', string='Leads')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class CrmSecondaryTag(models.Model):
    _name = 'crm.secondary.tag'
    _description = 'CRM Secondary Tag'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    
    lead_ids = fields.Many2many('crm.lead', 'crm_lead_secondary_tag_rel', 'tag_id', 'lead_id', string='Leads')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class CrmTertiaryTag(models.Model):
    _name = 'crm.tertiary.tag'
    _description = 'CRM Tertiary Tag'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    
    lead_ids = fields.Many2many('crm.lead', 'crm_lead_tertiary_tag_rel', 'tag_id', 'lead_id', string='Leads')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]


class CrmDiscardTag(models.Model):
    _name = 'crm.discard.tag'
    _description = 'CRM Discard Tag'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    
    lead_ids = fields.Many2many('crm.lead', 'crm_lead_discard_tag_rel', 'tag_id', 'lead_id', string='Leads')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists!"),
    ]



class CnsMaster(models.Model):
    _name = 'cns.master'
    _description = 'CNS Master'
    _order = 'name'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    
    # You can add more fields specific to your CNS master requirements
    sequence = fields.Integer(default=10, help='Used to order CNS items')
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'CNS name must be unique!'),
        ('code_unique', 'unique(code)', 'CNS code must be unique!')
    ]


class AgePreference(models.Model):
    _name = 'age.preference'
    _description = 'Age Preference'
    _order = 'sequence, name'
    
    name = fields.Char(string='Name', required=True)
    min_age = fields.Integer(string='Minimum Age')
    max_age = fields.Integer(string='Maximum Age')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    
    doctor_ids = fields.Many2many(
        'res.partner', 
        'doctor_age_rel',
        '_unknown_id',  # Use the existing column name
        'res_partner_id',  # Use the existing column name
        string='Doctors'
    )
    
    # Optional: Add validation to ensure min_age < max_age if both provided
    @api.constrains('min_age', 'max_age')
    def _check_age_range(self):
        for record in self:
            if record.min_age and record.max_age and record.min_age > record.max_age:
                raise models.ValidationError(_('Minimum age must be less than maximum age'))
    
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Age preference name must be unique!')
    ]