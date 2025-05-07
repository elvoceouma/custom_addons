# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RegistrationForm(models.Model):
    _name = 'hospital.registration.form'
    _description = 'Patient Registration Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'
    
    reference = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Registration Date', default=fields.Date.context_today, tracking=True)
    
    # Patient Information
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    name = fields.Char(string='Patient Name', related='patient_id.name', store=True, readonly=False)
    gender = fields.Selection(related='patient_id.gender', readonly=False, store=True)
    age = fields.Integer(string='Age', related='patient_id.age', readonly=False, store=True)
    dob = fields.Date(string='Date of Birth', related='patient_id.dob', readonly=False, store=True)
    blood_group = fields.Selection(related='patient_id.blood_group', readonly=False, store=True)
    mobile = fields.Char(string='Mobile', related='patient_id.mobile', readonly=False, store=True)
    email = fields.Char(string='Email', related='patient_id.email', readonly=False, store=True)
    address = fields.Text(string='Address', readonly=False, store=True)
    
    # Emergency Contact Information
    emergency_contact = fields.Char(string='Emergency Contact')
    emergency_relation = fields.Many2one('hospital.patient.relationship', string='Relationship')
    emergency_phone = fields.Char(string='Emergency Phone')
    
    # Insurance Information
    insurance_provider = fields.Many2one('hospital.insurance', string='Insurance Provider')
    policy_number = fields.Char(string='Policy Number')
    policy_holder = fields.Char(string='Policy Holder')
    
    # Medical Information
    illness_tag_ids = fields.Many2many('hospital.illness.tag', string='Illness Tags', related='patient_id.illness_tag_ids', readonly=False)
    allergies = fields.Text(string='Allergies')
    current_medications = fields.Text(string='Current Medications')
    pre_existing_conditions = fields.Text(string='Pre-existing Conditions')
    family_history = fields.Text(string='Family History')
    
    # Registration Type
    registration_type = fields.Selection([
        ('op', 'Outpatient'),
        ('ip', 'Inpatient'),
        ('emergency', 'Emergency')
    ], string='Registration Type', default='op', required=True, tracking=True)
    
    # Campus/Location Information
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    
    # For Inpatient Registrations
    is_admission_needed = fields.Boolean(string='Is Admission Needed')
    admission_date = fields.Datetime(string='Admission Date')
    block_id = fields.Many2one('hospital.block', string='Block')
    room_id = fields.Many2one('hospital.room', string='Room')
    bed_id = fields.Many2one('hospital.bed', string='Bed')
    
    # Physician Information
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    referral_source = fields.Char(string='Referral Source')
    
    # Document Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Documents')
    
    # Status and Agreement
    consent_signed = fields.Boolean(string='Consent Form Signed')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('registered', 'Registered'),
        ('admitted', 'Admitted'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Additional Fields
    notes = fields.Text(string='Notes')
    
    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.registration.form') or _('New')
        
        # If patient_id not provided, create a new patient record
        if not vals.get('patient_id') and vals.get('name'):
            patient_vals = {
                'name': vals.get('name'),
                'gender': vals.get('gender'),
                'age': vals.get('age'),
                'dob': vals.get('dob'),
                'blood_group': vals.get('blood_group'),
                'mobile': vals.get('mobile'),
                'email': vals.get('email'),
                'address': vals.get('address'),
            }
            patient = self.env['hospital.patient'].create(patient_vals)
            vals['patient_id'] = patient.id
            
        return super(RegistrationForm, self).create(vals)
    
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            # Load patient data into the form
            self.gender = self.patient_id.gender
            self.age = self.patient_id.age
            self.dob = self.patient_id.dob
            self.blood_group = self.patient_id.blood_group
            self.mobile = self.patient_id.mobile
            self.email = self.patient_id.email
            self.address = self.patient_id.address
            self.illness_tag_ids = self.patient_id.illness_tag_ids
    
    @api.onchange('campus_id')
    def _onchange_campus_id(self):
        if self.campus_id:
            # Reset block, room and bed when campus changes
            self.block_id = False
            self.room_id = False
            self.bed_id = False
            
    @api.onchange('block_id')
    def _onchange_block_id(self):
        if self.block_id:
            # Filter rooms based on selected block
            self.room_id = False
            self.bed_id = False
            
    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            # Filter beds based on selected room
            self.bed_id = False
    
    def action_register(self):
        self.ensure_one()
        self.state = 'registered'
        
        # If admission is needed, create an admission record
        if self.is_admission_needed and self.registration_type == 'ip':
            admission_vals = {
                'patient_id': self.patient_id.id,
                'campus_id': self.campus_id.id,
                'block_id': self.block_id.id,
                'room_id': self.room_id.id,
                'bed_id': self.bed_id.id,
                'admission_date': self.admission_date or fields.Datetime.now(),
                'physician_id': self.physician_id.id,
                'state': 'draft',
            }
            
            admission = self.env['hospital.admission'].create(admission_vals)
            # Link the admission to this registration
            self.write({
                'state': 'admitted',
            })
            
            # Return action to view the created admission
            return {
                'type': 'ir.actions.act_window',
                'name': _('Admission'),
                'res_model': 'hospital.admission',
                'view_mode': 'form',
                'res_id': admission.id,
                'target': 'current',
            }
            
        return True
    
    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        return True
    
    def action_draft(self):
        self.ensure_one()
        self.state = 'draft'
        return True
    

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

