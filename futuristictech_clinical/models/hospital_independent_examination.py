from odoo import api, fields, models, _


class HospitalIndependentExamination(models.Model):
    _name = 'hospital.independent.examination'
    _description = 'Independent Medical Examination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Examination Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    name_seq = fields.Char(string='Sequence', required=True, copy=False, readonly=True,
                          default=lambda self: _('New'))
    
    # Patient Information
    ip_number = fields.Many2one('hospital.patient', string='IP Number', required=True, tracking=True)
    patient_name = fields.Char(string='Patient Name', related='ip_number.name', readonly=True)
    mrn_no = fields.Char(string='MRN No', readonly=True)
    age = fields.Integer(string='Age', related='ip_number.age', readonly=True)
    gender = fields.Selection(related='ip_number.gender', string='Sex', readonly=True)
    
    # Examination Details
    date = fields.Date(string='Examination Date', default=fields.Date.context_today, required=True, tracking=True)
    examination_type = fields.Selection([
        ('professional_1', 'Professional I'),
        ('professional_2', 'Professional II')
    ], string='Examination Type', default='professional_1', tracking=True)
    
    # One2many fields
    professional_line_ids = fields.One2many('hospital.independent.examination.professional', 
                                           'examination_id', string='Professional Lines')
    examination_category_id = fields.One2many('hospital.independent.examination.category', 
                                             'examination_id', string='Examination Categories')
    examination_document_ids = fields.One2many('hospital.independent.examination.document', 
                                              'examination_id', string='Examination Documents')
    examination_capacity_ids = fields.One2many('hospital.independent.examination.capacity', 
                                              'examination_id', string='Capacity Assessments')
    examintation_mental_health = fields.One2many('hospital.independent.examination.mental.health', 
                                                'examination_id', string='Mental Health Board')
    examination_details_ids = fields.One2many('hospital.independent.examination.scales', 
                                             'examination_id', string='Examination Details')
    
    # Diagnosis and Symptoms
    provisional_diagnosis = fields.Text(string='Provisional Diagnosis', tracking=True)
    severity_symptoms = fields.Text(string='Severity of Symptoms', tracking=True)
    
    # Reasons for Admission
    recently_threatened = fields.Boolean(string='Recently Threatened', tracking=True)
    recently_behaved = fields.Boolean(string='Recently Behaved Violently', tracking=True)
    inability = fields.Boolean(string='Inability to Look After Self', tracking=True)
    nature_purpose = fields.Text(string='Nature & Purpose of Treatment', tracking=True)
    
    # Additional Notes
    additional_notes = fields.Text(string='Additional Notes', tracking=True)
    
    # Care Plan
    diagnostics = fields.Boolean(string='Diagnostics', tracking=True)
    symptom = fields.Boolean(string='Symptom Management', tracking=True)
    psychopharmacological = fields.Boolean(string='Psychopharmacological Treatment', tracking=True)
    observation = fields.Boolean(string='Observation', tracking=True)
    psycho_social = fields.Boolean(string='Psycho-Social Interventions', tracking=True)
    rehabilitation = fields.Boolean(string='Rehabilitation', tracking=True)
    risk_harm = fields.Boolean(string='Risk/Harm Management', tracking=True)
    crisis = fields.Boolean(string='Crisis Intervention', tracking=True)
    
    # Previous Attempts
    op_treatment = fields.Boolean(string='OP Treatment', tracking=True)
    home_care = fields.Boolean(string='Home Care', tracking=True)
    independent_patient = fields.Boolean(string='Independent Patient', tracking=True)
    alternative_treatment = fields.Boolean(string='Alternative Treatment', tracking=True)
    psychological_counselling = fields.Boolean(string='Psychological Counselling', tracking=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.independent.examination') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.independent.examination.seq') or _('New')
        return super(HospitalIndependentExamination, self).create(vals_list)
    
    def action_confirm(self):
        """Change state to completed when confirmed"""
        self.write({'state': 'completed'})
    
    def inprogress(self):
        """Change state to in_progress"""
        self.write({'state': 'in_progress'})


class HospitalIndependentExaminationProfessional(models.Model):
    _name = 'hospital.independent.examination.professional'
    _description = 'Independent Examination Professional Details'
    
    examination_id = fields.Many2one('hospital.independent.examination', string='Examination', ondelete='cascade')
    professional_id = fields.Many2one('hospital.employee', string='Professional')
    examination_date = fields.Date(string='Examination Date')
    place = fields.Char(string='Place')


class HospitalIndependentExaminationCategory(models.Model):
    _name = 'hospital.independent.examination.category'
    _description = 'Independent Examination Category'
    
    examination_id = fields.Many2one('hospital.independent.examination', string='Examination', ondelete='cascade')
    doctor_name = fields.Many2one('hospital.physician', string='Doctor Name')
    category = fields.Char(string='Category')
    date = fields.Date(string='Date')
    date_admission = fields.Date(string='Date of Admission')
    expiry_date = fields.Date(string='Expiry Date')


class HospitalIndependentExaminationDocument(models.Model):
    _name = 'hospital.independent.examination.document'
    _description = 'Independent Examination Document'
    
    examination_id = fields.Many2one('hospital.independent.examination', string='Examination', ondelete='cascade')
    document_type = fields.Char(string='Document Type')
    executed_date = fields.Date(string='Executed Date')
    available = fields.Boolean(string='Available')


class HospitalIndependentExaminationCapacity(models.Model):
    _name = 'hospital.independent.examination.capacity'
    _description = 'Independent Examination Capacity'
    
    examination_id = fields.Many2one('hospital.independent.examination', string='Examination', ondelete='cascade')
    capacity_assessment = fields.Char(string='Capacity Assessment')
    outcome = fields.Char(string='Outcome')
    psychiatrist = fields.Many2one('hospital.physician', string='Psychiatrist')
    date = fields.Date(string='Date')


class HospitalIndependentExaminationMentalHealth(models.Model):
    _name = 'hospital.independent.examination.mental.health'
    _description = 'Independent Examination Mental Health'
    
    examination_id = fields.Many2one('hospital.independent.examination', string='Examination', ondelete='cascade')
    category = fields.Char(string='Category')
    Mandate = fields.Char(string='Mandate')
    date_admission = fields.Date(string='Date of Admission')
    inform_date = fields.Date(string='Inform Date')


class HospitalIndependentExaminationScales(models.Model):
    _name = 'hospital.independent.examination.scales'
    _description = 'Independent Examination Scales'
    
    examination_id = fields.Many2one('hospital.independent.examination', string='Examination', ondelete='cascade')
    scale = fields.Char(string='Scale')
    administered = fields.Char(string='Administered')
    scoring = fields.Char(string='Scoring')
    date = fields.Date(string='Date')