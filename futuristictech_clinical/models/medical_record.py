from odoo import models, fields, api, _

class InitialAssessment(models.Model):
    _name = 'hospital.initial.assessment'
    _description = 'Initial Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    name_seq = fields.Char(string='Assessment ID', readonly=True, index=True, copy=False, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Status', default='draft', tracking=True)
    
    # Patient Information
    ip_number = fields.Char(string='IP Number')
    patient_name = fields.Char(string='Patient Name')
    mrn_no = fields.Char(string='MRN No')
    age = fields.Integer(string='Age')
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender')
    campus_id = fields.Many2one('res.partner', string='Campus')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    doctor = fields.Many2one('res.partner', string='Doctor')
    known_allergies = fields.Text(string='Known Allergies')
    assessment_date = fields.Datetime(string='Assessment Date', default=fields.Datetime.now)
    physician_id = fields.Many2one('hr.employee', string='Physician')
    # History Information
    history_given_by = fields.Char(string='History Given By')
    history_taken_by = fields.Many2one(
        'hr.employee', 
        string='History Taken By',
        domain="[('job_id.name','in',['MEDICAL OFFICER', 'Senior Registrar/ Junior Consultant','Psychiatrist'])]"
    )
    
    # Complaint Lines
    cheif_complain_line_ids = fields.One2many(
        'hospital.chief.complaint.line', 
        'assessment_id', 
        string='Chief Complaints'
    )
    
    # Past History Lines
    past_history_line_ids = fields.One2many(
        'hospital.past.history.line', 
        'assessment_id', 
        string='Past History'
    )
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    # Medical Information
    history_present_illness = fields.Text(string='History of Present Illness')
    present_medication = fields.Text(string='Present Medication')
    family_history = fields.Text(string='Family History')
    personal_history = fields.Text(string='Personal History')
    relevant_investigation = fields.Text(string='Relevant Investigation')
    
    # Physical Examination
    pulse_rate = fields.Char(string='Pulse Rate')
    bp_rate = fields.Char(string='BP Rate')
    cyanosis = fields.Boolean(string='Cyanosis')
    icterus = fields.Boolean(string='Icterus')
    sensorim = fields.Boolean(string='Sensorim')
    pallor = fields.Boolean(string='Pallor')
    clubbing = fields.Boolean(string='Clubbing')
    lymphadeonopathy = fields.Boolean(string='Lymphadenopathy')
    other_assessment = fields.Text(string='Other Assessment')
    systemac_examination = fields.Text(string='Systemic Examination')
    provisional_diagnosis = fields.Text(string='Provisional Diagnosis')
    
    # Button Actions
    def action_confirm(self):
        self.write({'state': 'completed'})
    
    def action_inprogress(self):
        self.write({'state': 'in_progress'})
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.initial.assessment') or _('New')
        return super(InitialAssessment, self).create(vals_list)

class ChiefComplaintLine(models.Model):
    _name = 'hospital.chief.complaint.line'
    _description = 'Chief Complaint Line'
    
    assessment_id = fields.Many2one('hospital.initial.assessment', string='Assessment')
    cheif_complaints = fields.Char(string='Chief Complaint')
    duration = fields.Char(string='Duration')

class PastHistoryLine(models.Model):
    _name = 'hospital.past.history.line'
    _description = 'Past History Line'
    
    assessment_id = fields.Many2one('hospital.initial.assessment', string='Assessment')
    past_history = fields.Char(string='Past History')
    past_duration = fields.Char(string='Duration')

class VitalChart(models.Model):
    _name = 'vital.charts'
    _description = 'Vital Chart'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    name_seq = fields.Char(string='Vital Chart ID', readonly=True, default=lambda self: _('New'))
    
    # Patient Information
    ip_number = fields.Char(string='IP Number', tracking=True)
    patient_name = fields.Char(string='Patient Name', tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    mrn_no = fields.Char(string='MRN Number', tracking=True)
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', tracking=True)
    patient_id = fields.Many2one('hospital.patient',string='Patient')
    datetime = fields.Datetime(string='DateTime')
    temperature = fields.Integer(string='temperature')
    pulse = fields.Integer('pulse')
    blood_pressure_systolic = fields.Integer(string='Blood pressure systolic')
    blood_pressure_diastolic = fields.Integer('blood 0pressure diastolic')
    recorded_by = fields.Many2one('res.users', string='Recorded By', default=lambda self: self.env.user)
    
    # Date and Consultant
    date = fields.Date(string='Date', default=fields.Date.today, tracking=True)
    consultant_id = fields.Many2one('hr.employee', string='Consultant', tracking=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', tracking=True)
    
    # Vital Chart Lines
    vital_chart_line_ids = fields.One2many('vital.charts.line', 'vital_chart_id', string='Vital Chart Lines')
    
    # Notes
    vital_notes = fields.Text(string='Notes', tracking=True)
    
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
                vals['name'] = self.env['ir.sequence'].next_by_code('vital.charts') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('vital.charts.sequence') or _('New')
        return super(VitalChart, self).create(vals_list)
    
    def action_inprogress(self):
        self.state = 'in_progress'
    
    def action_confirm(self):
        self.state = 'completed'


class VitalChartLine(models.Model):
    _name = 'vital.charts.line'
    _description = 'Vital Chart Line'
    _order = 'vital_datetime desc'
    
    vital_chart_id = fields.Many2one('vital.charts', string='Vital Chart', ondelete='cascade')
    vital_datetime = fields.Datetime(string='Date & Time', default=fields.Datetime.now)
    vital_temp = fields.Float(string='Temperature (°C)')
    vital_pulse = fields.Integer(string='Pulse (bpm)')
    vital_resp = fields.Integer(string='Respiratory Rate')
    vital_bp = fields.Char(string='Blood Pressure')
    vital_spo2 = fields.Float(string='SpO2 (%)')
    vital_intake = fields.Float(string='Intake')
    vital_output = fields.Float(string='Output')
    vital_Total = fields.Float(string='Total', compute='_compute_total')
    vital_user = fields.Many2one('res.users', string='Recorded By', default=lambda self: self.env.user)
    
    @api.depends('vital_intake', 'vital_output')
    def _compute_total(self):
        for record in self:
            record.vital_Total = record.vital_intake - record.vital_output


class MentalStatusExamination(models.Model):
    _name = 'hospital.mental.status.examination'
    _description = 'Mental Status Examination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    name_seq = fields.Char(string='MSE #', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    ip_number = fields.Char(string='IP Number')
    patient_name = fields.Char(related='patient_id.name', string='Patient Name')
    admission_id = fields.Many2one('hospital.inpatient.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    age = fields.Integer(string='Age', related='patient_id.age')
    mrn_no = fields.Char(string='MRN No', related='patient_id.mrn')
    patient_gender = fields.Selection(related='patient_id.gender', string='Sex')
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    
    # General appearance and behavior
    general_appearance_behavior = fields.Selection([
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string='General Appearance & Behavior')
    eye_contact_with_examiner = fields.Selection([
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('none', 'None')
    ], string='Eye Contact with Examiner')
    touch_with_surrounding = fields.Selection([
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('none', 'None')
    ], string='Touch with Surrounding')
    dress = fields.Selection([
        ('appropriate', 'Appropriate'),
        ('inappropriate', 'Inappropriate')
    ], string='Dress')
    rapport = fields.Selection([
        ('good', 'Good'),
        ('adequate', 'Adequate'),
        ('poor', 'Poor')
    ], string='Rapport')
    attitude_towards_interviewer = fields.Selection([
            ('cooperative', 'Cooperative'),
        ('uncooperative', 'Uncooperative'), 
        ('seductive', 'Seductive'),
        ('hostile', 'Hostile'),
        ('playful', 'Playful'),
        ('evasive', 'Evasive'),
        ('guarded', 'Guarded'),
        ('ingratiating', 'Ingratiating'),
        ('attention_seeking', 'Attention seeking'),
        ('suspicious', 'Suspicious'),
        ('tense', 'Tense'),
        ('withdrawn', 'Withdrawn'),
        ('apathetic', 'Apathetic'),
        ('perplexed', 'Perplexed'),
        ('disinhibited', 'Disinhibited'),
        ('attentive', 'Attentive'),
        ('frank', 'Frank')
    ], string='Attitude towards Interviewer')
    
    # Psychomotor activity
    psychomotor_activity = fields.Selection([
        ('normal', 'Normal'),
        ('hyperactive', 'Hyperactive'),
        ('hypoactive', 'Hypoactive')
    ], string='Psychomotor Activity')
    
    # Speech
    speech_initiation = fields.Selection([
        ('spontaneous', 'Spontaneous'),
        ('hesitant', 'Hesitant'),
        ('mute', 'Mute')
    ], string='Speech Initiation')
    speech_reaction_time = fields.Selection([
        ('normal', 'Normal'),
        ('delayed', 'Delayed'),
        ('accelerated', 'Accelerated')
    ], string='Reaction Time')
    speech_intensity = fields.Selection([
        ('normal', 'Normal'),
        ('increased', 'Increased'),
        ('decreased', 'Decreased')
    ], string='Intensity')
    speech_pitch = fields.Selection([
        ('normal', 'Normal'),
        ('high', 'High'),
        ('low', 'Low')
    ], string='Speed')
    pressure_of_speech = fields.Selection([
        ('normal', 'Normal'),
        ('pressured', 'Pressured'),
        ('reduced', 'Reduced')
    ], string='Pressure of Speech')
    speech_volume = fields.Selection([
        ('normal', 'Normal'),
        ('loud', 'Loud'),
        ('soft', 'Soft')
    ], string='Volume')
    speech_relevance = fields.Selection([
        ('relevant', 'Relevant'),
        ('irrelevant', 'Irrelevant')
    ], string='Relevance')
    speech_coherence = fields.Selection([
        ('coherent', 'Coherent'),
        ('incoherent', 'Incoherent')
    ], string='Coherence')
    speech_deviation = fields.Selection([
        ('none', 'None'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Deviation')
    
    # Thought
    thought_form = fields.Selection([
        ('normal', 'Normal'),
        ('circumstantial', 'Circumstantial'),
        ('tangential', 'Tangential'),
        ('loosening', 'Loosening of Association'),
        ('flight', 'Flight of Ideas')
    ], string='Thought Form')
    thought_normal = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Normal (Appropriate, Goal Directed and Relevant)')
    possession = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Possession')
    compulsions = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Compulsions')
    content_delusions = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Delusions')
    delusion_primary_secondary = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('complete', 'Complete'),
        ('partial', 'Partial'),
        ('systematized', 'Systematized'),
        ('non_systematized', 'Non-Systematized'),
        ('mood_congruent', 'Mood Congruent'),
        ('mood_incongruent', 'Mood Incongruent')
    ], string='Primary/Secondary, Complete/Partial, Systematized/Non-Systematized, Mood Congruent/Incongruent')
    effect_on_life = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='How Much It Affects His or Her Life')
    preoccupation = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Preoccupation')
    flow_stream_of_thought = fields.Selection([
        ('normal', 'Normal'),
        ('increased', 'Increased'),
        ('decreased', 'Decreased'),
        ('blocked', 'Blocked')
    ], string='Flow/Stream of Thought')
    thought_abnormal = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Abnormal')
    obsessions = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Obsessions')
    thought_alienation = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Thought Alienation')
    delusion_of = fields.Selection([
        ('reference', 'Reference'),
        ('persecution', 'Persecution'),
        ('grandeur', 'Grandeur'),
        ('nihilism', 'Nihilism'),
        ('guilt', 'Guilt')
    ], string='Delusion of')
    conviction_of_validity = fields.Selection([
        ('full', 'Full'),
        ('partial', 'Partial'),
        ('none', 'None')
    ], string='Conviction of Its Validity')
    depressive_cognition = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Depressive Cognition')
    preoccupation_details = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Preoccupation Details')
    somatization = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Somatization')
    
    # Mood
    mood_subjective = fields.Selection([
        ('euthymic', 'Euthymic'),
        ('dysphoric', 'Dysphoric'),
        ('euphoric', 'Euphoric'),
        ('irritable', 'Irritable'),
        ('anxious', 'Anxious')
    ], string='Mood (Subjective)')
    mood_objective = fields.Selection([
        ('euthymic', 'Euthymic'),
        ('annoyed', 'Annoyed'),
        ('irritable', 'Irritable'),
        ('angry', 'Angry')
    ], string='Mood (Objective)')
    mood_range = fields.Selection([
        ('normal', 'Normal & Broad'),
        ('restricted', 'Restricted'),
        ('blunted', 'Blunted'),
        ('flat', 'Flat')
    ], string='Range')
    mood_communicability = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Communicability')
    mood_congruence = fields.Selection([
        ('congruent', 'Congruent'),
        ('incongruent', 'Incongruent')
    ], string='Congruence')
    mood_fluctuations = fields.Selection([
        ('stable', 'Stable'),
        ('labile', 'Labile')
    ], string='Fluctuations of Mood')
    mood_intensity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], string='Intensity')
    mood_reactivity = fields.Selection([
        ('normal', 'Normal'),
        ('increased', 'Increased'),
        ('decreased', 'Decreased')
    ], string='Reactivity')
    mood_appropriateness = fields.Selection([
        ('appropriate', 'Appropriate'),
        ('inappropriate', 'Inappropriate')
    ], string='Appropriateness')
    
    # Perception
    perceptual_disturbances = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Perceptual Disturbances')
    body_image_disturbance = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Body Image Disturbance')
    sense_distortion = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Sense Distortion (Comment on Dulled or Heightened Perception & Changes in Quality)')
    sensory_modality = fields.Selection([
        ('auditory', 'Auditory'),
        ('visual', 'Visual'),
        ('tactile', 'Tactile'),
        ('olfactory', 'Olfactory'),
        ('gustatory', 'Gustatory')
    ], string='Sensory Modality')
    
    # Cognitive
    cognitive_attention_concentration = fields.Selection([
        ('normal', 'Normal'),
        ('impaired', 'Impaired')
    ], string='First Rank Symptom')
    cognitive_depersonalization_derealisation = fields.Selection([
        ('absent', 'Absent'),
        ('present', 'Present (Extreme Feelings of Detachment from Self or the Environment)')
    ], string='Depersonalization, Derealisation')
    cognitive_vigilance = fields.Selection([
        ('normal', 'Normal'),
        ('hypovigilant', 'Hypovigilant'),
        ('hypervigilant', 'Hypervigilant'),
        ('serial_sevens', 'Serial-Sevens (100-7)')
    ], string='Vigilance')
    cognitive_timing = fields.Selection([
        ('normal', 'Normal'),
        ('hypnopompic', 'Hypnopompic Hallucinations (While Waking Up)'),
        ('hypnagogic', 'Hypnagogic Hallucinations (While Falling Asleep)')
    ], string='Timing')
    hallucinations_description = fields.Selection([
        ('spontaneous', 'Spontaneous'),
        ('provoked', 'Provoked'),
        ('easily_aroused', 'Easily Aroused & Sustained')
    ], string='Describe Hallucinations')
    cognitive_orientation = fields.Selection([
        ('time', 'Time'),
        ('place', 'Place'),
        ('person', 'Person')
    ], string='Orientation')
    
    # Memory
    memory = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Memory')
    intelligence = fields.Selection([
        ('below_average', 'Below Average'),
        ('average', 'Average'),
        ('above_average', 'Above Average')
    ], string='Intelligence')
    comprehension = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Comprehension')
    abstract_thinking = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Abstract Thinking')
    memory_assess_by = fields.Selection([
        ('clinical_behavior', 'Clinical Behavior'),
        ('formal_tests', 'Formal Tests')
    ], string='Memory Assess By')
    general_fund_of_information = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='General Fund of Information')
    simple_arithmetics = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Simple Arithmetics')
    abstract_thinking_type = fields.Selection([
        ('concrete', 'Concrete'),
        ('abstract', 'Abstract')
    ], string='Abstract Thinking Type')
    
    # Judgment and Insight
    differences = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Differences')
    proverb = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Proverb')
    judgement_test = fields.Selection([
        ('social', 'Social'),
        ('test', 'Test')
    ], string='Judgement Test')
    insight_grade = fields.Selection([
        ('grade1', 'Grade I: Absence of Insight'),
        ('grade2', 'Grade II: Partial Insight'),
        ('grade3', 'Grade III: Complete Insight')
    ], string='Insight Grade')
    similarities = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Similarities')
    judgement = fields.Selection([
        ('intact', 'Intact'),
        ('impaired', 'Impaired')
    ], string='Judgement')
    insight = fields.Selection([
        ('absent', 'Absent'),
        ('partial', 'Partial'),
        ('complete', 'Complete')
    ], string='Insight')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='State', default='draft', tracking=True)
    
    examiner_id = fields.Many2one('res.users', string='Examiner', default=lambda self: self.env.user)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.mental.status.examination') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.mental.status.examination.seq') or _('New')
        return super(MentalStatusExamination, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'completed'
    
    def action_inprogress(self):
        for record in self:
            record.state = 'in_progress'

class CarePlan(models.Model):
    _name = 'hospital.care.plan'
    _description = 'Care Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date_from = fields.Date(string='From Date', default=fields.Date.context_today)
    date_to = fields.Date(string='To Date')
    problems = fields.Text(string='Problems')
    goals = fields.Text(string='Goals')
    interventions = fields.Text(string='Interventions')
    evaluation = fields.Text(string='Evaluation')
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.care.plan') or _('New')
        return super(CarePlan, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_in_progress(self):
        for record in self:
            record.state = 'in_progress'
    
    def action_complete(self):
        for record in self:
            record.state = 'completed'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'


class NurseAssessment(models.Model):
    _name = 'hospital.nurse.assessment'
    _description = 'Nurse Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    assessment_date = fields.Datetime(string='Assessment Date', default=fields.Datetime.now)
    nurse_id = fields.Many2one('res.users', string='Nurse', default=lambda self: self.env.user)
    vital_signs = fields.Text(string='Vital Signs')
    general_appearance = fields.Text(string='General Appearance')
    neurological = fields.Text(string='Neurological')
    cardiovascular = fields.Text(string='Cardiovascular')
    respiratory = fields.Text(string='Respiratory')
    gastrointestinal = fields.Text(string='Gastrointestinal')
    genitourinary = fields.Text(string='Genitourinary')
    musculoskeletal = fields.Text(string='Musculoskeletal')
    skin = fields.Text(string='Skin')
    pain = fields.Text(string='Pain Assessment')
    interventions = fields.Text(string='Interventions')
    notes = fields.Text(string='Additional Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.nurse.assessment') or _('New')
        return super(NurseAssessment, self).create(vals_list)


class DrugChart(models.Model):
    _name = 'hospital.drug.chart'
    _description = 'Drug Chart'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    line_ids = fields.One2many('hospital.drug.chart.line', 'drug_chart_id', string='Drug Lines')
    age = fields.Integer(string='Age', store=True)
    ip_number = fields.Char(string='IP Number', store=True)
    mrn_no = fields.Char(string='MRN No', store=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', store=True)
    gender = fields.Selection([
        ('male','Male'),
        ('feemale', 'Female'),
        ('other', 'Other'),
    ],string="Sex")
    drug_allergies = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Drug Allergies', default='no')
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    ward = fields.Many2one('hospital.block', string='Ward', store=True)
    room = fields.Integer('Room')
    diet = fields.Selection([
        ('veg_diet', 'Vega\etable Diet'),
        ('non_veg_diet', 'Non-Vegetable  Diet'),
        ('mixed_diet', 'Mixed Diet'),
    ], string='Diet', default='veg_diet', store=True)
    blood_group = fields.Selection([
        ('a_positive', 'A+'),
        ('a_negative', 'A-'),
        ('b_positive', 'B+'),
        ('b_negative', 'B-'),
        ('ab_positive', 'AB+'),
        ('ab_negative', 'AB-'),
        ('o_positive', 'O+'),
        ('o_negative', 'O-')
    ], string='Blood Group', store=True)
    doctor = fields.Many2one('res.partner', string='Doctor', store=True)
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.drug.chart') or _('New')
        return super(DrugChart, self).create(vals_list)


class DrugChartLine(models.Model):
    _name = 'hospital.drug.chart.line'
    _description = 'Drug Chart Line'
    
    drug_chart_id = fields.Many2one('hospital.drug.chart', string='Drug Chart')
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    dosage = fields.Char(string='Dosage')
    frequency_id = fields.Many2one('hospital.drug.frequency', string='Frequency')
    route_id = fields.Many2one('hospital.drug.route', string='Route')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    morning = fields.Boolean(string='Morning')
    noon = fields.Boolean(string='Noon')
    evening = fields.Boolean(string='Evening')
    night = fields.Boolean(string='Night')
    administration_ids = fields.One2many('hospital.drug.administration', 'chart_line_id', string='Administrations')


class DrugAdministration(models.Model):
    _name = 'hospital.drug.administration'
    _description = 'Drug Administration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    chart_line_id = fields.Many2one('hospital.drug.chart.line', string='Drug Chart Line')
    patient_id = fields.Many2one(related='chart_line_id.drug_chart_id.patient_id', string='Patient', store=True)
    medicine_id = fields.Many2one(related='chart_line_id.medicine_id', string='Medicine', store=True)
    dosage = fields.Char(related='chart_line_id.dosage', string='Dosage', store=True)
    administration_date = fields.Date(string='Date', default=fields.Date.context_today)
    time = fields.Selection([
        ('morning', 'Morning'),
        ('noon', 'Noon'),
        ('evening', 'Evening'),
        ('night', 'Night')
    ], string='Time', required=True)
    administered = fields.Boolean(string='Administered')
    administered_by = fields.Many2one('res.users', string='Administered By')
    administered_datetime = fields.Datetime(string='Administered At')
    notes = fields.Text(string='Notes')
    
    @api.depends('patient_id', 'medicine_id', 'administration_date', 'time')
    def _compute_name(self):
        for record in self:
            if record.patient_id and record.medicine_id and record.administration_date:
                record.name = f"{record.patient_id.name} - {record.medicine_id.name} - {record.administration_date} - {record.time}"
            else:
                record.name = "New Administration"
    
    def action_administer(self):
        for record in self:
            record.administered = True
            record.administered_by = self.env.user.id
            record.administered_datetime = fields.Datetime.now()

class DrugFrequencyConfiguration(models.Model):
    _name = 'hospital.drug.frequency.config'
    _description = 'Drug Frequency Configuration'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    morning = fields.Boolean(string='Morning')
    noon = fields.Boolean(string='Noon')
    evening = fields.Boolean(string='Evening')
    night = fields.Boolean(string='Night')
    active = fields.Boolean(default=True)