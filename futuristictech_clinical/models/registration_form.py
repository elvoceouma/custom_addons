# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RegistrationForm(models.Model):
    _name = 'hospital.registration.form'
    _description = 'Patient Registration Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'lead_reference_no'
    
    # CRM References
    lead_reference_no = fields.Char(string='Lead Reference No.', required=True, tracking=True)
    lead_id = fields.Char(string='Lead ID')
    visit_id = fields.Char(string='Visit ID')
    registration_id = fields.Char(string='Registration ID')
    date = fields.Date(string='Registration Date', default=fields.Date.context_today, tracking=True)
    reference = fields.Char(string='Reference')
    # Campus Information
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    
    # Patient Information
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    
    # Nominee Information
    nominee_name = fields.Char(string='Nominee Name')
    nominee_age = fields.Integer(string='Nominee Age')
    nominee_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Nominee Sex')
    nominee_relationship = fields.Selection([
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('friend', 'Friend'),
        ('other', 'Other')
    ], string='Nominee Relationship with Patient')
    nominee_mobile = fields.Char(string='Nominee Mobile')
    nominee_email = fields.Char(string='Nominee Email')
    nominee_address = fields.Char(string='Nominee Address')
    nominee_street2 = fields.Char(string='Nominee Street 2')
    nominee_city = fields.Char(string='Nominee City')
    nominee_state = fields.Char(string='Nominee State')
    nominee_zip = fields.Char(string='Nominee ZIP')
    nominee_country = fields.Char(string='Nominee Country')
    
    # Visitor Information
    visitor_name = fields.Char(string='Visitor Name')
    visitor_age = fields.Integer(string='Visitor Age')
    visitor_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Visitor Sex')
    visitor_relationship = fields.Selection([
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('friend', 'Friend'),
        ('other', 'Other')
    ], string='Visitor Relationship with Patient')
    visitor_mobile = fields.Char(string='Visitor Mobile')
    visitor_email = fields.Char(string='Visitor Email')
    visitor_address = fields.Char(string='Visitor Address')
    visitor_street2 = fields.Char(string='Visitor Street 2')
    visitor_city = fields.Char(string='Visitor City')
    visitor_state = fields.Char(string='Visitor State')
    visitor_zip = fields.Char(string='Visitor ZIP')
    visitor_country = fields.Char(string='Visitor Country')
    
    # Services
    services_looking_for = fields.Selection([
        ('counselling', 'Counselling'),
        ('psychiatry', 'Psychiatry'),
        ('psychology', 'Psychology'),
        ('therapy', 'Therapy'),
        ('rehabilitation', 'Rehabilitation'),
        ('other', 'Other')
    ], string='Services Looking for')
    de_addiction = fields.Selection([
        ('alcohol', 'Alcohol'),
        ('drugs', 'Drugs'),
        ('smoking', 'Smoking'),
        ('gambling', 'Gambling'),
        ('other', 'Other')
    ], string='De Addiction')
    mental_illness = fields.Selection([
        ('depression', 'Depression'),
        ('anxiety', 'Anxiety'),
        ('bipolar', 'Bipolar Disorder'),
        ('schizophrenia', 'Schizophrenia'),
        ('other', 'Other')
    ], string='Mental Illness')
    mental_retardation = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('profound', 'Profound')
    ], string='Mental Retardation')
    old_age_psychiatric_problem = fields.Selection([
        ('dementia', 'Dementia'),
        ('alzheimers', 'Alzheimer\'s'),
        ('parkinsons', 'Parkinson\'s'),
        ('other', 'Other')
    ], string='Old Age Psychiatric Problem')
    
    # Patient Details
    patient_first_name = fields.Char(string='Patient First Name')
    patient_last_name = fields.Char(string='Patient Last Name')
    dob = fields.Date(string='DOB')
    patient_age = fields.Integer(string='Patient Age')
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Patient Sex')
    patient_address = fields.Char(string='Patient Address')
    patient_street2 = fields.Char(string='Patient Street 2')
    patient_city = fields.Char(string='Patient City')
    patient_state = fields.Char(string='Patient State')
    patient_zip = fields.Char(string='Patient ZIP')
    patient_country = fields.Char(string='Patient Country')
    landline_number = fields.Char(string='Landline Number')
    patient_mobile = fields.Char(string='Patient Mobile')
    patient_email = fields.Char(string='Patient Email')
    nationality = fields.Char(string='Nationality')
    education_qualification = fields.Selection([
        ('primary', 'Primary Education'),
        ('secondary', 'Secondary Education'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
        ('other', 'Other')
    ], string='Education Qualification')
    occupation = fields.Char(string='Occupation')
    religion = fields.Selection([
        ('hinduism', 'Hinduism'),
        ('islam', 'Islam'),
        ('christianity', 'Christianity'),
        ('sikhism', 'Sikhism'),
        ('buddhism', 'Buddhism'),
        ('jainism', 'Jainism'),
        ('other', 'Other')
    ], string='Religion')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated')
    ], string='Marital Status')
    languages_known = fields.Many2many('res.lang', string='Languages Known')
    has_children = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Do you have Children')
    children_count = fields.Integer(string='Number of Children')
    concerns_problems = fields.Text(string='Concerns/Problems')
    physical_condition = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor')
    ], string='Physical Condition')
    
    # CRM Remarks
    crm_remarks_ids = fields.One2many('hospital.registration.crm.remarks', 'registration_id', string='CRM Remarks')
    
    # Emergency Contact Information
    emergency_person_name = fields.Char(string='Emergency Person Name')
    emergency_person_mobile = fields.Char(string='Emergency Person Mobile')
    emergency_person_email = fields.Char(string='Emergency Person Email')
    emergency_person_relationship = fields.Selection([
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('friend', 'Friend'),
        ('other', 'Other')
    ], string='Emergency Person Relationship with Patient')
    
    # Consultant Information
    has_consulted_before = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Have you consulted any other psycologist / psychiatrist / counsellor')
    whom_to_meet = fields.Selection([
        ('psychologist', 'Psychologist'),
        ('psychiatrist', 'Psychiatrist'),
        ('any_one', 'Any one'),
        ('both', 'Both'),
        ('dont_know', 'I don\'t know whom to meet')
    ], string='Whom do you want to meet?')
    previous_consultant_name = fields.Char(string='Previous Consultant Name')
    how_known_about_us = fields.Selection([
        ('friend', 'Friend'),
        ('relative', 'Relative'),
        ('internet', 'Internet'),
        ('newspaper', 'Newspaper'),
        ('doctor', 'Doctor'),
        ('other', 'Other')
    ], string='How did you get to know about us')
    
    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('admitted', 'Admitted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('lead_reference_no'):
            vals['lead_reference_no'] = self.env['ir.sequence'].next_by_code('hospital.registration.form.lead.ref') or 'New'
        return super(RegistrationForm, self).create(vals)
    
    def action_register(self):
        """Action to register the patient"""
        self.state = 'registered'
        # Additional logic for registration can be added here

    def action_cancel(self):
        """Action to cancel the registration"""
        self.state = 'cancelled'
        # Additional logic for cancellation can be added here

class HospitalRegistrationCRMRemarks(models.Model):
    _name = 'hospital.registration.crm.remarks'
    _description = 'Registration CRM Remarks'
    
    registration_id = fields.Many2one('hospital.registration.form', string='Registration', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    points_of_discussion = fields.Text(string='Points of Discussion')
    remarks = fields.Text(string='Remarks')
    employee_id = fields.Many2one('hr.employee', string='Employee')




class HospitalRegistrationDetilsService(models.Model):
    _name = 'hospital.registration.details.service'
    _description = 'Hospital Registration Details Service'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    service_id = fields.Many2one('hospital.service', string='Service', required=True)
    service_date = fields.Date(string='Service Date', default=fields.Date.context_today)
    service_time = fields.Datetime(string='Service Time')
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')    

class HospitalRegistrationDetailsLanguage(models.Model):
    _name = 'hospital.registration.details.language'
    _description = 'Hospital Registration Details Language'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    language_id = fields.Many2one('res.lang', string='Language', required=True)
    proficiency_level = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], string='Proficiency Level')


class HospitalRegistrationDetailsRelationship(models.Model):
    _name = 'hospital.registration.details.relationship'
    _description = 'Hospital Registration Details Relationship'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    relationship_id = fields.Many2one('hospital.patient.relationship', string='Relationship', required=True)
    name = fields.Char(string='Name')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    # Add any additional fields as 
    
class HospitalRegistrationDetailsPhysicalHelthCondition(models.Model):
    _name = 'hospital.registration.details.physical.health.condition'
    _description = 'Hospital Registration Details Physical Health Condition'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    condition_id = fields.Many2one('hospital.physical.health.condition', string='Condition', required=True)
    severity_level = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Severity Level')
    notes = fields.Text(string='Notes')

class HospitalRegistrationDetailsServiceList(models.Model):
    _name = 'hospital.registration.details.service.list'
    _description = 'Hospital Registration Details Service List'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    service_id = fields.Many2one('hospital.service', string='Service', required=True)
    service_date = fields.Date(string='Service Date', default=fields.Date.context_today)
    service_time = fields.Datetime(string='Service Time')
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')


class  HospitalRegistrationDetailsAssessment(models.Model):
    _name = 'hospital.registration.details.risk.assessment'
    _description = 'Hospital Registration Details Assessment'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    assessment_type_id = fields.Many2one('hospital.assessment.type', string='Assessment Type', required=True)
    assessment_date = fields.Date(string='Assessment Date', default=fields.Date.context_today)
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    notes = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')



class HospitalRegistrationDetailsPsychomotorActivity(models.Model):
    _name = 'hospital.registration.details.psychomotor.activity'
    _description = 'Hospital Registration Details Psychomotor Activity'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    activity_type = fields.Selection([
        ('agitation', 'Agitation'),
        ('retardation', 'Retardation'),
        ('normal', 'Normal Activity')
    ], string='Activity Type', required=True)
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'), 
        ('severe', 'Severe')
    ], string='Severity')
    observation_date = fields.Date(string='Observation Date', default=fields.Date.context_today)
    observer_id = fields.Many2one('res.partner', string='Observer', domain=[('is_physician', '=', True)])
    notes = fields.Text(string='Observation Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')



class HospitalRegistrationDetailsCatatonicSign(models.Model):
    _name = 'hospital.registration.details.catatonic.sign'
    _description = 'Hospital Registration Details Catatonic Sign'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    sign_type = fields.Selection([
        ('stupor', 'Stupor'),
        ('rigidity', 'Rigidity'),
        ('posturing', 'Posturing'),
        ('negativism', 'Negativism'),
        ('waxy_flexibility', 'Waxy Flexibility'),
        ('mutism', 'Mutism'),
        ('echolalia', 'Echolalia'),
        ('stereotypy', 'Stereotypy')
    ], string='Sign Type', required=True)
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Severity')
    observation_date = fields.Date(string='Observation Date', default=fields.Date.context_today)
    observer_id = fields.Many2one('res.partner', string='Observer', domain=[('is_physician', '=', True)])
    notes = fields.Text(string='Clinical Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

class HospitalRegistrationDetailsPhysicalIllness(models.Model):
    _name = 'hospital.registration.details.physical.illness'
    _description = 'Hospital Registration Details Physical Illness'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    illness_id = fields.Many2one('hospital.physical.illness', string='Physical Illness', required=True)
    diagnosis_date = fields.Date(string='Diagnosis Date', default=fields.Date.context_today)
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Severity')
    diagnosed_by = fields.Many2one('res.partner', string='Diagnosed By', domain=[('is_physician', '=', True)])
    treatment_status = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued')
    ], string='Treatment Status')
    notes = fields.Text(string='Clinical Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')


class HospitalRegistrationDetailsPsychiatricIllness(models.Model):
    _name = 'hospital.registration.details.physiatric.illness'
    _description = 'Hospital Registration Details Psychiatric Illness'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    illness_id = fields.Many2one('hospital.psychiatric.illness', string='Psychiatric Illness', required=True)
    diagnosis_date = fields.Date(string='Diagnosis Date', default=fields.Date.context_today)
    severity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Severity')
    diagnosed_by = fields.Many2one('res.partner', string='Diagnosed By', domain=[('is_physician', '=', True)])
    treatment_status = fields.Selection([
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued')
    ], string='Treatment Status')
    notes = fields.Text(string='Clinical Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')


class HospitalRegistrationDetailsSource(models.Model):
    _name = 'hospital.registration.details.source'
    _description = 'Hospital Registration Details Source'
    
    registration_form_id = fields.Many2one('hospital.registration.form', string='Registration Form', required=True, ondelete='cascade')
    source_type = fields.Selection([
        ('referral', 'Professional Referral'),
        ('self', 'Self Referral'),
        ('emergency', 'Emergency Services'),
        ('transfer', 'Hospital Transfer'),
        ('other', 'Other')
    ], string='Source Type', required=True)
    referrer_name = fields.Char(string='Referrer Name')
    referrer_organization = fields.Char(string='Referring Organization')
    referral_date = fields.Date(string='Referral Date', default=fields.Date.context_today)
    notes = fields.Text(string='Additional Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
