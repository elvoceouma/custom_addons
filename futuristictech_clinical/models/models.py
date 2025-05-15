# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

# For missing action models referenced in menus
class HospitalActivityRecord(models.Model):
    _name = 'hospital.activity.record'
    _description = 'Hospital Activity Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    activity = fields.Char(string='Activity')
    comments = fields.Text(string='Comments')
    activity_type = fields.Selection([
        ('formal', 'Formal'),
        ('informal', 'Informal')
    ], string='Activity Type', required=True, default='formal')

# class HospitalAppointment(models.Model):
#     _name = 'hospital.appointment'
#     _description = 'Hospital Appointment'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
    
#     name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
#     physician_id = fields.Many2one('hospital.physician', string='Physician', required=True, tracking=True)
#     appointment_date = fields.Datetime(string='Appointment Date', required=True, tracking=True)
#     purpose = fields.Text(string='Purpose')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('confirmed', 'Confirmed'),
#         ('done', 'Done'),
#         ('cancelled', 'Cancelled')
#     ], string='Status', default='draft', tracking=True)
    
#     @api.model_create_multi
#     def create(self, vals_list):
#         for vals in vals_list:
#             if vals.get('name', _('New')) == _('New'):
#                 vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
#         return super(HospitalAppointment, self).create(vals_list)


class HospitalGynecology(models.Model):
    _name = 'hospital.gynecology'
    _description = 'Hospital Gynecology'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True, tracking=True)
    visit_date = fields.Date(string='Visit Date', default=fields.Date.context_today, tracking=True)
    reason = fields.Text(string='Reason for Visit')
    findings = fields.Text(string='Findings')
    recommendations = fields.Text(string='Recommendations')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.gynecology') or _('New')
        return super(HospitalGynecology, self).create(vals_list)
    


# Medicine Consumption Model
# class HospitalMedicineConsumption(models.Model):
#     _name = 'hospital.medicine.consumption'
#     _description = 'Hospital Medicine Consumption'
#     _inherit = ['mail.thread', 'mail.activity.mixin']

#     name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
#                        default=lambda self: _('New'))
#     date = fields.Date(string='Date', default=fields.Date.context_today)
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     physician_id = fields.Many2one('hospital.physician', string='Physician')
#     medicine_line_ids = fields.One2many('hospital.medicine.consumption.line', 'consumption_id', 
#                                        string='Medicine Lines')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('confirm', 'Confirmed'),
#         ('done', 'Done'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', default='draft', tracking=True)
#     notes = fields.Text(string='Notes')
    
    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('name', _('New')) == _('New'):
    #             vals['name'] = self.env['ir.sequence'].next_by_code('hospital.medicine.consumption') or _('New')
    #     return super(HospitalMedicineConsumption, self).create(vals_list)
    
    # def action_confirm(self):
    #     self.state = 'confirm'
    
    # def action_done(self):
    #     self.state = 'done'
    
    # def action_cancel(self):
    #     self.state = 'cancel'
    
    # def action_draft(self):
    #     self.state = 'draft'


class HospitalMedicineConsumptionLine(models.Model):
    _name = 'hospital.medicine.consumption.line'
    _description = 'Hospital Medicine Consumption Line'

    consumption_id = fields.Many2one('hospital.medicine.consumption', string='Consumption')
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    dose_unit_id = fields.Many2one('hospital.dose.unit', string='Dose Unit')
    notes = fields.Text(string='Notes')



class HospitalVaccineType(models.Model):
    _name = 'hospital.vaccine.type'
    _description = 'Hospital Vaccine Type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    dosage_schedule = fields.Text(string='Dosage Schedule')
    active = fields.Boolean(string='Active', default=True)


# Tablet/Capsule Model
class HospitalTabletCapsule(models.Model):
    _name = 'hospital.tablet.capsule'
    _description = 'Hospital Tablet/Capsule'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    date = fields.Date(string='Date', default=fields.Date.context_today)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    quantity = fields.Float(string='Quantity', default=1.0)
    frequency_id = fields.Many2one('hospital.drug.frequency', string='Frequency')
    campus_id = fields.Many2one('hospital.campus', string='Campus')
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    person_responsible = fields.Many2one('res.users', string='Person Responsible')
    time = fields.Char(string='Time', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('prescribed', 'Prescribed'),
        ('dispensed', 'Dispensed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.tablet.capsule') or _('New')
        return super(HospitalTabletCapsule, self).create(vals_list)


# Injection/Application Model
class HospitalInjectionApplication(models.Model):
    _name = 'hospital.injection.application'
    _description = 'Hospital Injection/Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    nurse_id = fields.Many2one('res.users', string='Nurse')
    route_id = fields.Many2one('hospital.drug.route', string='Route')
    dosage = fields.Float(string='Dosage')
    dose_unit_id = fields.Many2one('hospital.dose.unit', string='Dose Unit')
    date_time = fields.Datetime(string='Date & Time', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('administered', 'Administered'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.injection.application') or _('New')
        return super(HospitalInjectionApplication, self).create(vals_list)


# Nurses Campus Duty Model
class HospitalNursesCampusDuty(models.Model):
    _name = 'hospital.nurses.campus.duty'
    _description = 'Hospital Nurses Campus Duty Allocation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    nurse_id = fields.Many2one('res.users', string='Nurse', required=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True)
    date_from = fields.Date(string='Date From', default=fields.Date.context_today, required=True)
    date_to = fields.Date(string='Date To', required=True)
    shift = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ], string='Shift', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.nurses.campus.duty') or _('New')
        return super(HospitalNursesCampusDuty, self).create(vals_list)



# Informed Consent Form Model
class HospitalInformedConsentForm(models.Model):
    _name = 'hospital.informed.consent.form'
    _description = 'Hospital Informed Consent Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    procedure = fields.Text(string='Procedure', required=True)
    risks = fields.Text(string='Risks and Complications')
    benefits = fields.Text(string='Benefits')
    alternatives = fields.Text(string='Alternatives')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    patient_signature = fields.Binary(string='Patient Signature')
    physician_signature = fields.Binary(string='Physician Signature')
    witness_id = fields.Many2one('res.users', string='Witness')
    witness_signature = fields.Binary(string='Witness Signature')
    nurse_id = fields.Many2one('res.users', string='Nurse')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('signed', 'Signed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    age = fields.Integer(string='Age')
    admitting_person = fields.Char(string='Admitting Person')
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.informed.consent.form') or _('New')
        return super(HospitalInformedConsentForm, self).create(vals_list)


class HospitalEctConsentForm(models.Model):
    _name = 'hospital.ect.consent.form'
    _description = 'Hospital ECT Consent Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='EC Format', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    ip_number = fields.Char(string='IP Number', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    age = fields.Integer(string='Age')
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Sex')
    admitting_person = fields.Char(string='Admitting Person')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    psychiatrist_id = fields.Many2one('hospital.physician', string='Psychiatrist')
    assistant_id = fields.Many2one('res.users', string='Assistant')
    equipment_used = fields.Char(string='Equipment Used')
    diagnosis = fields.Char(string='Diagnosis')
    num_sessions = fields.Integer(string='Number of Sessions')
    anesthesia_type = fields.Char(string='Anesthesia Type')
    risks_explained = fields.Boolean(string='Risks Explained')
    benefits_explained = fields.Boolean(string='Benefits Explained')
    alternatives_explained = fields.Boolean(string='Alternatives Explained')
    patient_signature = fields.Binary(string='Patient Signature')
    physician_signature = fields.Binary(string='Physician Signature')
    witness_id = fields.Many2one('res.users', string='Witness')
    witness_signature = fields.Binary(string='Witness Signature')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('signed', 'Signed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    others = fields.Text(string='Others')
    internal_code = fields.Char(string='Internal Code')
    # log_ids = fields.One2many('ect.form.log', 'form_id', string='Logs')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.ect.consent.form') or _('New')
        return super(HospitalEctConsentForm, self).create(vals_list)

    def action_sign(self):
        self.state = 'signed'

    def action_cancel(self):
        self.state = 'cancelled'
        
        
class HospitalProceduralFormSection86(models.Model):
    _name = 'hospital.procedural.form.section.86'
    _description = 'Hospital Procedural Form Section-86'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    
    # Related fields from Patient for display
    patient_name_display = fields.Char(related='patient_id.name', string='Patient Name', readonly=True, store=True)
    patient_age_display = fields.Integer(related='patient_id.age', string='Patient Age', readonly=True, store=True)
    patient_sex_display = fields.Selection(related='patient_id.gender', string='Patient Sex', readonly=True, store=True)
    # For Tree View consistency
    patient_ip_number_tree = fields.Char(string='IP Number', store=True, readonly=True)


    physician_id = fields.Many2one('hospital.physician', string='Mental Health Professional (Psychiatrist)', required=True, tracking=True)
    
    form_datetime = fields.Datetime(string='Date & Time', default=fields.Datetime.now, required=True, tracking=True) # Changed from Date to Datetime

    # New fields from the form image
    mrn_no = fields.Char(string='MRN No', tracking=True)
    admitting_person_identifier = fields.Char(string='Admitting Person', tracking=True) # Label in image is 'Admitting Person'

    symptom_severity_text = fields.Text(string='Severity of the Symptoms (As per Relevant Scales)', tracking=True)
    clinical_assessment_text = fields.Text(string='Clinical Assessment of the Severity Requiring Admission (Mental Illness of Severity Requiring admission)', tracking=True)
    care_plan_text = fields.Text(string='Care Plan (Likely Benefits from Admission)', tracking=True)
    patient_understanding_text = fields.Text(string='Patients Understanding of the Admission and Request for Admission', tracking=True)
    purpose_as_per_patient_text = fields.Text(string='Purpose (As per Patient)', tracking=True)
    support_required_text = fields.Text(string='Support Required for Taking Mental Health Decision', tracking=True)
    
    medical_officer_id = fields.Many2one('hospital.physician', string='Medical Officer', tracking=True) # Or res.users
    non_psychiatrist_professional_id = fields.Many2one('hr.employee', string='Mental Health Professional (Non Psychiatrist)', tracking=True) # Or other relevant model

    # Existing fields, review their usage with new detailed fields
    procedure_details = fields.Text(string='General Procedure Details', tracking=True) # Kept for general notes
    reasons = fields.Text(string='General Reasons', tracking=True) # Kept for general notes
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'In Progress'), # Updated label
        ('approved', 'Completed'),   # Updated label
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    
    notes = fields.Text(string='Additional Internal Notes') # Renamed for clarity
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.procedural.form.section.86') or _('New')
        return super(HospitalProceduralFormSection86, self).create(vals_list)

    # Action Buttons
    def action_submit(self):
        self.ensure_one()
        self.write({'state': 'submitted'})
        return True

    def action_approve(self):
        self.ensure_one()
        self.write({'state': 'approved'})
        return True

    def action_reject(self):
        self.ensure_one()
        self.write({'state': 'rejected'})
        return True

    def action_reset_to_draft(self):
        for record in self:
            if record.state in ['submitted', 'approved', 'rejected']:
                record.state = 'draft'
        return True
    
# Enhanced Recovery Model
class HospitalEnhancedRecovery(models.Model):
    _name = 'hospital.enhanced.recovery'
    _description = 'Hospital Enhanced Recovery (CEROP)'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                      default=lambda self: _('New'))
    name_seq = fields.Char(string='Form Number', readonly=True)
    ip_number = fields.Char(string='IP Number', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    mrn_no = fields.Char(string='MRN Number')
    age = fields.Integer(string='Age')
    admitted_by = fields.Char(string='Admitted By')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex')
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    psychiatrist = fields.Char(string='Psychiatrist')
    languages_known = fields.Many2many('res.lang', string='Languages Known')
    residence = fields.Char(string='Residence')
    psychiatric_diagnosis = fields.Char(string='Psychiatric Diagnosis')
    medical_comorbidity = fields.Char(string='Medical Comorbidity')
    psychiatric_hospitalisation = fields.Char(string='Psychiatric Hospitalisation')
    client_education = fields.Char(string='Client Education')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed')
    ], string='Marital Status')
    doi = fields.Char(string='DOI')
    duration = fields.Char(string='Duration')
    inter_episodic = fields.Text(string='Inter Episodic')
    current_living = fields.Text(string='Current Living')
    substance_use = fields.Text(string='Substance Use')
    understanding_illness = fields.Text(string='Understanding Illness')
    treatment_adherence = fields.Text(string='Treatment Adherence')
    patients_basic_activity = fields.Text(string="Patient's Basic Activity")
    patient_instrumental = fields.Text(string='Patient Instrumental')
    patient_functioning = fields.Text(string='Patient Functioning')
    attitude_emotions = fields.Text(string='Attitude Emotions')
    concerns_caregiver = fields.Text(string='Concerns Caregiver')
    short_term = fields.Text(string='Short Term Goals')
    long_term = fields.Text(string='Long Term Goals')
    disability_certification = fields.Boolean(string='Disability Certification')
    perceived_change = fields.Text(string='Perceived Change')
    commitment_change = fields.Text(string='Commitment Change')
    time_and_effort = fields.Text(string='Time and Effort')
    potential_barriers = fields.Text(string='Potential Barriers')
    advice = fields.Text(string='Advice')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.enhanced.recovery') or _('New')
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.enhanced.recovery.seq') or _('New')
        return super(HospitalEnhancedRecovery, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'completed'})
    
    def action_inprogress(self):
        self.write({'state': 'in_progress'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
    
    def action_draft(self):
        self.write({'state': 'draft'})

# Case Formulation Model
class HospitalCaseFormulation(models.Model):
    _name = 'hospital.case.formulation'
    _description = 'Hospital Case Formulation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Case Number', required=True, copy=False, readonly=True,
                         default=lambda self: _('New'))
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    
    # Patient Information
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', readonly=True)
    mrn_no = fields.Char(string='MRN Number', readonly=True)
    age = fields.Integer(string='Age', readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female','Female'),
        ('other', 'Other')
    ], string="Gender", readonly=True)
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)

    # Predisposing - Biological Factors
    genetic = fields.Text(string='Genetic', tracking=True)
    birth_trauma = fields.Text(string='Birth Trauma', tracking=True)
    illness_psychological = fields.Text(string='Illness (Psychological)', tracking=True)
    physical = fields.Text(string='Physical', tracking=True)
    medication = fields.Text(string='Medication', tracking=True)
    drugs = fields.Text(string='Drugs', tracking=True)
    alcohol = fields.Text(string='Alcohol', tracking=True)
    pain = fields.Text(string='Pain', tracking=True)
    
    # Predisposing - Psychological Factors
    personality = fields.Text(string='Personality', tracking=True)
    modelling = fields.Text(string='Modelling', tracking=True)
    defences = fields.Text(string='Defences', tracking=True)
    coping_strategies = fields.Text(string='Coping Strategies', tracking=True)
    self_esteem = fields.Text(string='Self Esteem', tracking=True)
    body_image = fields.Text(string='Body Image', tracking=True)
    cognition = fields.Text(string='Cognition', tracking=True)
    
    # Predisposing - Social Factors
    socio_economic = fields.Text(string='Socio-Economic', tracking=True)
    trauma = fields.Text(string='Trauma', tracking=True)
    
    # Precipitating - Biological Factors
    precipitating_medication = fields.Text(string='Medication', tracking=True)
    precipitating_trauma = fields.Text(string='Trauma', tracking=True)
    precipitating_drug_alcohol = fields.Text(string='Drug/Alcohol', tracking=True)
    precipitating_acute_illness = fields.Text(string='Acute Illness', tracking=True)
    precipitating_pain = fields.Text(string='Pain', tracking=True)
    
    # Precipitating - Psychological Factors
    precipitating_state_life = fields.Text(string='State/Life Events', tracking=True)
    precipitating_loss_grief = fields.Text(string='Loss/Grief', tracking=True)
    precipitating_treatment = fields.Text(string='Treatment', tracking=True)
    precipitating_stressor = fields.Text(string='Stressor', tracking=True)
    
    # Precipitating - Social Factors
    precipitating_work = fields.Text(string='Work', tracking=True)
    precipitating_finance = fields.Text(string='Finance', tracking=True)
    precipitating_connections = fields.Text(string='Connections', tracking=True)
    precipitating_relationships = fields.Text(string='Relationships', tracking=True)
    
    # Perpetuating Factors
    perpetuating = fields.Text(string='Perpetuating Factors', tracking=True)
    
    # Protective - Biological Factors
    protective_health = fields.Text(string='Health', tracking=True)
    
    # Protective - Psychological Factors
    protective_engagement = fields.Text(string='Engagement', tracking=True)
    protective_insight = fields.Text(string='Insight', tracking=True)
    protective_adherence = fields.Text(string='Adherence', tracking=True)
    protective_coping_strategies = fields.Text(string='Coping Strategies', tracking=True)
    protective_intelligence = fields.Text(string='Intelligence', tracking=True)
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.case.formulation') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.case.formulation.seq') or _('New')
        return super(HospitalCaseFormulation, self).create(vals_list)
    
    def inprogress(self):
        """Set state to in_progress"""
        return self.write({'state': 'in_progress'})
    
    def action_confirm(self):
        """Confirm the case formulation"""
        return self.write({'state': 'completed'})


class HospitalEmergencyAssessment(models.Model):
    _name = 'hospital.emergency.assessment'
    _description = 'Hospital Emergency Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', readonly=True, copy=False)
    
    # Patient information
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', readonly=True)
    mrn_no = fields.Char(string='MRN No', readonly=True)
    age = fields.Integer(string='Age', readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female','Female'),
        ('other', 'Other')
    ], string="Gender", readonly=True)
    
    # Staff information
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)
    medical_officer = fields.Many2one('hospital.physician', string='Medical Officer', tracking=True)
    staff_nurse = fields.Many2one('res.users', string='Staff Nurse', tracking=True)
    
    # Basic information
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    occupation = fields.Char(string='Occupation', tracking=True)
    identification_mark = fields.Char(string='Identification Mark', tracking=True)
    
    # Patient relative information
    patient_relative = fields.Char(string='Patient Relative', tracking=True)
    reliable_unreliable = fields.Selection([
        ('reliable', 'Reliable'),
        ('unreliable', 'Unreliable')
    ], string='Reliable/Unreliable', tracking=True)
    relationship_patient = fields.Char(string='Relationship with Patient', tracking=True)
    
    # Medical information
    complaints = fields.Text(string='Complaints', tracking=True)
    allergic_history = fields.Text(string='Allergic History', tracking=True)
    
    # Physical examination
    height = fields.Float(string='Height (cm)', tracking=True)
    weight = fields.Float(string='Weight (kg)', tracking=True)
    skin = fields.Char(string='Skin', tracking=True)
    conjunctiva = fields.Char(string='Conjunctiva', tracking=True)
    rs = fields.Char(string='RS (Respiratory System)', tracking=True)
    cvs = fields.Char(string='CVS (Cardiovascular System)', tracking=True)
    pa = fields.Char(string='PA (Per Abdomen)', tracking=True)
    
    # Glasgow Coma Scale
    coma_score = fields.Integer(string='Glasgow Coma Score', tracking=True)
    eyes = fields.Selection([
        ('1', '1 - No eye opening'),
        ('2', '2 - Eye opening to pain'),
        ('3', '3 - Eye opening to verbal command'),
        ('4', '4 - Eyes open spontaneously')
    ], string='Eyes', tracking=True)
    verbal = fields.Selection([
        ('1', '1 - No verbal response'),
        ('2', '2 - Incomprehensible sounds'),
        ('3', '3 - Inappropriate words'),
        ('4', '4 - Confused'),
        ('5', '5 - Oriented')
    ], string='Verbal', tracking=True)
    motor = fields.Selection([
        ('1', '1 - No motor response'),
        ('2', '2 - Extension to pain'),
        ('3', '3 - Flexion to pain'),
        ('4', '4 - Withdrawal from pain'),
        ('5', '5 - Localizing pain'),
        ('6', '6 - Obeys commands')
    ], string='Motor', tracking=True)
    
    # Mental state examination
    appearance_behaviour = fields.Text(string='Appearance & Behaviour', tracking=True)
    psychomotor_activity = fields.Text(string='Psychomotor Activity', tracking=True)
    speech = fields.Text(string='Speech', tracking=True)
    mood = fields.Text(string='Mood', tracking=True)
    perceptual_disturbances = fields.Text(string='Perceptual Disturbances', tracking=True)
    cognitive_functions = fields.Text(string='Cognitive Functions', tracking=True)
    insight = fields.Text(string='Insight', tracking=True)
    
    # Treatment and investigations
    lab_investigation = fields.Text(string='Lab Investigation', tracking=True)
    treatment = fields.Text(string='Treatment', tracking=True)
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.emergency.assessment') or _('New')
            if not vals.get('name_seq'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.emergency.assessment.seq') or _('EA-0000')
        return super(HospitalEmergencyAssessment, self).create(vals_list)
    
    def inprogress(self):
        """Set state to in_progress"""
        self.write({'state': 'in_progress'})
        
    def action_confirm(self):
        """Set state to completed"""
        self.write({'state': 'completed'})

class HospitalIncidentReport(models.Model):
    _name = 'hospital.incident.report'
    _description = 'Hospital Incident Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', readonly=True, copy=False)
    
    # Patient information
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', readonly=True)
    mrn_no = fields.Char(string='MRN No', readonly=True)
    age = fields.Integer(string='Age', readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex')
    
    # Location information
    location_room = fields.Char(string='Room', tracking=True)
    location_bed = fields.Char(string='Bed', tracking=True)
    loaction_ward = fields.Char(string='Ward', tracking=True)  # Keeping typo for compatibility
    
    # Staff information
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)
    
    # Date information
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    
    # Medical information
    diagnosis = fields.Text(string='Diagnosis', tracking=True)
    
    # Incident details
    incident_type = fields.Selection([
        ('fall', 'Fall'),
        ('medication', 'Medication Error'),
        ('treatment', 'Treatment Error'),
        ('infection', 'Infection'),
        ('ect_anesthesia', 'ECT/Anesthesia'),
        ('drugs_iv_blood', 'Drugs/IV/Blood'),
        ('laboratory', 'Laboratory'),
        ('radiology', 'Radiology'),
        ('miscellaneous', 'Miscellaneous'),
        ('other', 'Other'),
    ], string='Incident Type', tracking=True)
    
    # Incident subtypes
    fall_subtype = fields.Char(string='Fall Subtype', tracking=True)
    treatment_subtype = fields.Char(string='Treatment Subtype', tracking=True)
    infection_subtype = fields.Char(string='Infection Subtype', tracking=True)
    ect_anesthesia_subtype = fields.Char(string='ECT/Anesthesia Subtype', tracking=True)
    miscellaneous_subtype = fields.Char(string='Miscellaneous Subtype', tracking=True)
    
    # Issue details
    drugs_iv_blood_issue = fields.Text(string='Drugs/IV/Blood Issue', tracking=True)
    laboratory_issue = fields.Text(string='Laboratory Issue', tracking=True)
    radiology_issue = fields.Text(string='Radiology Issue', tracking=True)
    other_issue = fields.Text(string='Other Issue', tracking=True)
    
    # Incident occurrence
    incident_occured = fields.Datetime(string='Incident Occurred', tracking=True)
    
    # Description and actions
    narrative_description = fields.Text(string='Narrative Description', tracking=True)
    immediate_action = fields.Text(string='Immediate Action Taken', tracking=True)
    root_cause = fields.Text(string='Root Cause Analysis', tracking=True)
    corrective_action = fields.Text(string='Corrective Action Plan', tracking=True)
    
    # Reporting information
    reported_by = fields.Many2one('res.users', string='Reported By', default=lambda self: self.env.user.id, tracking=True)
    reporting_date_time = fields.Datetime(string='Reporting Date & Time', default=fields.Datetime.now, tracking=True)
    report_sent_date_time = fields.Datetime(string='Report Sent Date & Time', tracking=True)
    reviewed_by = fields.Many2one('res.users', string='Reviewed By', tracking=True)
    review_time = fields.Datetime(string='Review Time', tracking=True)
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.incident.report') or _('New')
            if not vals.get('name_seq'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.incident.report.seq') or _('IR-0000')
        return super(HospitalIncidentReport, self).create(vals_list)
    
    def inprogress(self):
        """Set state to in_progress"""
        self.write({'state': 'in_progress'})
        
    def action_confirm(self):
        """Set state to completed"""
        self.write({'state': 'completed'})

from odoo import api, fields, models, _


class HospitalCapacityAssessment(models.Model):
    _name = 'hospital.capacity.assessment'
    _description = 'Hospital Capacity Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', required=True, copy=False, readonly=True,
                          default=lambda self: _('New'))
    
    # Patient Information Fields
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name',  readonly=True)
    mrn_no = fields.Char(string='MRN No',  readonly=True)
    age = fields.Integer(string='Age',  readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex')
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)
    
    # Assessment Fields
    date = fields.Date(string='Assessment Date', default=fields.Date.context_today, required=True, tracking=True)
    purpose = fields.Text(string='Purpose of Assessment', tracking=True)
    advanced_directive = fields.Text(string='Advanced Directive', tracking=True)
    
    # Lack of Capacity Fields
    condition_meaning = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Condition Meaning', tracking=True, 
    help="Is she/he in a condition that one cannot have any kind of meaningful conversation with him/her")
    condition_explanation = fields.Text(string='Explanation', tracking=True)
    
    # Understanding Information Fields
    individual_oriented = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Individual Oriented', tracking=True)
    relevant_information = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Relevant Information', tracking=True)
    simple_commands = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Simple Commands', tracking=True)
    acknowledge = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Acknowledge Illness', tracking=True)
    one_explanation = fields.Text(string='Explanation', tracking=True)
    
    # Appreciating Consequences Fields
    individual_agree = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Individual Agree', tracking=True)
    receive_treatment = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Receive Treatment', tracking=True)
    agree_treatment = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Agree Treatment', tracking=True)
    two_explanation = fields.Text(string='Explanation', tracking=True)
    
    # Communication Fields
    communicating = fields.Text(string='Communication Details', tracking=True)
    individual_communicate = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Individual Communicate', tracking=True)
    explanation_communicate = fields.Text(string='Communication Explanation', tracking=True)
    
    # Decision Making Fields
    self_treatment = fields.Boolean(string='Can Make Treatment Decisions Without Support', tracking=True)
    support_treatment = fields.Boolean(string='Needs Support for Treatment Decisions', tracking=True)
    four_explanation = fields.Text(string='Decision Making Explanation', tracking=True)
    
    # State Management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.capacity.assessment') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.capacity.assessment.seq') or _('New')
        return super(HospitalCapacityAssessment, self).create(vals_list)
    
    def action_confirm(self):
        """Change state to completed when confirmed"""
        self.write({'state': 'completed'})
    
    def inprogress(self):
        """Change state to in_progress"""
        self.write({'state': 'in_progress'})

# Independent Examination Professional I Model
class HospitalIndependantExaminationProfessionalI(models.Model):
    _name = 'hospital.independant.examination.professional.i'
    _description = 'Hospital Independent Examination Professional I'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    examiner_id = fields.Many2one('hospital.physician', string='Examining Professional', required=True)
    date = fields.Date(string='Examination Date', default=fields.Date.context_today, required=True)
    purpose = fields.Text(string='Purpose of Examination', required=True)
    findings = fields.Text(string='Clinical Findings')
    diagnosis = fields.Text(string='Diagnosis/Opinion')
    recommendations = fields.Text(string='Recommendations')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.independant.examination.professional.i') or _('New')
        return super(HospitalIndependantExaminationProfessionalI, self).create(vals_list)
    

class HospitalIndependentExaminationProfessionalII(models.Model):
    _name = 'hospital.independent.examination.professional.ii'
    _description = 'Hospital Independent Examination Professional II'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                        default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', required=True, copy=False, readonly=True,
                        default=lambda self: _('New'))
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    mrn_no = fields.Char(string='MRN No', tracking=True)
    date = fields.Date(string='Examination Date', default=fields.Date.context_today, required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex', tracking=True)
    
    # Professional line
    professional_line_ids = fields.One2many('hospital.independent.examination.professional.line', 
                                           'examination_id', string='Professional Lines')
    
    # Diagnosis and symptoms
    provisional_diagnosis = fields.Text(string='Provisional Diagnosis', tracking=True)
    severity_symptoms = fields.Text(string='Severity of Symptoms', tracking=True)
    examination_type = fields.Selection([
        ('professional_1', 'Professional I'),
        ('professional_2', 'Professional II'),
    ], string='Examination Type', default='professional_2')
    
    # Reasons for admission and treatment
    recently_threatened = fields.Boolean(string='Recently threatened or attempted to cause harm to self', tracking=True)
    recently_behaved = fields.Boolean(string='Recently behaved violently or caused another person to fear violence', tracking=True)
    inability = fields.Boolean(string='Inability to care for self and protect self from significant harm', tracking=True)
    nature_purpose = fields.Boolean(string='Nature/Purpose of Admission not understood by Patient due to Mental Illness', tracking=True)
    
    # Additional notes
    additional_notes = fields.Text(string='Additional Notes', tracking=True)
    
    # Care Plan
    diagnostics = fields.Boolean(string='Diagnostics and assessment', tracking=True)
    symptom = fields.Boolean(string='Symptom control', tracking=True)
    psychopharmacological = fields.Boolean(string='Psychopharmacological management', tracking=True)
    observation = fields.Boolean(string='Observation', tracking=True)
    psycho_social = fields.Boolean(string='Psycho-social intervention', tracking=True)
    rehabilitation = fields.Boolean(string='Rehabilitation', tracking=True)
    risk_harm = fields.Boolean(string='Risk/harm management', tracking=True)
    crisis = fields.Boolean(string='Crisis management', tracking=True)
    
    # Previous attempts of support
    op_treatment = fields.Boolean(string='OP Treatment', tracking=True)
    home_care = fields.Boolean(string='Home Care', tracking=True)
    independent_patient = fields.Boolean(string='Independent Patient', tracking=True)
    alternative_treatment = fields.Boolean(string='Alternative Treatment', tracking=True)
    psychological_counselling = fields.Boolean(string='Psychological Counselling', tracking=True)
    
    # Professional categories
    professional_category_id = fields.One2many('hospital.professional.category', 
                                              'examination_id', string='Professional Categories')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.independent.examination.professional.ii') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.independent.examination.professional.ii.seq') or _('New')
        return super(HospitalIndependentExaminationProfessionalII, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'completed'})
    
    def inprogress(self):
        self.write({'state': 'in_progress'})


class HospitalIndependentExaminationProfessionalLine(models.Model):
    _name = 'hospital.independent.examination.professional.line'
    _description = 'Hospital Independent Examination Professional Line'
    
    examination_id = fields.Many2one('hospital.independent.examination.professional.ii', 
                                    string='Independent Examination', ondelete='cascade')
    professional_id = fields.Many2one('hr.employee', string='Professional', 
                                    )
    examination_date = fields.Date(string='Examination Date')
    place = fields.Char(string='Place')


class HospitalProfessionalCategory(models.Model):
    _name = 'hospital.professional.category'
    _description = 'Hospital Professional Category'
    
    examination_id = fields.Many2one('hospital.independent.examination.professional.ii', 
                                    string='Independent Examination', ondelete='cascade')
    doctor_name = fields.Char(string='Doctor Name')
    category = fields.Char(string='Category')
    date = fields.Date(string='Date')
    date_admission = fields.Date(string='Date of Admission')
    expiry_date = fields.Date(string='Expiry Date')


class HospitalInjctionApplication(models.Model):
    _name = 'hospital.injection.application'
    _description = 'Hospital Injection/Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                        default=lambda self: _('New'))
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    nurse_id = fields.Many2one('res.users', string='Nurse')
    route_id = fields.Many2one('hospital.drug.route', string='Route')
    dosage = fields.Float(string='Dosage')
    dose_unit_id = fields.Many2one('hospital.dose.unit', string='Dose Unit')
    date_time = fields.Datetime(string='Date & Time', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('administered', 'Administered'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')


class HospitalMedicalProcedure(models.Model):
    _name = 'hospital.medical.procedure'
    _description = 'Medical Procedure'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # For chatter

    # Original fields (kept if sensible)
    name = fields.Char(string='Procedure Reference', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Performing Physician', tracking=True)
    procedure_type = fields.Char(string='Procedure Type', tracking=True)
    notes = fields.Text(string='Procedure Notes')
    complications = fields.Text(string='Complications')

    # Fields from the form view
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission', # Assuming this model exists
        string='IP Number',
        tracking=True
    )
    purpose = fields.Text(string='Purpose', tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        readonly=True # Usually set once
    )
    date_selection = fields.Selection([
        ('by_date', 'By Date'),
        ('by_period', 'By Period')
    ], string="Date Selection Type", tracking=True) # Made the string more descriptive

    requested_date = fields.Date(string='Requested Date', tracking=True)
    start_date = fields.Date(string='Period Start Date', tracking=True)
    end_date = fields.Date(string='Period End Date', tracking=True)

    required_date = fields.Date(string='Required Date', tracking=True) # As per view, though its use alongside others is to be defined by business logic

    approved_date = fields.Datetime(string='Approved Date', readonly=True, tracking=True)
    debit_note_id = fields.Many2one(
        'account.move', # Assuming standard debit notes are account.move
        string='Debit Note',
        readonly=True,
        tracking=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )

    requisition_line_ids = fields.One2many(
        'hospital.medical.procedure.line',
        'procedure_id',
        string='Products/Services'
    )
    material_line_ids = fields.One2many(
        'hospital.medical.procedure.material.line',
        'procedure_id',
        string='Materials Used'
    )

    # --- Business Methods ---
    def action_approve(self):
        self.ensure_one() # Ensure method is called on a single record for this implementation
        if not self.approved_by: # Prevent re-approval or other logic can be added
            self.write({
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now()
            })
            self.message_post(body=_("Procedure approved.")) # Post a message to chatter
        return True

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise models.ValidationError(_("End Date cannot be earlier than Start Date."))


class HospitalMedicalProcedureLine(models.Model):
    _name = 'hospital.medical.procedure.line'
    _description = 'Medical Procedure Product/Service Line'

    procedure_id = fields.Many2one(
        'hospital.medical.procedure',
        string='Medical Procedure',
        required=True,
        ondelete='cascade'
    )
    date = fields.Date(string='Date') # As per the view's invisible field
    product_id = fields.Many2one(
        'product.product',
        string='Product/Service',
        required=True,
        domain="[('type','=','service'),('procedure_product','=',True)]" # Simplified domain for clarity, original had 'debit_note' too
    )
    name = fields.Text(string='Description') # Intended for product description, can be auto-filled
    internal_category_id = fields.Many2one(
        'product.category',
        related='product_id.categ_id',
        string='Internal Category',
        store=True, # Store for easier access if needed
        readonly=True
    )
    quantity = fields.Float(string='Quantity', default=1.0, required=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    price_subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_price_subtotal',
        store=True
    )
    currency_id = fields.Many2one(
        related='procedure_id.company_id.currency_id',
        string='Currency',
        store=True, # Store for monetary field functionality
        readonly=True
    )

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.get_product_multiline_description_sale() if self.product_id else ''
            # Ensure company_id is available for price context if using product pricelists
            # For simplicity, using standard list price. Adjust if pricelists are used.
            self.price_unit = self.product_id.lst_price
        else:
            self.name = ''
            self.price_unit = 0.0


class HospitalMedicalProcedureMaterialLine(models.Model):
    _name = 'hospital.medical.procedure.material.line'
    _description = 'Medical Procedure Material Line'

    procedure_id = fields.Many2one(
        'hospital.medical.procedure',
        string='Medical Procedure',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Material/Drug',
        required=True,
        domain="[('medicine_product','=',True)]" # Assuming 'medicine_product' is a boolean on product.product
    )
    name = fields.Text(string='Description', readonly=False, store=True) # Allow override if needed
    internal_category_id = fields.Many2one(
        'product.category',
        related='product_id.categ_id',
        string='Internal Category',
        store=True,
        readonly=True
    )
    quantity = fields.Float(string='Quantity', default=1.0, required=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Name is related, but if you want to set it differently on change:
            # self.name = self.product_id.display_name
            pass # Name is already related
        else:
            # self.name = '' # Handled by related if product is unset
            pass

class HospitalMedicineRequisition(models.Model):
    _name = 'hospital.medicine.requisition'
    _description = 'Medicine Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Requisition Reference',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True
    )
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        domain="[('state','!=','discharge_advised')]",
        tracking=True
    )
    patient_id = fields.Many2one(
        'hospital.patient',
        string='Patient',
        required=True,
        tracking=True
    )
    physician_id = fields.Many2one(
        'hospital.physician',
        string='Requesting Physician',
        tracking=True
    )
    purpose = fields.Text(string='Purpose', tracking=True)
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        tracking=True
    )
    requested_date = fields.Date(string='Requested Date', tracking=True)
    required_date = fields.Date(string='Required Date', tracking=True)
    approved_date = fields.Date(string='Approved Date', readonly=True, tracking=True)
    requisition_line_ids = fields.One2many(
        'hospital.medicine.requisition.line',
        'requisition_id',
        string='Medicines',
        tracking=True
    )
    requirement = fields.Text(string='Requirement', tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', tracking=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', tracking=True)
    source_location_id = fields.Many2one('stock.location', string='Source Location', tracking=True)
    destination_location_id = fields.Many2one('stock.location', string='Destination Location', tracking=True)
    move_type = fields.Selection([
        ('direct', 'As soon as possible'),
        ('one', 'When all products are ready')
    ], string='Move Type', default='direct', tracking=True)
    stock_picking_ids = fields.Many2many('stock.picking', string='Stock Pickings', tracking=True)
    stock_picking_count = fields.Integer(string='Stock Picking Count', compute='_compute_stock_picking_count')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        tracking=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, tracking=True)
    debit_note_id = fields.Many2one('account.move', string='Debit Note', readonly=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('issued', 'Issued')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.medicine.requisition') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.write({
            'state': 'inprogress',
            'approved_date': fields.Date.today(),
            'approved_by': self.env.user.id
        })

    @api.depends('stock_picking_ids')
    def _compute_stock_picking_count(self):
        for record in self:
            record.stock_picking_count = len(record.stock_picking_ids)

    def view_stock_picking(self):
        self.ensure_one()
        return {
            'name': _('Stock Pickings'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.stock_picking_ids.ids)],
        }

    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id


class HospitalMedicineRequisitionLine(models.Model):
    _name = 'hospital.medicine.requisition.line'
    _description = 'Medicine Requisition Line'
    
    requisition_id = fields.Many2one('hospital.medicine.requisition', string='Requisition')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('medicine_product','=',True)]",
        required=True
    )
    name = fields.Text(string='Description')
    date = fields.Date(string='Date')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    is_issued = fields.Boolean(string='Is Issued', default=False)
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.internal_category_id = self.product_id.categ_id
            self.price_unit = self.product_id.list_price

class HospitalMicrobiology(models.Model):
    _name = 'hospital.microbiology'
    _description = 'Microbiology Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    specimen_type = fields.Char(string='Specimen Type')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalMinorAdmission(models.Model):
    _name = 'hospital.minor.admission'
    _description = 'Minor Admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Admission Reference', readonly=True)
    name_seq = fields.Char(string='Sequence', readonly=True, copy=False, default=lambda self: _('New'))
    
    # Fields from the form view
    ip_number = fields.Char(string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    
    # Illness symptoms fields
    illness_symptoms_1 = fields.Char(string='Illness Symptoms 1', tracking=True)
    illness_symptoms_2 = fields.Char(string='Illness Symptoms 2', tracking=True)
    illness_symptoms_3 = fields.Char(string='Illness Symptoms 3', tracking=True)
    illness_symptoms_4 = fields.Char(string='Illness Symptoms 4', tracking=True)
    illness_symptoms_5 = fields.Char(string='Illness Symptoms 5', tracking=True)
    
    # Illness documents fields
    illness_doc_1 = fields.Char(string='Illness Document 1', tracking=True)
    illness_doc_2 = fields.Char(string='Illness Document 2', tracking=True)
    illness_doc_3 = fields.Char(string='Illness Document 3', tracking=True)
    illness_doc_4 = fields.Char(string='Illness Document 4', tracking=True)
    illness_doc_5 = fields.Char(string='Illness Document 5', tracking=True)
    
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)
    symptoms_since = fields.Char(string='Symptoms Since', tracking=True, 
                                help="Days / Month / Year eg: 2 Years/4months/10days")
    report_contents = fields.Binary(string='Report Contents', attachment=True)
    
    # Original fields from the provided model
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    guardian_id = fields.Many2one('hospital.patient.relationship', string='Guardian', tracking=True)
    admission_date = fields.Date(string='Admission Date', default=fields.Date.today, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Admitting Physician', tracking=True)
    reason = fields.Text(string='Reason for Admission', tracking=True)
    guardian_consent = fields.Boolean(string='Guardian Consent Obtained', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.minor.admission') or _('New')
        return super(HospitalMinorAdmission, self).create(vals_list)
    
    def action_confirm(self):
        self.state = 'completed'
        return True
    
class HospitalMiscellaneous(models.Model):
    _name = 'hospital.miscellaneous'
    _description = 'Miscellaneous Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    test_type = fields.Char(string='Test Type')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalMolecularBiology(models.Model):
    _name = 'hospital.molecular.biology'
    _description = 'Molecular Biology Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    test_type = fields.Char(string='Test Type')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalMOSRSection86(models.Model):
    _name = 'hospital.mo.sr.section.86'
    _description = 'MO/SR Section 86'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True)
    name_seq = fields.Char(string='Sequence', readonly=True, copy=False, default=lambda self: _('New'))
    
    # Fields from the form view
    ip_number = fields.Char(string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', tracking=True)
    mrn_no = fields.Char(string='MRN No', tracking=True)
    provisional_diagnosis = fields.Text(string='Provisional Diagnosis', tracking=True)
    symptoms_severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Symptoms Severity', tracking=True)
    
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)
    severity_requiring = fields.Selection([
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
        ('icu', 'ICU')
    ], string='Severity Requiring', tracking=True)
    patient_understanding = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Patient Understanding', tracking=True)
    purpose = fields.Selection([
        ('assessment', 'Assessment'),
        ('treatment', 'Treatment'),
        ('followup', 'Follow-up')
    ], string='Purpose', tracking=True)
    report_contents = fields.Binary(string='Report Contents', attachment=True)
    
    # Original fields from the provided model
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', tracking=True)
    assessment = fields.Text(string='Assessment', tracking=True)
    recommendations = fields.Text(string='Recommendations', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.mo.sr.section.86') or _('New')
        return super(HospitalMOSRSection86, self).create(vals_list)
    
    def action_confirm(self):
        self.state = 'completed'
        return True
    

class HospitalOutingExpenses(models.Model):
    _name = 'hospital.outing.expenses'
    _description = 'Outing Expenses'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, tracking=True)
    type = fields.Selection([
        ('outing', 'Outing'),
        ('outside_consultation', 'Outside Consultation')
    ], string='Type', default='outing', tracking=True)
    
    # Partners and Products
    partner_id = fields.Many2one('res.partner', string='Vendor', tracking=True)
    product_id = fields.Many2one('product.product', string='Nature of Outing', domain="[('can_be_expensed','=',True)]")
    partner_payable = fields.Float(string='Vendor Payable')
    
    # Date fields
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    start_datetime = fields.Datetime(string='Start Date & Time')
    end_datetime = fields.Datetime(string='End Date & Time')
    no_of_days = fields.Float(string='No. of Days', compute='_compute_no_of_days', store=True)
    
    # Vehicle and Transportation details
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    opening_km = fields.Float(string='Opening KM')
    closing_km = fields.Float(string='Closing KM')
    total_km = fields.Float(string='Total KM', compute='_compute_total_km', store=True)
    cost_per_km = fields.Float(string='Cost Per KM')
    transportation_charge = fields.Float(string='Toll/Driver Charges')
    
    # Financial fields
    issued_to = fields.Many2one('res.users', string='Amount issued to')
    approved_amount = fields.Float(string='Approved Amount')
    return_charge = fields.Float(string='Amount to be returned', compute='_compute_return_charge', store=True)
    misc_expenditure = fields.Float(string='Miscellaneous Expenditure')
    total_misc_expenditure = fields.Float(string='Total Misc. Expenditure', compute='_compute_total_misc', store=True)
    total_head_count = fields.Integer(string='Total Head Count', compute='_compute_total_head_count', store=True)
    trip_cost = fields.Float(string='Trip Cost', compute='_compute_trip_cost', store=True)
    
    # Related records
    invoice_id = fields.Many2one('account.move', string='Vendor Bill')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    
    # Relationships
    patient_expense_line_ids = fields.One2many('hospital.outing.expense.line', 'outing_expense_id', string='Patient Expense Lines')
    patient_specific_expense_line_ids = fields.One2many('hospital.patient.specific.expense', 'outing_expense_id', string='Patient Specific Expense Lines')
    employee_ids = fields.Many2many('hr.employee', string='Employees / Resources')
    
    # Status field
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Completed')
    ], string='Status', default='new', tracking=True)
    
    @api.depends('start_datetime', 'end_datetime')
    def _compute_no_of_days(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                delta = record.end_datetime - record.start_datetime
                record.no_of_days = delta.total_seconds() / (24 * 60 * 60)
            else:
                record.no_of_days = 0.0
    
    @api.depends('opening_km', 'closing_km')
    def _compute_total_km(self):
        for record in self:
            record.total_km = record.closing_km - record.opening_km
    
    @api.depends('approved_amount', 'partner_payable', 'transportation_charge', 'misc_expenditure')
    def _compute_return_charge(self):
        for record in self:
            total_expenses = record.partner_payable + record.transportation_charge + record.misc_expenditure
            record.return_charge = record.approved_amount - total_expenses
    
    @api.depends('patient_expense_line_ids.misc_expense', 'misc_expenditure')
    def _compute_total_misc(self):
        for record in self:
            patient_misc = sum(record.patient_expense_line_ids.mapped('misc_expense'))
            record.total_misc_expenditure = patient_misc + record.misc_expenditure
    
    @api.depends('patient_expense_line_ids')
    def _compute_total_head_count(self):
        for record in self:
            record.total_head_count = len(record.patient_expense_line_ids)
    
    @api.depends('total_km', 'cost_per_km', 'transportation_charge', 'misc_expenditure')
    def _compute_trip_cost(self):
        for record in self:
            km_cost = record.total_km * record.cost_per_km
            record.trip_cost = km_cost + record.transportation_charge + record.misc_expenditure
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_close(self):
        self.write({'state': 'closed'})
    
    def view_vendor_bill(self):
        self.ensure_one()
        return {
            'name': _('Vendor Bill'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
            'context': {'form_view_initial_mode': 'edit'}
        }


class HospitalOutingExpenseLine(models.Model):
    _name = 'hospital.outing.expense.line'
    _description = 'Outing Expense Line'
    
    outing_expense_id = fields.Many2one('hospital.outing.expenses', string='Outing Expense')
    inpatient_admission_id = fields.Many2one('hospital.inpatient.admission', string='Inpatient Admission', 
                                           domain="[('state','!=','discharge_advised')]")
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    age = fields.Integer(string='Age', related='patient_id.age', store=True)
    sex = fields.Selection(related='patient_id.gender', string='Gender', store=True)
    campus_id = fields.Many2one('hospital.campus', string='Campus')
    block_id = fields.Many2one('hospital.block', string='Block')
    room_id = fields.Many2one('hospital.room', string='Room')
    partner_expense = fields.Float(string='Partner Expense')
    misc_expense = fields.Float(string='Misc. Expense')
    conveyance_expense = fields.Float(string='Conveyance Expense')


class HospitalPatientSpecificExpense(models.Model):
    _name = 'hospital.patient.specific.expense'
    _description = 'Patient Specific Expense'
    
    outing_expense_id = fields.Many2one('hospital.outing.expenses', string='Outing Expense')
    inpatient_admission_id = fields.Many2one('hospital.inpatient.admission', string='Inpatient Admission')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    partner_id = fields.Many2one('res.partner', string='Partner')
    reference = fields.Char(string='Reference')
    amount = fields.Float(string='Amount')
    misc_expense = fields.Float(string='Misc. Expense')
    misc_description = fields.Text(string='Misc. Description')

class HospitalOutingForm(models.Model):
    _name = 'hospital.outing.form'
    _description = 'Hospital Outing Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True)
    name_seq = fields.Char(string='Outing Number', required=True, copy=False, readonly=True, 
                         default=lambda self: _('New'))
    
    # Patient information fields
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    mrn_no = fields.Char(string='MRN No', tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex', tracking=True)
    
    # Outing details
    date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    outing_reason = fields.Text(string='Outing Reason', tracking=True)
    outing_duration = fields.Float(string='Outing Duration', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Outing Destination', tracking=True)
    
    # Staff responsible
    admitted_by = fields.Many2one('hr.employee', string='Admitted By', tracking=True)
    doctor = fields.Many2one('hr.employee', string='Doctor', tracking=True)
    nurse = fields.Many2one('hr.employee', string='Nurse', tracking=True)
    grt = fields.Many2one('hr.employee', string='GRT', tracking=True)
    security = fields.Many2one('hr.employee', string='Security', tracking=True)
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.outing.form') or _('New')
        return super(HospitalOutingForm, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'completed'})
        
    @api.onchange('ip_number')
    def _onchange_ip_number(self):
        if self.ip_number:
            self.patient_name = self.ip_number.name
            self.mrn_no = self.ip_number.mrn_no
            self.age = self.ip_number.age
            self.gender = self.ip_number.gender

class HospitalPatientRequisition(models.Model):
    _name = 'hospital.patient.requisition'
    _description = 'Patient Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Requisition Reference', required=True, readonly=True, copy=False, 
                       default=lambda self: _('New'), tracking=True)
    
    # Patient information
    inpatient_admission_id = fields.Many2one('hospital.inpatient.admission', string='IP Number', tracking=True,
                                            domain="[('state','!=','discharge_advised')]")
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    purpose = fields.Text(string='Purpose', tracking=True)
    
    # Date fields
    date_selection = fields.Selection([
        ('by_date', 'By Date'),
        ('by_period', 'By Period')
    ], string='Date Selection', tracking=True)
    requested_date = fields.Date(string='Requested Date', tracking=True)
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    required_date = fields.Date(string='Required Date', tracking=True)
    approved_date = fields.Date(string='Approved Date', readonly=True, tracking=True)
    
    # Requisition details
    requisition_line_ids = fields.One2many('hospital.patient.requisition.line', 'requisition_id', 
                                          string='Requisition Lines', tracking=True)
    requirement = fields.Text(string='Requirement', tracking=True)
    
    # Warehouse and location information
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', tracking=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', tracking=True)
    source_location_id = fields.Many2one('stock.location', string='Source Location', tracking=True)
    destination_location_id = fields.Many2one('stock.location', string='Destination Location', tracking=True)
    move_type = fields.Selection([
        ('direct', 'As soon as possible'),
        ('one', 'When all products are ready')
    ], string='Move Type', default='direct', tracking=True)
    
    # Related records
    stock_picking_ids = fields.Many2many('stock.picking', string='Stock Pickings', tracking=True)
    stock_picking_count = fields.Integer(string='Stock Picking Count', compute='_compute_stock_picking_count')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # Users
    user_id = fields.Many2one('res.users', string='Requested By', 
                             default=lambda self: self.env.user, readonly=True, tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, tracking=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('issued', 'Issued')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.patient.requisition') or _('New')
        return super(HospitalPatientRequisition, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_approve(self):
        self.write({
            'state': 'inprogress',
            'approved_date': fields.Date.today(),
            'approved_by': self.env.user.id
        })
    
    @api.depends('stock_picking_ids')
    def _compute_stock_picking_count(self):
        for record in self:
            record.stock_picking_count = len(record.stock_picking_ids)
    
    def view_stock_picking(self):
        self.ensure_one()
        return {
            'name': _('Stock Pickings'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.stock_picking_ids.ids)],
        }
    
    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id


# 


class HospitalProfile(models.Model):
    _name = 'hospital.profile'
    _description = 'Patient Profile'
    
    name = fields.Char(string='Profile Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-')
    ], string='Blood Group')
    allergies = fields.Text(string='Allergies')
    chronic_conditions = fields.Text(string='Chronic Conditions')
    family_history = fields.Text(string='Family History')
    lifestyle = fields.Text(string='Lifestyle')

class PatientRequisitionLine(models.Model):
    _name = 'patient.requisition.line'
    _description = 'Patient Requisition Line'
    
    patient_requisition_id = fields.Char(string='Requisition Number')
    inpatient_admission_id = fields.Many2one('hospital.inpatient', string='Inpatient Admission')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    campus_id = fields.Many2one('hospital.campus', string='Campus')
    block_id = fields.Many2one('hospital.block', string='Block')
    room_id = fields.Many2one('hospital.room', string='Room')
    bed_id = fields.Many2one('hospital.bed', string='Bed')
    
    date = fields.Datetime(string='Date')
    product_id = fields.Many2one('product.product', string='Product')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

class HospitalProvisionalBill(models.Model):
    _name = 'hospital.provisional.bill'
    _description = 'Provisional Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Bill Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    inpatient_admission_id = fields.Many2one(
        'hospital.admission', 
        string='IP Number', 
        domain="[('state','!=','Discharged')]"
    )
    purpose = fields.Text(string='Purpose')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    date_selection = fields.Selection([
        ('by_date', 'By Date'),
        ('by_period', 'By Period')
    ], string='Date Selection')
    requested_date = fields.Date(string='Requested Date')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    required_date = fields.Date(string='Required Date', invisible=True)
    approved_date = fields.Date(string='Approved Date', readonly=True)
    debit_note_id = fields.Many2one('account.move', string='Debit Note', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid')
    ], string='Status', default='draft')
    requisition_line_ids = fields.One2many(
        'hospital.provisional.bill.line', 
        'bill_id', 
        string='Products',
        domain=[('line_type', '=', 'product')]
    )
    material_line_ids = fields.One2many(
        'hospital.provisional.bill.line', 
        'bill_id', 
        string='Materials',
        domain=[('line_type', '=', 'material')]
    )
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    notes = fields.Text(string='Notes')

    def action_approve(self):
        for record in self:
            record.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Date.today()
            })


class HospitalProvisionalBillLine(models.Model):
    _name = 'hospital.provisional.bill.line'
    _description = 'Provisional Bill Line'
    
    bill_id = fields.Many2one('hospital.provisional.bill', string='Bill')
    line_type = fields.Selection([
        ('product', 'Product'),
        ('material', 'Material')
    ], string='Line Type')
    date = fields.Date(string='Date')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit


# class HospitalRoomInspection(models.Model):
#     _name = 'hospital.room.inspection'
#     _description = 'Room Inspection'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
    
#     name = fields.Char(string='Inspection Reference', required=True, tracking=True)
#     ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
#     room_id = fields.Many2one('hospital.room', string='Room', required=True, tracking=True)
#     block_id = fields.Many2one('hospital.block', string='Block', related='room_id.block_id', store=True, tracking=True)
#     remarks = fields.Text(string='Remarks', tracking=True)
#     user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
#     # Fields from the original model that weren't in the form view
#     inspector_id = fields.Many2one('res.users', string='Inspector', tracking=True)
#     inspection_date = fields.Datetime(string='Inspection Date', default=fields.Datetime.now, tracking=True)
#     cleanliness = fields.Selection([
#         ('excellent', 'Excellent'),
#         ('good', 'Good'),
#         ('fair', 'Fair'),
#         ('poor', 'Poor')
#     ], string='Cleanliness', tracking=True)
#     maintenance_required = fields.Boolean(string='Maintenance Required', tracking=True)
#     maintenance_notes = fields.Text(string='Maintenance Notes', tracking=True)
#     action_taken = fields.Text(string='Action Taken', tracking=True)
    
class HospitalServiceRequisition(models.Model):
    _name = 'hospital.service.requisition'
    _description = 'Service Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Requisition Reference',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True
    )
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        domain="[('state','!=','discharge_advised')]",
        tracking=True
    )
    patient_id = fields.Many2one(
        'hospital.patient',
        string='Patient',
        required=True,
        tracking=True
    )
    physician_id = fields.Many2one(
        'hospital.physician',
        string='Requesting Physician',
        tracking=True
    )
    prescribing_doctor = fields.Many2one(
        'res.partner',
        string='Prescribing Doctor',
        # domain="[('team_role','in',('psychiatrist','physician'))]",
        tracking=True
    )
    purpose = fields.Text(string='Purpose', tracking=True)
    service_type = fields.Char(string='Service Type', tracking=True)
    description = fields.Text(string='Service Description', tracking=True)
    date_selection = fields.Selection([
        ('by_date', 'By Date'),
        ('by_period', 'By Period')
    ], string='Date Selection', tracking=True)
    requested_date = fields.Date(string='Requested Date', tracking=True)
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    required_date = fields.Date(string='Required Date', tracking=True)
    approved_date = fields.Date(string='Approved Date', readonly=True, tracking=True)
    service_date = fields.Date(
        string='Service Date',
        default=fields.Date.today,
        tracking=True
    )
    requisition_line_ids = fields.One2many(
        'hospital.service.requisition.line',
        'requisition_id',
        string='Services',
        tracking=True
    )
    debit_note_id = fields.Many2one(
        'account.move',
        string='Debit Note',
        readonly=True,
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        tracking=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )
    urgency = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency')
    ], string='Urgency', default='normal', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.service.requisition') or _('New')
        return super().create(vals_list)

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_date': fields.Date.today(),
            'approved_by': self.env.user.id
        })


class HospitalServiceRequisitionLine(models.Model):
    _inherit = 'hospital.service.requisition.line'
    _description = 'Service Requisition Line'
    
    requisition_id = fields.Many2one('hospital.service.requisition', string='Requisition')
    product_id = fields.Many2one(
        'product.product',
        string='Service',
        domain="[('type','=','service'),('debit_note','=',True)]",
        required=True
    )
    
    name = fields.Text(string='Description')
    date = fields.Date(string='Date')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.internal_category_id = self.product_id.categ_id
            self.price_unit = self.product_id.list_price


# class HospitalSpecialPrivileges(models.Model):
#     _name = 'hospital.special.privileges'
#     _description = 'Special Privileges'
    
#     name = fields.Char(string='Reference', required=True)
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     privilege_type = fields.Char(string='Privilege Type')
#     start_date = fields.Date(string='Start Date')
#     end_date = fields.Date(string='End Date')
#     approved_by = fields.Many2one('res.users', string='Approved By')
#     notes = fields.Text(string='Notes')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('requested', 'Requested'),
#         ('approved', 'Approved'),
#         ('expired', 'Expired')
#     ], string='Status', default='draft')

# class HospitalStoreClearance(models.Model):
#     _name = 'hospital.store.clearance'
#     _description = 'Store Clearance'
    
#     name = fields.Char(string='Clearance Reference', required=True)
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     admission_id = fields.Many2one('hospital.admission', string='Admission')
#     clearance_date = fields.Date(string='Clearance Date', default=fields.Date.today)
#     cleared_by = fields.Many2one('res.users', string='Cleared By')
#     items_returned = fields.Boolean(string='All Items Returned')
#     notes = fields.Text(string='Notes')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('in_progress', 'In Progress'),
#         ('cleared', 'Cleared'),
#         ('not_cleared', 'Not Cleared')
#     ], string='Status', default='draft')

class HospitalUrineChemistry(models.Model):
    _name = 'hospital.urine.chemistry'
    _description = 'Urine Chemistry Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    ph_level = fields.Float(string='pH Level')
    glucose = fields.Char(string='Glucose')
    protein = fields.Char(string='Protein')
    ketones = fields.Char(string='Ketones')
    blood = fields.Char(string='Blood')
    notes = fields.Text(string='Notes')

class HospitalUrineScreening(models.Model):
    _name = 'hospital.urine.screening'
    _description = 'Urine Screening Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    color = fields.Char(string='Color')
    appearance = fields.Char(string='Appearance')
    specific_gravity = fields.Float(string='Specific Gravity')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalVariableBilling(models.Model):
    _name = 'hospital.variable.billing'
    _description = 'Variable Billing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Bill Reference', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='IP Number', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Vendor',  tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', tracking=True)
    order_date = fields.Date(string='Order Date', default=fields.Date.today, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    variable_billing_line_ids = fields.One2many('hospital.variable.billing.line', 'variable_billing_id', string='Variable Billing Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('billed', 'Billed')
    ], string='Status', default='draft', tracking=True)
    
    # Fields from original model that are not in the view but keeping them for backward compatibility
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    billing_date = fields.Date(string='Billing Date', default=fields.Date.today)
    service_description = fields.Text(string='Service Description')
    amount = fields.Float(string='Amount')
    approved_by = fields.Many2one('res.users', string='Approved By')
    
    @api.depends('variable_billing_line_ids.price_subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.variable_billing_line_ids.mapped('price_subtotal'))
    
    def action_confirm(self):
        self.state = 'confirmed'
    
    def view_vendor_bill(self):
        self.ensure_one()
        return {
            'name': 'Vendor Bill',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }


class HospitalVariableBillingLine(models.Model):
    _name = 'hospital.variable.billing.line'
    _description = 'Variable Billing Line'
    
    variable_billing_id = fields.Many2one('hospital.variable.billing', string='Variable Billing')
    product_id = fields.Many2one('product.product', string='Product', domain="[('variable_billing','=',True)]")
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price


class HospitalDrugAssays(models.Model):
    _name = 'hospital.drug.assays'
    _description = 'Drug Assays Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    drug_name = fields.Char(string='Drug Name')
    concentration = fields.Float(string='Concentration')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')


# class HospitalBillEstimation(models.Model):
#     _name = 'hospital.bill.estimation'
#     _description = 'Hospital Bill Estimation'
    
#     name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     admission_id = fields.Many2one('hospital.admission', string='Admission')
#     date = fields.Date(string='Date', default=fields.Date.today)
#     estimated_amount = fields.Float(string='Estimated Amount')
#     actual_amount = fields.Float(string='Actual Amount')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('confirmed', 'Confirmed'),
#         ('done', 'Done')
#     ], string='Status', default='draft')

class HospitalBiochemistry(models.Model):
    _name = 'hospital.biochemistry'
    _description = 'Biochemistry Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

# class HospitalCaretakerAllotment(models.Model):
#     _name = 'hospital.caretaker.allotment'
#     _description = 'Caretaker Allotment'
    
#     name = fields.Char(string='Allotment Reference', required=True)
#     caretaker_id = fields.Many2one('hospital.caretaker', string='Caretaker', required=True)
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     start_date = fields.Date(string='Start Date', required=True)
#     end_date = fields.Date(string='End Date')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('assigned', 'Assigned'),
#         ('completed', 'Completed')
#     ], string='Status', default='draft')

from odoo.exceptions import ValidationError
 
 
class HospitalCaretaker(models.Model):
    _name = 'hospital.caretaker'
    _description = 'Hospital Caretaker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    image = fields.Binary(string='Image')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', tracking=True)
    date_of_birth = fields.Date(string='Date of Birth')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    active = fields.Boolean(default=True)
    caretaker_type_id = fields.Many2one('hospital.caretaker.type', string='Caretaker Type', required=True)
    qualification = fields.Char(string='Qualification')
    experience = fields.Text(string='Experience')
    state = fields.Selection([
        ('available', 'Available'),
        ('engaged', 'Engaged'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive')
    ], string='Status', default='available', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            if record.phone and not record.phone.isdigit():
                raise ValidationError(_("Phone number should contain only digits"))

# class HospitalCounsellorClearance(models.Model):
#     _name = 'hospital.counsellor.clearance'
#     _description = 'Counsellor Clearance'
    
#     name = fields.Char(string='Clearance Reference', required=True)
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
#     counsellor_id = fields.Many2one('hospital.physician', string='Counsellor')
#     clearance_date = fields.Date(string='Clearance Date', default=fields.Date.today)
#     is_cleared = fields.Boolean(string='Is Cleared')
#     notes = fields.Text(string='Notes')

class HospitalBiochemistry(models.Model):
    _name = 'hospital.biochemistry'
    _description = 'Biochemistry Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')



class HospitalDAMAForm(models.Model):
    _name = 'hospital.dama.form'
    _description = 'Discharge Against Medical Advice Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='DAMA Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', required=True, copy=False, readonly=True,
                          default=lambda self: _('New'))
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    mrn_no = fields.Char(string='MRN No', tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex', tracking=True)
    
    # DAMA specific fields
    dama_date = fields.Date(string='DAMA Date', tracking=True)
    Patient_relation = fields.Char(string='Patient Relation', tracking=True)
    medical_record = fields.Char(string='Medical Record', tracking=True)
    relation_with = fields.Char(string='Relation With', tracking=True)
    
    # Reasons for DAMA
    reasons_dama = fields.Text(string='Reasons DAMA', tracking=True)
    
    # Additional information
    against_medical = fields.Boolean(string='Against Medical', tracking=True)
    duty_doctor = fields.Many2one('hospital.physician', string='Duty Doctor', tracking=True)
    witness_person = fields.Char(string='Witness Person', tracking=True)
    
    # Status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.dama.form') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.dama.form.seq') or _('New')
        return super(HospitalDAMAForm, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'completed'})
    
    def inprogress(self):
        self.write({'state': 'in_progress'})

class HospitalDischargeClearance(models.Model):
    _name = 'hospital.discharge.clearance'
    _description = 'Hospital Discharge Clearance Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', required=True, copy=False, readonly=True,
                          default=lambda self: _('New'))
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    mrn_no = fields.Char(string='MRN No', tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex', tracking=True)
    
    # Admission and clearance details
    center_admitted = fields.Char(string='Center Admitted', tracking=True)
    clearance_given = fields.Many2one('hr.employee', string='Clearance Given By', 
                                     
                                     tracking=True)
    
    # Patient accompanying documents and materials
    case_history = fields.Integer(string='Case History', default=0, tracking=True)
    progress_notes = fields.Integer(string='Progress Notes', default=0, tracking=True)
    drug_chart = fields.Integer(string='Drug Chart', default=0, tracking=True)
    discharge_summary = fields.Integer(string='Discharge Summary', default=0, tracking=True)
    prescription = fields.Integer(string='Prescription', default=0, tracking=True)
    valuables = fields.Integer(string='Valuables', default=0, tracking=True)
    cloths = fields.Integer(string='Clothes', default=0, tracking=True)
    
    # Other details
    nurse = fields.Many2one('hr.employee', string='Nurse', domain="[('job_id.name','in',['NURSES'])]", tracking=True)
    caretaker = fields.Char(string='Caretaker', tracking=True)
    driver = fields.Char(string='Driver', tracking=True)
    vehicle = fields.Char(string='Vehicle', tracking=True)
    security = fields.Char(string='Security', tracking=True)
    
    # Final verification details
    receive_date = fields.Date(string='Receive Date', tracking=True)
    verified_by = fields.Char(string='Verified By', tracking=True)
    program_manager = fields.Char(string='Program Manager', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge.clearance') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.discharge.clearance.seq') or _('New')
        return super(HospitalDischargeClearance, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'completed'})
    
    def inprogress(self):
        self.write({'state': 'in_progress'})



class HospitalEmergencyMedicine(models.Model):
    _name = 'hospital.emergency.medicine'
    _description = 'Emergency Medicine Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _('New'),
        tracking=True
    )
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        domain="[('state','!=','discharge_advised')]",
        tracking=True
    )
    patient_id = fields.Many2one(
        'hospital.patient',
        string='Patient',
        required=True,
        tracking=True
    )
    physician_id = fields.Many2one(
        'hospital.physician',
        string='Prescribing Physician',
        tracking=True
    )

    advising_doctor_id = fields.Many2one(
        'res.partner',
        string='Advising Doctor',
        # domain="[('doctor','=',True),('active_doctor','=',True)]",
        required=True,
        tracking=True
    )
    purpose = fields.Text(string='Purpose', tracking=True)
    reason = fields.Text(string='Reason', tracking=True)
    note = fields.Text(string='Notes', required=True, tracking=True)
    requested_date = fields.Date(string='Requested Date', tracking=True)
    required_date = fields.Date(string='Required Date', tracking=True)
    approved_date = fields.Date(string='Approved Date', readonly=True, tracking=True)
    date = fields.Datetime(
        string='Date',
        default=fields.Datetime.now,
        tracking=True
    )
    requisition_line_ids = fields.One2many(
        'hospital.emergency.medicine.line',
        'requisition_id',
        string='Medicines',
        tracking=True
    )
    requirement = fields.Text(string='Requirement', tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', tracking=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', tracking=True)
    source_location_id = fields.Many2one('stock.location', string='Source Location', tracking=True)
    destination_location_id = fields.Many2one('stock.location', string='Destination Location', tracking=True)
    move_type = fields.Selection([
        ('direct', 'As soon as possible'),
        ('one', 'When all products are ready')
    ], string='Move Type', default='direct', tracking=True)
    stock_picking_ids = fields.Many2many('stock.picking', string='Stock Pickings', tracking=True)
    stock_picking_count = fields.Integer(string='Stock Picking Count', compute='_compute_stock_picking_count')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        tracking=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
        tracking=True
    )
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True, tracking=True)
    administered = fields.Boolean(string='Administered', tracking=True)
    administered_by = fields.Many2one('res.users', string='Administered By', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('issued', 'Issued')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.emergency.medicine') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_approve(self):
        self.write({
            'state': 'inprogress',
            'approved_date': fields.Date.today(),
            'approved_by': self.env.user.id
        })

    @api.depends('stock_picking_ids')
    def _compute_stock_picking_count(self):
        for record in self:
            record.stock_picking_count = len(record.stock_picking_ids)

    def view_stock_picking(self):
        self.ensure_one()
        return {
            'name': _('Stock Pickings'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.stock_picking_ids.ids)],
        }

    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id


class HospitalEmergencyMedicineLine(models.Model):
    _name = 'hospital.emergency.medicine.line'
    _description = 'Emergency Medicine Line'
    
    requisition_id = fields.Many2one('hospital.emergency.medicine', string='Requisition')
    product_id = fields.Many2one(
        'product.product',
        string='Medicine',
        domain="[('medicine_product','=',True)]",
        required=True
    )
    name = fields.Text(string='Description')
    date = fields.Date(string='Date')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    dosage = fields.Char(string='Dosage')
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    is_issued = fields.Boolean(string='Is Issued', default=False)
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.internal_category_id = self.product_id.categ_id
            self.price_unit = self.product_id.list_price


class HospitalFormCSection86(models.Model):
    _name = 'hospital.form.c.section.86'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Form C Section 86'
    
    name = fields.Char(string='Name', readonly=True)
    name_seq = fields.Char(string='Reference Number', readonly=True)
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(related='ip_number.name', string='Patient Name', store=True)
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    age = fields.Integer(related='ip_number.age', string='Age', store=True)
    since = fields.Char(string='Since', help='How many years')
    admitted_by = fields.Many2one('res.users', string='Admitted By', default=lambda self: self.env.user)
    symptoms_since = fields.Char(string='Symptoms Since', help='Mention the year')
    
    # Illness symptoms fields
    illness_symptoms_1 = fields.Char(string='Illness Symptoms 1')
    illness_symptoms_2 = fields.Char(string='Illness Symptoms 2')
    illness_symptoms_3 = fields.Char(string='Illness Symptoms 3')
    illness_symptoms_4 = fields.Char(string='Illness Symptoms 4')
    illness_symptoms_5 = fields.Char(string='Illness Symptoms 5')
    
    # Illness documents fields
    illness_doc_1 = fields.Char(string='Illness Document 1')
    illness_doc_2 = fields.Char(string='Illness Document 2')
    illness_doc_3 = fields.Char(string='Illness Document 3')
    
    report_contents = fields.Text(string='Report Contents')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = 'Independent Admission'
            if not vals.get('name_seq'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.form.c.section.86') or _('New')
        return super(HospitalFormCSection86, self).create(vals_list)
    
    def action_confirm(self):
        self.state = 'completed'
        return True
    


class HospitalHematology(models.Model):
    _name = 'hospital.hematology'
    _description = 'Hematology Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    hemoglobin = fields.Float(string='Hemoglobin')
    wbc_count = fields.Float(string='WBC Count')
    platelet_count = fields.Float(string='Platelet Count')
    notes = fields.Text(string='Notes')
class HospitalHighSupportAdmission(models.Model):
    _name = 'hospital.high.support.admission'
    _description = 'High Support Admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Admission Reference', readonly=True)
    name_seq = fields.Char(string='Sequence', readonly=True, copy=False, default=lambda self: _('New'))
    
    # Fields from the form view
    ip_number = fields.Char(string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    since = fields.Char(string='Since', tracking=True, help="How many year")
    
    # Illness symptoms fields
    illness_symptoms_1 = fields.Char(string='Illness Symptoms 1', tracking=True)
    illness_symptoms_2 = fields.Char(string='Illness Symptoms 2', tracking=True)
    illness_symptoms_3 = fields.Char(string='Illness Symptoms 3', tracking=True)
    illness_symptoms_4 = fields.Char(string='Illness Symptoms 4', tracking=True)
    illness_symptoms_5 = fields.Char(string='Illness Symptoms 5', tracking=True)
    
    # Illness documents fields
    illness_doc_1 = fields.Char(string='Illness Document 1', tracking=True)
    illness_doc_2 = fields.Char(string='Illness Document 2', tracking=True)
    illness_doc_3 = fields.Char(string='Illness Document 3', tracking=True)
    
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    admitted_by = fields.Many2one('hospital.physician', string='Admitted By', tracking=True)
    symptoms_since = fields.Char(string='Symptoms Since', tracking=True, help="Mention the year")
    report_contents = fields.Binary(string='Report Contents', attachment=True)
    
    # Original fields from the provided model
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    admission_date = fields.Date(string='Admission Date', default=fields.Date.today, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Admitting Physician', tracking=True)
    reason = fields.Text(string='Reason for High Support', tracking=True)
    care_plan = fields.Text(string='Care Plan', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.high.support.admission') or _('New')
        return super(HospitalHighSupportAdmission, self).create(vals_list)
    
    def action_confirm(self):
        self.state = 'completed'
        return True


class HospitalHormones(models.Model):
    _name = 'hospital.hormones'
    _description = 'Hormone Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalImmunology(models.Model):
    _name = 'hospital.immunology'
    _description = 'Immunology Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

from odoo import models, fields, api

class HospitalInvestigationRequest(models.Model):
    _name = 'hospital.investigation.request'
    _description = 'Investigation Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Request Reference', required=True, readonly=True, default='New')
    name_seq = fields.Char(string='Sequence', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    # Patient Information
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True)
    patient_name = fields.Char(related='ip_number.name', string='Patient Name', readonly=True, store=True)
    gender = fields.Selection(related='ip_number.gender', string='Gender', readonly=True, store=True)
    age = fields.Integer(related='ip_number.age', string='Age', readonly=True, store=True)    
    # Investigation Details
    ref_doctor = fields.Many2one('hospital.physician', string='Referring Doctor')
    req_no = fields.Char(string='Request Number')
    clinic_details = fields.Char(string='Clinic Details')
    ward_no = fields.Char(string='Ward Number')
    date = fields.Date(string='Date', default=fields.Date.context_today, readonly=True)
    admitted_by = fields.Char(string='Admitted By')
    bill_no = fields.Char(string='Bill Number')
    collection_time = fields.Datetime(string='Collection Time')
    site = fields.Char(string='Site')
    routine = fields.Boolean(string='Routine')
    other_tests = fields.Text(string='Other Tests')
    
   # Test Categories (now using separate models)
    hematology_ids = fields.Many2many('hematology.test', string='Hematology')
    biochemistry_ids = fields.Many2many('biochemistry.test', string='Biochemistry')
    hormones_ids = fields.Many2many('hormones.test', string='Hormones')
    microbiology_ids = fields.Many2many('microbiology.test', string='Microbiology')
    immunology_ids = fields.Many2many('immunology.test', string='Immunology')
    urine_che_ids = fields.Many2many('urine.chemistry.test', string='Urine Chemistry')
    urine_screening_ids = fields.Many2many('urine.screening.test', string='Urine for Drug Screening')
    drug_assays_ids = fields.Many2many('drug.assays.test', string='Drug Assays')
    molecular_bio_ids = fields.Many2many('molecular.biology.test', string='Molecular Biology')
    miscelleneous_ids = fields.Many2many('miscelleneous.test', string='Miscelleneous')
    profile_ids = fields.Many2many('profile.test', string='Profile')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.investigation.request') or 'New'
        return super(HospitalInvestigationRequest, self).create(vals)
    
    def action_confirm(self):
        self.write({'state': 'completed'})


class HospitalLAMAForm(models.Model):
    _name = 'hospital.lama.form'
    _description = 'Leave Against Medical Advice Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', readonly=True)
    name_seq = fields.Char(string='LAMA Reference', readonly=True)
    
    # Patient information
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True)
    patient_name = fields.Char(string='Patient Name')
    mrn_no = fields.Char(string='MRN Number')
    age = fields.Integer(string='Age')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex')
    
    # LAMA details
    date = fields.Date(string='Creation Date', default=fields.Date.today(), readonly=True)
    lama_date = fields.Date(string='LAMA Date')
    Patient_relation = fields.Char(string='Patient Relation')
    medical_record = fields.Boolean(string='Medical Record')
    relation_with = fields.Char(string='Relation With')
    
    # Medical information
    complaints_admission = fields.Text(string='Complaints on Admission')
    diagnosis = fields.Text(string='Diagnosis')
    request_fir = fields.Text(string='Request FIR')
    reasons_lama = fields.Text(string='Reasons for LAMA')
    
    # Signatures and approval
    against_medical = fields.Char(string='Against Medical Advice')
    duty_doctor = fields.Many2one('hospital.physician', string='Duty Doctor')
    witness_person = fields.Char(string='Witness Person')
    
    # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.lama.form') or 'New'
            vals['name_seq'] = 'LAMA/' + vals['name']
        return super(HospitalLAMAForm, self).create(vals_list)
    
    def inprogress(self):
        self.state = 'in_progress'
    
    def action_confirm(self):
        self.state = 'completed'


class HospitalLabTestRequisition(models.Model):
    _name = 'hospital.lab.test.requisition'
    _description = 'Laboratory Test Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Requisition Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician', tracking=True)
    requisition_date = fields.Date(string='Requisition Date', default=fields.Date.today, tracking=True)
    test_ids = fields.One2many('hospital.lab.test.requisition.line', 'requisition_id', string='Tests')
    clinical_history = fields.Text(string='Clinical History')
    diagnosis = fields.Text(string='Provisional Diagnosis')
    urgency = fields.Selection([
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency')
    ], string='Urgency', default='routine', tracking=True)
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    admission_id = fields.Many2one('hospital.admission', string='Admission')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.lab.test.requisition') or 'New'
        return super(HospitalLabTestRequisition, self).create(vals)

class HospitalLabTestRequisitionLine(models.Model):
    _name = 'hospital.lab.test.requisition.line'
    _description = 'Laboratory Test Requisition Line'

    requisition_id = fields.Many2one('hospital.lab.test.requisition', string='Requisition')
    test_type = fields.Selection([
        ('biochemistry', 'Biochemistry'),
        ('hematology', 'Hematology'),
        ('hormones', 'Hormones'),
        ('immunology', 'Immunology'),
        ('microbiology', 'Microbiology'),
        ('molecular_biology', 'Molecular Biology'),
        ('urine_chemistry', 'Urine Chemistry'),
        ('urine_screening', 'Urine Screening'),
        ('drug_assays', 'Drug Assays'),
        ('other', 'Other')
    ], string='Test Type', required=True)
    specific_test = fields.Char(string='Specific Test')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='pending')