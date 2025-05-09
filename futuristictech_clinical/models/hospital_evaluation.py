from odoo import _, api, fields, models

class Evaluation(models.Model):
    _name = 'hospital.evaluation'
    _description = 'Patient Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Evaluation #', required=True, readonly=True, default=lambda self: 'New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', tracking=True)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment #')
    date = fields.Date(string='Evaluation Date', default=fields.Date.context_today, tracking=True)
    evaluation_end_date = fields.Date(string='End Date', tracking=True)
    # Clinical data
    indication = fields.Char(string='Indication')
    height = fields.Float(string='Height (cm)')
    weight = fields.Float(string='Weight (kg)')
    bmi = fields.Float(string='Body Mass Index (BMI)', compute='_compute_bmi', store=True)
    temperature = fields.Float(string='Temperature (°C)')
    pulse = fields.Integer(string='Pulse')
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    systolic_bp = fields.Integer(string='Systolic BP')
    diastolic_bp = fields.Integer(string='Diastolic BP')
      # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    chief_complaint = fields.Char(string='Chief Complaint', tracking=True)
    notes_complaint = fields.Text(string='Complaint Notes')
    evaluation_type = fields.Selection([
        ('initial', 'Initial'),
        ('followup', 'Follow-up'),
        ('annual', 'Annual'),
        ('emergency', 'Emergency'),
    ], string='Evaluation Type', default='initial', tracking=True)
    
    observation = fields.Text(string='Observation')
    diagnosis = fields.Text(string='Diagnosis')
    treatment_plan = fields.Text(string='Treatment Plan')
    notes = fields.Text(string='Notes')

    # Vital Signs
    temperature = fields.Float(string='Temperature (°C)')
    systolic_bp = fields.Integer(string='Systolic BP')
    diastolic_bp = fields.Integer(string='Diastolic BP')
    pulse = fields.Integer(string='Pulse (BPM)')
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    osat = fields.Float(string='O2 Saturation (%)')
    
    # Anthropometry
    height = fields.Float(string='Height (cm)')
    weight = fields.Float(string='Weight (kg)')
    bmi = fields.Float(string='Body Mass Index (BMI)', compute='_compute_bmi', store=True)
    abdominal_circ = fields.Float(string='Abdominal Circumference (cm)')
    head_circumference = fields.Float(string='Head Circumference (cm)')
    
    # Signs - Physical Examination
    edema = fields.Boolean(string='Edema')
    petechiae = fields.Boolean(string='Petechiae')
    acropachy = fields.Boolean(string='Acropachy')
    miosis = fields.Boolean(string='Miosis')
    cough = fields.Boolean(string='Cough')
    arritmia = fields.Boolean(string='Arritmia')
    heart_extra_sounds = fields.Boolean(string='Heart Extra Sounds')
    ascites = fields.Boolean(string='Ascites')
    bronchophony = fields.Boolean(string='Bronchophony')
    cyanosis = fields.Boolean(string='Cyanosis')
    hematoma = fields.Boolean(string='Hematoma')
    nystagmus = fields.Boolean(string='Nystagmus')
    mydriasis = fields.Boolean(string='Mydriasis')
    palpebral_ptosis = fields.Boolean(string='Palpebral Ptosis')
    heart_murmurs = fields.Boolean(string='Heart Murmurs')
    jugular_engorgement = fields.Boolean(string='Jugular Engorgement')
    lung_adventitious_sounds = fields.Boolean(string='Lung Adventitious Sounds')
    increased_fremitus = fields.Boolean(string='Increased Fremitus')
    jaundice = fields.Boolean(string='Jaundice')
    breast_lump = fields.Boolean(string='Breast Lump')
    nipple_inversion = fields.Boolean(string='Nipple Inversion')
    peau_dorange = fields.Boolean(string='Peau d\'Orange')
    hypotonia = fields.Boolean(string='Hypotonia')
    masses = fields.Boolean(string='Masses')
    goiter = fields.Boolean(string='Goiter')
    xerosis = fields.Boolean(string='Xerosis')
    decreased_fremitus = fields.Boolean(string='Decreased Fremitus')
    lynphadenitis = fields.Boolean(string='Lynphadenitis')
    breast_asymmetry = fields.Boolean(string='Breast Asymmetry')
    nipple_discharge = fields.Boolean(string='Nipple Discharge')
    gynecomastia = fields.Boolean(string='Gynecomastia')
    hypertonia = fields.Boolean(string='Hypertonia')
    pressure_ulcers = fields.Boolean(string='Pressure Ulcers')
    alopecia = fields.Boolean(string='Alopecia')
    erithema = fields.Boolean(string='Erithema')

        # Nutrition
    malnutrition = fields.Boolean(string='Malnutrition')
    dehydration = fields.Boolean(string='Dehydration')
    
    # Lab Values
    glycemia = fields.Float(string='Glycemia (mg/dL)')
    hba1c = fields.Float(string='HbA1c (%)')
    cholesterol_total = fields.Float(string='Total Cholesterol (mg/dL)')
    ldl = fields.Float(string='LDL (mg/dL)')
    hdl = fields.Float(string='HDL (mg/dL)')
    tag = fields.Float(string='Triglycerides (mg/dL)')

    # Symptoms - Pain
    symptom_pain = fields.Boolean(string='Pain')
    symptom_pain_intensity = fields.Selection([
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ], string='Pain Intensity')
    symptom_arthralgia = fields.Boolean(string='Arthralgia')
    symptom_myalgia = fields.Boolean(string='Myalgia')
    symptom_abdominal_pain = fields.Boolean(string='Abdominal Pain')
    symptom_cervical_pain = fields.Boolean(string='Cervical Pain')
    symptom_thoracic_pain = fields.Boolean(string='Thoracic Pain')
    symptom_lumbar_pain = fields.Boolean(string='Lumbar Pain')
    symptom_pelvic_pain = fields.Boolean(string='Pelvic Pain')
    symptom_headache = fields.Boolean(string='Headache')
    symptom_hoarseness = fields.Boolean(string='Hoarseness')
    symptom_odynophagia = fields.Boolean(string='Odynophagia')
    symptom_sore_throat = fields.Boolean(string='Sore Throat')
    symptom_otalgia = fields.Boolean(string='Otalgia')
    symptom_ear_discharge = fields.Boolean(string='Ear Discharge')
    symptom_chest_pain = fields.Boolean(string='Chest Pain')
    symptom_chest_pain_excercise = fields.Boolean(string='Chest Pain during Exercise')
    symptom_orthostatic_hypotension = fields.Boolean(string='Orthostatic Hypotension')
    symptom_astenia = fields.Boolean(string='Astenia')
    symptom_anorexia = fields.Boolean(string='Anorexia')
    symptom_weight_change = fields.Boolean(string='Weight Change')
    symptom_abdominal_distension = fields.Boolean(string='Abdominal Distension')
    symptom_hemoptysis = fields.Boolean(string='Hemoptysis')
    symptom_hematemesis = fields.Boolean(string='Hematemesis')
    symptom_epistaxis = fields.Boolean(string='Epistaxis')
    symptom_gingival_bleeding = fields.Boolean(string='Gingival Bleeding')
    symptom_rinorrhea = fields.Boolean(string='Rinorrhea')
    symptom_nausea = fields.Boolean(string='Nausea')
    symptom_vomiting = fields.Boolean(string='Vomiting')
    symptom_dysphagia = fields.Boolean(string='Dysphagia')
    symptom_polydipsia = fields.Boolean(string='Polydipsia')
    symptom_polyphagia = fields.Boolean(string='Polyphagia')
    symptom_polyuria = fields.Boolean(string='Polyuria')
    symptom_nocturia = fields.Boolean(string='Nocturia')
    symptom_vesical_tenesmus = fields.Boolean(string='Vesical Tenesmus')
    symptom_pollakiuria = fields.Boolean(string='Pollakiuria')
    symptom_dysuria = fields.Boolean(string='Dysuria')

    # Symptoms - Miscellaneous
    symptom_mood_swings = fields.Boolean(string='Mood Swings')
    symptom_stress = fields.Boolean(string='Stress')
    symptom_pruritus = fields.Boolean(string='Pruritus')
    symptom_insomnia = fields.Boolean(string='Insomnia')
    symptom_disturb_sleep = fields.Boolean(string='Disturbed Sleep')
    symptom_dyspnea = fields.Boolean(string='Dyspnea')
    symptom_orthopnea = fields.Boolean(string='Orthopnea')
    symptom_amnesia = fields.Boolean(string='Amnesia')
    symptom_paresthesia = fields.Boolean(string='Paresthesia')
    symptom_paralysis = fields.Boolean(string='Paralysis')
    symptom_dizziness = fields.Boolean(string='Dizziness')
    symptom_vertigo = fields.Boolean(string='Vertigo')
    symptom_tinnitus = fields.Boolean(string='Tinnitus')
    symptom_syncope = fields.Boolean(string='Syncope')
    symptom_eye_glasses = fields.Boolean(string='Eye Glasses')
    symptom_blurry_vision = fields.Boolean(string='Blurry Vision')
    symptom_diplopia = fields.Boolean(string='Diplopia')
    symptom_photophobia = fields.Boolean(string='Photophobia')
    symptom_dysmenorrhea = fields.Boolean(string='Dysmenorrhea')
    symptom_amenorrhea = fields.Boolean(string='Amenorrhea')
    symptom_metrorrhagia = fields.Boolean(string='Metrorrhagia')
    symptom_menorrhagia = fields.Boolean(string='Menorrhagia')
    symptom_vaginal_discharge = fields.Boolean(string='Vaginal Discharge')
    symptom_urethral_discharge = fields.Boolean(string='Urethral Discharge')
    symptom_diarrhea = fields.Boolean(string='Diarrhea')
    symptom_constipation = fields.Boolean(string='Constipation')
    symptom_rectal_tenesmus = fields.Boolean(string='Rectal Tenesmus')
    symptom_melena = fields.Boolean(string='Melena')
    symptom_proctorrhagia = fields.Boolean(string='Proctorrhagia')
    symptom_sexual_dysfunction = fields.Boolean(string='Sexual Dysfunction')
    symptom_xerostomia = fields.Boolean(string='Xerostomia')

      # Mental Status - Glasgow Coma Scale
    loc = fields.Integer(string='Glasgow Coma Scale', compute='_compute_loc', store=True)
    loc_eyes = fields.Selection([
        ('1', '1: No Response'),
        ('2', '2: To Pain'),
        ('3', '3: To Verbal Command'),
        ('4', '4: Spontaneously'),
    ], string='Eyes')
    loc_verbal = fields.Selection([
        ('1', '1: No Response'),
        ('2', '2: Incomprehensible Sounds'),
        ('3', '3: Inappropriate Words'),
        ('4', '4: Disoriented and Converses'),
        ('5', '5: Oriented and Converses'),
    ], string='Verbal')
    loc_motor = fields.Selection([
        ('1', '1: No Response'),
        ('2', '2: Extension to Pain'),
        ('3', '3: Flexion to Pain'),
        ('4', '4: Withdrawal from Pain'),
        ('5', '5: Localizes Pain'),
        ('6', '6: Obeys Commands'),
    ], string='Motor')

     # Mental Assessment
    mood = fields.Selection([
        ('normal', 'Normal'),
        ('depressed', 'Depressed'),
        ('anxious', 'Anxious'),
        ('euphoric', 'Euphoric'),
        ('angry', 'Angry'),
        ('flat', 'Flat'),
    ], string='Mood')
    orientation = fields.Selection([
        ('normal', 'Normal'),
        ('partially', 'Partially Oriented'),
        ('disoriented', 'Disoriented'),
    ], string='Orientation')
    knowledge_current_events = fields.Selection([
        ('normal', 'Normal'),
        ('limited', 'Limited'),
        ('none', 'None'),
    ], string='Knowledge of Current Events')
    abstraction = fields.Selection([
        ('normal', 'Normal'),
        ('concrete', 'Concrete'),
        ('limited', 'Limited'),
    ], string='Abstraction')
    calculation_ability = fields.Selection([
        ('normal', 'Normal'),
        ('limited', 'Limited'),
        ('impaired', 'Impaired'),
    ], string='Calculation Ability')
    praxis = fields.Selection([
        ('normal', 'Normal'),
        ('limited', 'Limited'),
        ('impaired', 'Impaired'),
    ], string='Praxis')
    violent = fields.Boolean(string='Violent')
    memory = fields.Selection([
        ('normal', 'Normal'),
        ('recent_impaired', 'Recent Memory Impaired'),
        ('remote_impaired', 'Remote Memory Impaired'),
        ('both_impaired', 'Both Impaired'),
    ], string='Memory')
    judgment = fields.Selection([
        ('normal', 'Normal'),
        ('limited', 'Limited'),
        ('impaired', 'Impaired'),
    ], string='Judgment')
    vocabulary = fields.Selection([
        ('normal', 'Normal'),
        ('limited', 'Limited'),
        ('impaired', 'Impaired'),
    ], string='Vocabulary')
    object_recognition = fields.Selection([
        ('normal', 'Normal'),
        ('limited', 'Limited'),
        ('impaired', 'Impaired'),
    ], string='Object Recognition')

    # Diagnosis and Treatment
    indication = fields.Many2one('hospital.pathology', string='Indication', tracking=True)
    info_diagnosis = fields.Text(string='Information on Diagnosis')
    treatment_plan = fields.Text(string='Treatment Plan')
    


    # write the code for the compute method to calculate BMI, oncreate and onchange
    @api.depends('weight', 'height')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight:
                height_m = record.height / 100
                record.bmi = record.weight / (height_m ** 2)
            else:
                record.bmi = 0.0

    @api.depends('loc_eyes', 'loc_verbal', 'loc_motor')
    def _compute_loc(self):
        for record in self:
            loc_eyes = int(record.loc_eyes) if record.loc_eyes else 0
            loc_verbal = int(record.loc_verbal) if record.loc_verbal else 0
            loc_motor = int(record.loc_motor) if record.loc_motor else 0
            
            record.loc = loc_eyes + loc_verbal + loc_motor


    @api.onchange('weight', 'height')
    def _onchange_weight_height(self):
        for record in self:
            if record.weight and record.height:
                height_m = record.height / 100
                record.bmi = record.weight / (height_m ** 2)
            else:
                record.bmi = 0.0
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.evaluation') or _('New')
        return super(Evaluation, self).create(vals_list)
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    def action_complete(self):
        for record in self:
            record.state = 'completed'
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    def action_draft(self):
        for record in self:
            record.state = 'draft'
    def action_view_evaluation(self):
        """Smart button action to view evaluations"""
        self.ensure_one()
        return {
            'name': _('Evaluations'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.evaluation',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.id)],
            'context': {
                'default_patient_id': self.id,
                'default_physician_id': self.physician_id.id,
            }
        }


class HospitalGynacology(models.Model):
    _name = 'hospital.gynecology'
    _description = 'Hospital Gynacology'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Gynacology ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')



class HospitalPathology(models.Model):
    _name = 'hospital.pathology'
    _description = 'Hospital Pathology'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    category_id = fields.Many2one('hospital.pathology.category', string='Category')


class HospitalPathologyCategory(models.Model):
    _name = 'hospital.pathology.category'
    _description = 'Hospital Pathology Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('hospital.pathology.category', string='Parent Category')
    child_ids = fields.One2many('hospital.pathology.category', 'parent_id', string='Child Categories')