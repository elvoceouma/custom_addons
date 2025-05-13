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
    


from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

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
    gender = fields.Selection(related='ip_number.gender', string='Sex', readonly=True)
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

# Emergency Assessment Model
class HospitalEmergencyAssessment(models.Model):
    _name = 'hospital.emergency.assessment'
    _description = 'Hospital Emergency Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    date_time = fields.Datetime(string='Date & Time', default=fields.Datetime.now, required=True)
    chief_complaint = fields.Text(string='Chief Complaint')
    vital_signs = fields.Text(string='Vital Signs')
    mental_status = fields.Text(string='Mental Status')
    risk_assessment = fields.Text(string='Risk Assessment')
    physical_assessment = fields.Text(string='Physical Assessment')
    provisional_diagnosis = fields.Text(string='Provisional Diagnosis')
    immediate_plan = fields.Text(string='Immediate Plan')
    disposition = fields.Selection([
        ('admit', 'Admit'),
        ('refer', 'Refer'),
        ('discharge', 'Discharge'),
        ('observation', 'Observation'),
    ], string='Disposition')
    triage_level = fields.Selection([
        ('level_1', 'Level 1 - Resuscitation'),
        ('level_2', 'Level 2 - Emergency'),
        ('level_3', 'Level 3 - Urgent'),
        ('level_4', 'Level 4 - Semi-urgent'),
        ('level_5', 'Level 5 - Non-urgent'),
    ], string='Triage Level')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.emergency.assessment') or _('New')
        return super(HospitalEmergencyAssessment, self).create(vals_list)


# Incident Report Model
class HospitalIncidentReport(models.Model):
    _name = 'hospital.incident.report'
    _description = 'Hospital Incident Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    reporter_id = fields.Many2one('res.users', string='Reporter', default=lambda self: self.env.user.id)
    patient_id = fields.Many2one('hospital.patient', string='Patient Involved')
    staff_involved_ids = fields.Many2many('res.users', string='Staff Involved')
    date_time = fields.Datetime(string='Date & Time of Incident', default=fields.Datetime.now, required=True)
    location = fields.Char(string='Location of Incident')
    incident_type = fields.Selection([
        ('medication', 'Medication Error'),
        ('fall', 'Patient Fall'),
        ('equipment', 'Equipment Failure'),
        ('behavior', 'Behavioral Incident'),
        ('security', 'Security Incident'),
        ('other', 'Other'),
    ], string='Incident Type', required=True)
    description = fields.Text(string='Description of Incident', required=True)
    immediate_actions = fields.Text(string='Immediate Actions Taken')
    injuries = fields.Boolean(string='Were there injuries?')
    injury_description = fields.Text(string='Injury Description')
    witnesses_ids = fields.Many2many('res.users', 'incident_witnesses_rel', 'incident_id', 'user_id', string='Witnesses')
    severity = fields.Selection([
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], string='Severity')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('under_investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.incident.report') or _('New')
        return super(HospitalIncidentReport, self).create(vals_list)


# Capacity Assessment Model
class HospitalCapacityAssessment(models.Model):
    _name = 'hospital.capacity.assessment'
    _description = 'Hospital Capacity Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Assessing Physician', required=True)
    date = fields.Date(string='Assessment Date', default=fields.Date.context_today, required=True)
    decision_context = fields.Text(string='Decision Context', required=True)
    understand_information = fields.Boolean(string='Patient can understand relevant information')
    retain_information = fields.Boolean(string='Patient can retain the information')
    weigh_information = fields.Boolean(string='Patient can weigh information to make decision')
    communicate_decision = fields.Boolean(string='Patient can communicate their decision')
    assessment_details = fields.Text(string='Assessment Details')
    capacity_determination = fields.Selection([
        ('has_capacity', 'Has Capacity'),
        ('lacks_capacity', 'Lacks Capacity'),
        ('fluctuating', 'Fluctuating Capacity'),
    ], string='Capacity Determination', required=True)
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
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.capacity.assessment') or _('New')
        return super(HospitalCapacityAssessment, self).create(vals_list)


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


# Independent Examination Professional II Model
class HospitalIndependentExaminationProfessionalII(models.Model):
    _name = 'hospital.independent.examination.professional.ii'
    _description = 'Hospital Independent Examination Professional II'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    examiner_id = fields.Many2one('hospital.physician', string='Examining Professional', required=True)
    date = fields.Date(string='Examination Date', default=fields.Date.context_today, required=True)
    purpose = fields.Text(string='Purpose of Examination', required=True)
    previous_exam_id = fields.Many2one('hospital.independant.examination.professional.i', string='Previous Examination')
    agrees_with_previous = fields.Boolean(string='Agrees with Previous Assessment')
    disagreement_reasons = fields.Text(string='Reasons for Disagreement')
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
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.independent.examination.professional.ii') or _('New')
        return super(HospitalIndependentExaminationProfessionalII, self).create(vals_list)


# Discharge Clearance Checklist Model
class HospitalDischargeClearanceChecklist(models.Model):
    _name = 'hospital.discharge.clearance.checklist'
    _description = 'Hospital Discharge Clearance Checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                          default=lambda self: _('New'))
    

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
    
    name = fields.Char(string='Procedure Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Performing Physician')
    procedure_date = fields.Datetime(string='Procedure Date')
    procedure_type = fields.Char(string='Procedure Type')
    notes = fields.Text(string='Procedure Notes')
    complications = fields.Text(string='Complications')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='planned')

class HospitalMedicineRequisition(models.Model):
    _name = 'hospital.medicine.requisition'
    _description = 'Medicine Requisition'
    
    name = fields.Char(string='Requisition Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    date = fields.Date(string='Date', default=fields.Date.today)
    medicine_lines = fields.One2many('hospital.medicine.requisition.line', 'requisition_id', string='Medicines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('dispensed', 'Dispensed')
    ], string='Status', default='draft')

class HospitalMedicineRequisitionLine(models.Model):
    _name = 'hospital.medicine.requisition.line'
    _description = 'Medicine Requisition Line'
    
    requisition_id = fields.Many2one('hospital.medicine.requisition', string='Requisition')
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine')
    quantity = fields.Float(string='Quantity')
    dosage = fields.Char(string='Dosage')
    frequency = fields.Char(string='Frequency')
    duration = fields.Integer(string='Duration (days)')

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
    
    name = fields.Char(string='Admission Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    guardian_id = fields.Many2one('hospital.patient.relationship', string='Guardian')
    admission_date = fields.Date(string='Admission Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Admitting Physician')
    reason = fields.Text(string='Reason for Admission')
    guardian_consent = fields.Boolean(string='Guardian Consent Obtained')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged')
    ], string='Status', default='draft')

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
    
    name = fields.Char(string='Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    date = fields.Date(string='Date', default=fields.Date.today)
    assessment = fields.Text(string='Assessment')
    recommendations = fields.Text(string='Recommendations')
    notes = fields.Text(string='Notes')

class HospitalOutingExpenses(models.Model):
    _name = 'hospital.outing.expenses'
    _description = 'Outing Expenses'
    
    name = fields.Char(string='Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    purpose = fields.Char(string='Purpose')
    amount = fields.Float(string='Amount')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid')
    ], string='Status', default='draft')

class HospitalOutingForm(models.Model):
    _name = 'hospital.outing.form'
    _description = 'Outing Form'
    
    name = fields.Char(string='Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    purpose = fields.Text(string='Purpose')
    accompanied_by = fields.Char(string='Accompanied By')
    approval_physician_id = fields.Many2one('hospital.physician', string='Approving Physician')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

class HospitalPatientRequisition(models.Model):
    _name = 'hospital.patient.requisition'
    _description = 'Patient Requisition'
    
    name = fields.Char(string='Requisition Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    date = fields.Date(string='Date', default=fields.Date.today)
    items = fields.Text(string='Requisition Items')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

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

class HospitalProvisionalBill(models.Model):
    _name = 'hospital.provisional.bill'
    _description = 'Provisional Bill'
    
    name = fields.Char(string='Bill Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.today)
    amount = fields.Float(string='Amount')
    details = fields.Text(string='Bill Details')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid')
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')


class HospitalRoomInspection(models.Model):
    _name = 'hospital.room.inspection'
    _description = 'Room Inspection'
    
    name = fields.Char(string='Inspection Reference', required=True)
    room_id = fields.Many2one('hospital.room', string='Room', required=True)
    inspector_id = fields.Many2one('res.users', string='Inspector')
    inspection_date = fields.Datetime(string='Inspection Date', default=fields.Datetime.now)
    cleanliness = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Cleanliness')
    maintenance_required = fields.Boolean(string='Maintenance Required')
    maintenance_notes = fields.Text(string='Maintenance Notes')
    action_taken = fields.Text(string='Action Taken')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inspected', 'Inspected'),
        ('maintenance', 'Under Maintenance'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

class HospitalServiceRequisition(models.Model):
    _name = 'hospital.service.requisition'
    _description = 'Service Requisition'
    
    name = fields.Char(string='Requisition Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    service_date = fields.Date(string='Service Date', default=fields.Date.today)
    service_type = fields.Char(string='Service Type')
    description = fields.Text(string='Service Description')
    urgency = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency')
    ], string='Urgency')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

class HospitalSpecialPrivileges(models.Model):
    _name = 'hospital.special.privileges'
    _description = 'Special Privileges'
    
    name = fields.Char(string='Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    privilege_type = fields.Char(string='Privilege Type')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    approved_by = fields.Many2one('res.users', string='Approved By')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('expired', 'Expired')
    ], string='Status', default='draft')

class HospitalStoreClearance(models.Model):
    _name = 'hospital.store.clearance'
    _description = 'Store Clearance'
    
    name = fields.Char(string='Clearance Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    clearance_date = fields.Date(string='Clearance Date', default=fields.Date.today)
    cleared_by = fields.Many2one('res.users', string='Cleared By')
    items_returned = fields.Boolean(string='All Items Returned')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('cleared', 'Cleared'),
        ('not_cleared', 'Not Cleared')
    ], string='Status', default='draft')

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
    
    name = fields.Char(string='Bill Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    billing_date = fields.Date(string='Billing Date', default=fields.Date.today)
    service_description = fields.Text(string='Service Description')
    amount = fields.Float(string='Amount')
    approved_by = fields.Many2one('res.users', string='Approved By')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('billed', 'Billed')
    ], string='Status', default='draft')


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


class HospitalBillEstimation(models.Model):
    _name = 'hospital.bill.estimation'
    _description = 'Hospital Bill Estimation'
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.today)
    estimated_amount = fields.Float(string='Estimated Amount')
    actual_amount = fields.Float(string='Actual Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft')

class HospitalBiochemistry(models.Model):
    _name = 'hospital.biochemistry'
    _description = 'Biochemistry Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalCaretakerAllotment(models.Model):
    _name = 'hospital.caretaker.allotment'
    _description = 'Caretaker Allotment'
    
    name = fields.Char(string='Allotment Reference', required=True)
    caretaker_id = fields.Many2one('hospital.caretaker', string='Caretaker', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed')
    ], string='Status', default='draft')


class HospitalCaretaker(models.Model):
    _name = 'hospital.caretaker'
    _description = 'Hospital Caretakers'
    
    name = fields.Char(string='Caretaker Name', required=True)
    registration_number = fields.Char(string='Registration Number')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    active = fields.Boolean(string='Active', default=True)

class HospitalCounsellorClearance(models.Model):
    _name = 'hospital.counsellor.clearance'
    _description = 'Counsellor Clearance'
    
    name = fields.Char(string='Clearance Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    counsellor_id = fields.Many2one('hospital.physician', string='Counsellor')
    clearance_date = fields.Date(string='Clearance Date', default=fields.Date.today)
    is_cleared = fields.Boolean(string='Is Cleared')
    notes = fields.Text(string='Notes')


from odoo import models, fields, api
from datetime import datetime

class HospitalBillEstimation(models.Model):
    _name = 'hospital.bill.estimation'
    _description = 'Hospital Bill Estimation'
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.today)
    estimated_amount = fields.Float(string='Estimated Amount')
    actual_amount = fields.Float(string='Actual Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft')

class HospitalBiochemistry(models.Model):
    _name = 'hospital.biochemistry'
    _description = 'Biochemistry Tests'
    
    name = fields.Char(string='Test Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    test_date = fields.Date(string='Test Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    result = fields.Text(string='Test Results')
    notes = fields.Text(string='Notes')

class HospitalCapacityAssessment(models.Model):
    _name = 'hospital.capacity.assessment'
    _description = 'Patient Capacity Assessment'
    
    name = fields.Char(string='Assessment Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    assessment_date = fields.Date(string='Assessment Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Assessing Physician')
    mental_capacity = fields.Selection([
        ('full', 'Full Capacity'),
        ('partial', 'Partial Capacity'),
        ('none', 'No Capacity')
    ], string='Mental Capacity Status')
    assessment_notes = fields.Text(string='Assessment Notes')

class HospitalCaretaker(models.Model):
    _name = 'hospital.caretaker'
    _description = 'Hospital Caretakers'
    
    name = fields.Char(string='Caretaker Name', required=True)
    registration_number = fields.Char(string='Registration Number')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    active = fields.Boolean(string='Active', default=True)

class HospitalCaretakerAllotment(models.Model):
    _name = 'hospital.caretaker.allotment'
    _description = 'Caretaker Allotment'
    
    name = fields.Char(string='Allotment Reference', required=True)
    caretaker_id = fields.Many2one('hospital.caretaker', string='Caretaker', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed')
    ], string='Status', default='draft')


class HospitalCounsellorClearance(models.Model):
    _name = 'hospital.counsellor.clearance'
    _description = 'Counsellor Clearance'
    
    name = fields.Char(string='Clearance Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    counsellor_id = fields.Many2one('hospital.physician', string='Counsellor')
    clearance_date = fields.Date(string='Clearance Date', default=fields.Date.today)
    is_cleared = fields.Boolean(string='Is Cleared')
    notes = fields.Text(string='Notes')

class HospitalDAMAForm(models.Model):
    _name = 'hospital.dama.form'
    _description = 'Discharge Against Medical Advice Form'
    
    name = fields.Char(string='DAMA Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    physician_id = fields.Many2one('hospital.physician', string='Treating Physician')
    date = fields.Date(string='Date', default=fields.Date.today)
    reason = fields.Text(string='Reason for DAMA')
    risk_explained = fields.Boolean(string='Risks Explained')
    witness_name = fields.Char(string='Witness Name')
    witness_signature = fields.Binary(string='Witness Signature')
    patient_signature = fields.Binary(string='Patient Signature')

class HospitalDischargeClearance(models.Model):
    _name = 'hospital.discharge.clearance'
    _description = 'Discharge Clearance Checklist'
    
    name = fields.Char(string='Clearance Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.today)
    medication_reconciliation = fields.Boolean(string='Medication Reconciliation')
    follow_up_scheduled = fields.Boolean(string='Follow-up Scheduled')
    documentation_complete = fields.Boolean(string='Documentation Complete')
    patient_educated = fields.Boolean(string='Patient Educated')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

class HospitalDoctorPayout(models.Model):
    _name = 'hospital.doctor.payout'
    _description = 'Doctor Payout'
    
    name = fields.Char(string='Payout Reference', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    period_start = fields.Date(string='Period Start', required=True)
    period_end = fields.Date(string='Period End', required=True)
    amount = fields.Float(string='Payout Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('paid', 'Paid')
    ], string='Status', default='draft')


class HospitalEmergencyAssessment(models.Model):
    _name = 'hospital.emergency.assessment'
    _description = 'Emergency Assessment'
    
    name = fields.Char(string='Assessment Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Assessing Physician')
    assessment_date = fields.Datetime(string='Assessment Date', default=fields.Datetime.now)
    chief_complaint = fields.Text(string='Chief Complaint')
    vital_signs = fields.Text(string='Vital Signs')
    assessment = fields.Text(string='Assessment')
    plan = fields.Text(string='Plan')
    disposition = fields.Selection([
        ('admit', 'Admit'),
        ('discharge', 'Discharge'),
        ('transfer', 'Transfer')
    ], string='Disposition')

class HospitalEmergencyMedicine(models.Model):
    _name = 'hospital.emergency.medicine'
    _description = 'Emergency Medicine'
    
    name = fields.Char(string='Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Prescribing Physician')
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine')
    dosage = fields.Char(string='Dosage')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    reason = fields.Text(string='Reason')
    administered = fields.Boolean(string='Administered')
    administered_by = fields.Many2one('res.users', string='Administered By')


class HospitalFormCSection86(models.Model):
    _name = 'hospital.form.c.section.86'
    _description = 'Form C Section 86'
    
    name = fields.Char(string='Form Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date = fields.Date(string='Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    diagnosis = fields.Text(string='Diagnosis')
    recommendations = fields.Text(string='Recommendations')
    notes = fields.Text(string='Notes')

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
    
    name = fields.Char(string='Admission Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_date = fields.Date(string='Admission Date', default=fields.Date.today)
    physician_id = fields.Many2one('hospital.physician', string='Admitting Physician')
    reason = fields.Text(string='Reason for High Support')
    care_plan = fields.Text(string='Care Plan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged')
    ], string='Status', default='draft')

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

class HospitalIncidentReport(models.Model):
    _name = 'hospital.incident.report'
    _description = 'Incident Report'
    
    name = fields.Char(string='Report Reference', required=True)
    date = fields.Datetime(string='Incident Date', default=fields.Datetime.now)
    location = fields.Char(string='Location')
    reported_by = fields.Many2one('res.users', string='Reported By')
    incident_type = fields.Selection([
        ('patient', 'Patient Related'),
        ('staff', 'Staff Related'),
        ('facility', 'Facility Related'),
        ('other', 'Other')
    ], string='Incident Type')
    description = fields.Text(string='Description')
    action_taken = fields.Text(string='Action Taken')
    witnesses = fields.Text(string='Witnesses')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reported', 'Reported'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved')
    ], string='Status', default='draft')

class HospitalIndependentExamination(models.Model):
    _name = 'hospital.independent.examination'
    _description = 'Independent Medical Examination'
    
    name = fields.Char(string='Examination Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Examining Physician')
    examination_date = fields.Date(string='Examination Date', default=fields.Date.today)
    examination_type = fields.Selection([
        ('professional_1', 'Professional I'),
        ('professional_2', 'Professional II')
    ], string='Examination Type')
    findings = fields.Text(string='Findings')
    recommendations = fields.Text(string='Recommendations')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed')
    ], string='Status', default='draft')

class HospitalInvestigationRequest(models.Model):
    _name = 'hospital.investigation.request'
    _description = 'Investigation Request'
    
    name = fields.Char(string='Request Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Requesting Physician')
    request_date = fields.Date(string='Request Date', default=fields.Date.today)
    investigation_type = fields.Selection([
        ('lab', 'Laboratory'),
        ('radiology', 'Radiology'),
        ('other', 'Other')
    ], string='Investigation Type')
    urgency = fields.Selection([
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency')
    ], string='Urgency')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft')

class HospitalLAMAForm(models.Model):
    _name = 'hospital.lama.form'
    _description = 'Leave Against Medical Advice Form'
    
    name = fields.Char(string='LAMA Reference', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    physician_id = fields.Many2one('hospital.physician', string='Treating Physician')
    date = fields.Date(string='Date', default=fields.Date.today)
    reason = fields.Text(string='Reason for LAMA')
    risk_explained = fields.Boolean(string='Risks Explained')
    witness_name = fields.Char(string='Witness Name')
    witness_signature = fields.Binary(string='Witness Signature')
    patient_signature = fields.Binary(string='Patient Signature')


from odoo import models, fields, api
from datetime import datetime

# class HospitalLabTest(models.Model):
#     _name = 'hospital.lab.test'
#     _description = 'Laboratory Test'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'id desc'

#     name = fields.Char(string='Test Reference', required=True, copy=False, readonly=True, default='New')
#     patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
#     physician_id = fields.Many2one('hospital.physician', string='Requesting Physician', tracking=True)
#     test_date = fields.Date(string='Test Date', default=fields.Date.today, tracking=True)
#     test_type = fields.Selection([
#         ('biochemistry', 'Biochemistry'),
#         ('hematology', 'Hematology'),
#         ('hormones', 'Hormones'),
#         ('immunology', 'Immunology'),
#         ('microbiology', 'Microbiology'),
#         ('molecular_biology', 'Molecular Biology'),
#         ('urine_chemistry', 'Urine Chemistry'),
#         ('urine_screening', 'Urine Screening'),
#         ('drug_assays', 'Drug Assays'),
#         ('other', 'Other')
#     ], string='Test Type', required=True, tracking=True)
#     urgency = fields.Selection([
#         ('routine', 'Routine'),
#         ('urgent', 'Urgent'),
#         ('emergency', 'Emergency')
#     ], string='Urgency', default='routine', tracking=True)
#     sample_type = fields.Selection([
#         ('blood', 'Blood'),
#         ('urine', 'Urine'),
#         ('stool', 'Stool'),
#         ('csf', 'CSF'),
#         ('tissue', 'Tissue'),
#         ('other', 'Other')
#     ], string='Sample Type', tracking=True)
#     sample_collection_date = fields.Datetime(string='Sample Collection Date', tracking=True)
#     collected_by = fields.Many2one('res.users', string='Collected By', tracking=True)
#     results = fields.Text(string='Test Results', tracking=True)
#     normal_range = fields.Text(string='Normal Range')
#     interpretation = fields.Text(string='Interpretation', tracking=True)
#     notes = fields.Text(string='Notes')
#     attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('sample_collected', 'Sample Collected'),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled')
#     ], string='Status', default='draft', tracking=True)
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
#     admission_id = fields.Many2one('hospital.admission', string='Admission')
#     requisition_id = fields.Many2one('hospital.lab.test.requisition', string='Requisition')

    # @api.model
    # def create(self, vals):
    #     if vals.get('name', 'New') == 'New':
    #         vals['name'] = self.env['ir.sequence'].next_by_code('hospital.lab.test') or 'New'
    #     return super(HospitalLabTest, self).create(vals)

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