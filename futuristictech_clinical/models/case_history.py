# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CaseHistory(models.Model):
    _name = 'case.history'
    _description = 'Case History'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'
    

    # Basic patient information
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    name = fields.Char(string='Name', related='patient_id.name')
    age = fields.Integer(string='Age', related='patient_id.age', store=True)
    dob = fields.Date(string='Date of Birth', related='patient_id.dob')
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex', related='patient_id.gender')
    
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated')
    ], string='Marital Status')
    
    languages_known = fields.Many2many('res.lang', string='Languages known')
    education = fields.Selection([
        ('none', 'None'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
        ('doctorate', 'Doctorate')
    ], string='Education')
    
    religion = fields.Selection([
        ('hindu', 'Hindu'),
        ('muslim', 'Muslim'),
        ('christian', 'Christian'),
        ('buddhist', 'Buddhist'),
        ('jain', 'Jain'),
        ('sikh', 'Sikh'),
        ('other', 'Other')
    ], string='Religion')
    other_religion = fields.Char(string='Other Religion')
    
    socio_economic_status = fields.Selection([
        ('low', 'Low'),
        ('middle', 'Middle'),
        ('high', 'High')
    ], string='Socio-Economic Status')
    
    occupation = fields.Many2one('hospital.patient.occupation', string='Occupation')
    vocation = fields.Char(string='Vocation')
    # Informants
    informant_name = fields.Char(string='Name')
    relationship_id = fields.Many2one('hospital.patient.relationship', string='Relationship')
    duration_stay = fields.Char(string='Duration of Stay with Patients')
    
    # Information and complaints
    information = fields.Text(string='INFORMATION : Reliable and Adequate')
    complaint_ids = fields.One2many('hospital.chief.complaint', 'case_history_id', string='CHIEF COMPLAINTS')
    
    # Onset of illness
    onset_of_ill = fields.Selection([
        ('Abrupt', 'Abrupt (Sudden)'),
        ('Acute', 'Acute (Few hours to few days)'),
        ('Sub-acute', 'Sub-acute (Few days to few weeks)'),
        ('Insidious', 'Insidious (Few weeks to few months)')
    ], string='Onset of Illness')
    abrupt_desc = fields.Text(string='Abrupt Description')
    acute_desc = fields.Text(string='Acute Description')
    subacute_desc = fields.Text(string='Sub-acute Description')
    insidious_desc = fields.Text(string='Insidious Description')
    
    # Course and duration
    course = fields.Selection(
        [('continuous', 'Continuous'),
            ('episodic', 'Episodic'),
            ('flutuating', 'Fluctuating'),],
        string='Course of Illness'
    )
    duration_illness = fields.Selection([
        ('Months', 'Months'),
        ('Years', 'Years')
    ], string='Duration of Illness')
    ill_months = fields.Integer(string='Months')
    ill_years = fields.Integer(string='Years')
    
    # Precipitating factors
    precipitating_factors = fields.Text(string='Precipitating Factors')
    
    # Present illness
    history_present_ill = fields.Text(string='HISTORY OF PRESENT ILLNESS (Describe Chief Complaints)')
    
    # Biological functioning
    appetite = fields.Selection([
        ('Normal', 'Normal'),
        ('Decreased', 'Decreased'),
        ('Increased', 'Increased')
    ], string='Appetite')
    
    sleep = fields.Selection([
        ('Normal', 'Normal'),
        ('Disturbed Difficulty in falling asleep', 'Disturbed Difficulty in falling asleep'),
        ('Early morning awakening', 'Early morning awakening'),
        ('No clear patterns of disturbances', 'No clear patterns of disturbances')
    ], string='Sleep')
    
    bladder = fields.Selection([
        ('Within Normal Limits', 'Within Normal Limits'),
        ('Incontinence', 'Incontinence')
    ], string='Bladder')
    
    bowel = fields.Selection([
        ('Constipation', 'Constipation'),
        ('Diarrhea', 'Diarrhea'),
        ('Normal', 'Normal')
    ], string='Bowel')
    
    weight = fields.Selection([
        ('Increase', 'Increase'),
        ('Decrease', 'Decrease')
    ], string='Weight')
    
    sexual = fields.Selection([
        ('Normal', 'Normal'),
        ('Increased Sexual Drive', 'Increased Sexual Drive'),
        ('Premature Ejaculation', 'Premature Ejaculation'),
        ('Impotence', 'Impotence'),
        ('Decreased Sexual urge', 'Decreased Sexual urge'),
        ('Other issues', 'Other issues')
    ], string='Sexual')
    other_sex_issues = fields.Text(string='Other Sexual Issues')
    
    # Social functioning
    dress_take_care_himself = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Dresses and takes care of him/ herself')
    suicidal_tendency = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Suicidal tendency')
    self_harm = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Self harm')
    self_harm_specify = fields.Text(string='Specify Self Harm')
    self_harm_others = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),

        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Self harm to others')
    self_harm_others_specify = fields.Text(string='Specify Self Harm to Others')    
    goes_out = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Goes out')
    violence_tendency = fields.Selection([

        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')    
    ], string='Violence tendency')

    goes_work = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Goes to work')
    
    does_husehold = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Does household chores')
    
    gets_along_wit_family = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Gets along with family')
    
    gets_along_wit_neighbours = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Gets along with neighbours')
    
    # Treatment history
    previous_hospitalization = fields.Text(string='Previous Hospitalization')
    opd = fields.Text(string='OPD')
    day_care_centre = fields.Text(string='Day Care Centre')
    
    # Interval functioning
    interval_functioning = fields.Text(string='Interval functioning (what is the patient like between episodes/when \'well\')')
    
    # Suicide attempts
    suicide_attempts = fields.Text(string='Suicide attempts (If present, refer Suicidal Risk Assessment - Becks Suicide Intent Scale)/drug and alcohol abuse')
    
    # Medical treatment history
    physical_illness = fields.Text(string='Physical Illness (Present)')
    
    head_injury = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Head Injury')
    specify_injury = fields.Text(string='Specify Injury')
    
    past_surgeris = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Past Surgeries')
    specify_surgeries = fields.Text(string='Specify Surgeries')
    
    seizure = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Seizure')
    specify_seizure = fields.Text(string='Specify Seizure')
    
    substance_use = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Substance Use')
    specify_substance = fields.Text(string='Specify Substance')
    
    allergies = fields.Text(string='Allergies (to food, medications etc., specify)')
    
    epilepsy = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Epilepsy')
    specify_episodes = fields.Text(string='Specify Episodes')
    
    # Constitutional health check
    weight_loss = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Weight Loss')
    
    fatigue = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Fatigue')
    
    fever = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Fever')
    
    # Respiratory
    cough_easy = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Cough Easy')
    
    cough_blood = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Coughing Blood')
    
    wheezing = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Wheezing')
    
    chills = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Chills')
    
    # Hematology/Lymph
    easy_bruising = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Easy Bruising')
    
    gums_bleed_easily = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Gums Bleed Easily')
    
    enlarged_glands = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Enlarged Glands')
    
    # Eyes
    glass_contact = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Glass/Contact')
    
    eye_pain = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Eye Pain')
    
    double_vision = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Double Vision')
    
    cataracts = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Cataracts')
    
    # Gastrointestinal
    heartburn_reflux = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Heartburn/Reflux')
    
    nausea_vomiting = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Nausea/Vomiting')
    
    constipation = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Constipation')
    
    change_in_bm = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Change in BM')
    
    diarrhea = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Diarrhea')
    
    jauntice = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Jauntice')
    
    abdominal_pain = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Abdominal Pain')
    
    black_bloody_bm = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Black Bloody BM')
    
    # Musculoskeletal
    joint_pain = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Joint Pain/Swelling')
    
    stiffness = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Stiffness')
    
    muscle_pain = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Muscle Pain')
    
    back_pain = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Back Pain')
    
    # Skin
    rash_shores = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Rash Shores')
    
    lesions = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Lesions')
    
    itching_burning = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Itching Burning')
    
    # Ears, Nose, Throat
    difficulty_hearing = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Difficulty Hearing')
    
    ringing_ears = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Ringing Ears')
    
    vertigo = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Vertigo')
    
    sinus_trouble = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Sinus Trouble')
    
    nasal_stuffiness = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Nasal Stuffiness')
    
    freq_sore_throat = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Frequent Sore Throat')
    
    # Genitourinary
    burning_freq = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Burning Frequency')
    
    nighttime = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Nighttime')
    
    blood_in_urine = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Blood in Urine')
    
    erictile_dysfunction = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Erectile Dysfunction')
    
    abnormal_discharge = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Abnormal Discharge')
    
    bladder_leakage = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Bladder Leakage')
    
    # Neurological
    loss_strength = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Loss Strength')
    
    numbness = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Numbness')
    
    headaches = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Headaches')
    
    tremors = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Tremors')
    
    memory_loss = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Memory Loss')
    
    # Cardiovascular
    murmur = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Murmur')
    
    chest_pain = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Chest Pain')
    
    palpitations = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Palpitations')
    
    dizziness = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Dizziness')
    
    fainting_spells = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Fainting Spells')
    
    shortness_of_breathe = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Shortness of Breathe')
    
    difficult_lying_flat = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Difficulty Lying Flat')
    
    swelling_ankles = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Swelling Ankles')
    
    # Endocrine
    loss_of_hair = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Loss of Hair')
    
    heat_cold_intolerance = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Heat/Cold Intolerance')
    
    # Allergic/Immunologic
    hives_eczema = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Hives/Eczema')
    
    hay_fever = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Hay Fever')
    
    # Females Only
    last_date_mammogram = fields.Date(string='Date last Mammogram')
    mammogram_options = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal')
    ], string='Select')
    
    date_last_pap = fields.Date(string='Date last PAP')
    pap_options = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal')
    ], string='PAP')
    
    age_onset_periods = fields.Char(string='Age onset Periods')
    age_onset_menopause = fields.Char(string='Age onset Menopause')
    
    regular_periods = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Regular Periods')
    
    no_pregnancies = fields.Char(string='Number Pregnancies')
    
    # Medication and effects
    physiatric_medication_ids = fields.One2many('hospital.psychiatric.medication', 'case_history_id', string='Psychiatric Medication')
    general_medication_ids = fields.One2many('hospital.general.medication', 'case_history_id', string='General Medication')
    physiatric_effect_ids = fields.One2many('hospital.psychiatric.effect', 'case_history_id', string='Psychiatric Medication Effects')
    general_effect_ids = fields.One2many('hospital.general.effect', 'case_history_id', string='General Medication Effects')
    history_medicines = fields.Text(string='History of Medicines Prescribed')
    
    # Family history
    consanguinity_in_parents = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Consanguinity in parents')
    consanguinity_specify = fields.Text(string='Specify')
    
    family_history_pp = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Family history of psychiatric and physical illness')
    present_specify = fields.Text(string='Specify')
    
    # Interpersonal relations
    interpersonal_relations = fields.Text(string='Interpersonal Relations')
    family_comm = fields.Text(string='Family Communication')
    leadership_pattern = fields.Text(string='Leadership Pattern')
    role_functions = fields.Text(string='Role Functions')
    social_support = fields.Text(string='Social Support')
    reinforcement = fields.Text(string='Reinforcement')
    
    # Type of family
    type_family = fields.Selection([
        ('joint_family', 'Joinit Family'),
        ('nuclear_family', 'Nuclear Family'),
        ('extended_family', 'extended_family'),
        ('single_family', 'single_family'),
    ],string='Type of Family')
    family_environ = fields.Selection([
        ('cordial', 'Cordial'),
        ('strained', 'Strained')
    ],string='Family Environment')
    
    # Personal history - birth
    drug_exposure = fields.Text(string='Drug Exposure')
    medical_complication = fields.Text(string='Medical Complication')
    complication_during_preg = fields.Text(string='Complication During Pregnancy')
    major_illness = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('not_known', 'Not Known'),
    ], string='H6 Major Mental Illness')
    whether_client_first_child = fields.Boolean(string='Whether Client is First Child')
    
    # Early development
    delayed_milestones = fields.Text(string='Delayed Milestones')
    behaviour_probs = fields.Text(string='Behaviour Problems')
    physical_illness_ids = fields.Many2many('hospital.physical.illness', string='Physical Illness')
    
    # Childhood / Academic history
    history_bullying = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='History of Bullying')
    
    check_boarding = fields.Selection([
        ('yes', 'Yes'), 
        ('no', 'No')
    ], string='Check if Boarding')
    
    parenting_style = fields.Selection([
        ('permissive', 'Permissive'),
        ('authoritarian', 'Authoritarian'),
        ('authoitative', 'Authoitative'),
        
    ], string='Parenting Style')
    
    academic_performance = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor')
    ], string='Academic Performance')
    
    # Menstrual history
    menstrual_history = fields.Text(string='Menstrual History')
    
    # Adolescence
    relationship_with_family = fields.Selection([
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor')
    ], string='Relationship with Family')
    specify_relationship = fields.Text(string='Specify Relationship')
    substance_usage = fields.Text(string='Substance Usage')
    bullying_history = fields.Text(string='Bullying History')
    check_if_boarding = fields.Text(string='Check if Boarding')
    
    parenting_style_adol = fields.Selection([
        ('permissive', 'Permissive'),
        ('authoritarian', 'Authoritarian'),
        ('authoitative', 'Authoitative'),],
        string= "Parenting Style")
    
    academic_performance_adol = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor')
    ], string='Academic Performance (Adolescence)')
    
    specify_not_good = fields.Text(string='Specify if Not Good')
    
    # Occupational history
    interaction_with_coll = fields.Selection([
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor')
    ], string='Interaction with Colleagues')
    interaction_specify = fields.Text(string='Specify Interaction')
    
    consistency_work = fields.Selection([
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor')
    ], string='Consistency at Work')
    consistency_specify = fields.Text(string='Specify Consistency')
    other_issues = fields.Text(string='Other Issues')
    
    # Sexual history
    premarital_relationship = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Premarital Relationship')
    if_yes_premarital = fields.Text(string='If Yes Premarital')
    
    history_masturbation = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='History of Masturbation')
    if_yes_masturbation = fields.Text(string='If Yes Masturbation')
    
    homosexuality = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Homosexuality')
    
    # Marital history
    relation_wife = fields.Selection([
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor')
    ], string='Relation with Wife')
    if_no_good_relationship = fields.Text(string='If Not Good Relationship')
    
    extra_marital = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Extra Marital')
    specify_if_extra = fields.Text(string='Specify if Extra')
    
    # Pre-morbid personality
    social_relations = fields.Text(string='Social Relations')
    moral_religious = fields.Text(string='Moral and Religious Standards')
    intellectual_activity = fields.Text(string='Intellectual Activities')
    predominant_mood = fields.Text(string='Predominant Mood')
    character = fields.Text(string='Character')
    use_of_leisure = fields.Text(string='Use of Leisure Time')
    habits = fields.Text(string='Habits')
    if_any_special_detail = fields.Text(string='If Any, Specify in Detail')
    
    # Legal involvements
    present_involvment = fields.Text(string='Present Involvement')
    past_involvment = fields.Text(string='Past Involvement')
    
    # Expectations of family
    expectations_family = fields.Text(string='Expectations of the Family (purpose of admission in the order of priority)')
    
    # Additional remarks
    additional_remarks = fields.Text(string='Additional Remarks')
    
    # Risk assessment
    risk_assessment_ids = fields.One2many('hospital.risk.assessment', 'case_history_id', string='Risk Assessment')
    
    # Mental status examination
    general_appearance = fields.Selection([
        ('Well Kempt', 'Well Kempt'),
        ('Poorly Kempt', 'Poorly Kempt')
    ], string='General Appearance')
    
    dress = fields.Selection([
        ('Appropriate', 'Appropriate'),
        ('shabby', 'shabby'),
        ('Inappropriate', 'Inappropriate')
    ], string='Dress')
    
    eye_contact = fields.Selection([
        ('maintained', 'Maintained'),
        ('partial', 'Partial'), 
        ('not_maintained', 'Not Maintained')
    ], string='Eye Contact')
    
    touch_with_surrounding = fields.Selection([
        ('Good', 'Good'),
        ('partial', 'Partial'),
        ('Poor', 'Poor')
    ], string='Touch with Surrounding')
    
    rapport = fields.Selection([
        ('easily_established', 'Easily Established'),
        ('established_with_difficulty', 'Established with difficulty'),
        ('not_possible', 'Not Possible')
    ], string='Rapport')
    
    attitude_to_interviewer = fields.Selection([
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
    ], string='Attitude to Interviewer')
    
    psychomotor_activity_ids = fields.Many2many('hospital.psychomotor.activity', string='Psychomotor Activity')
    catatonic_signs = fields.Many2many('hospital.catatonic.sign', string='Catatonic Signs')
    
    # Speech
    speech_initiation = fields.Selection([
        ('spontaneous', 'Spontaneous'),
        ('speaks_when_spoken', 'Speaks When Spoken To'),
        ('hesitant', 'Hesitant'), 
        ('mute', 'Mute'),
        ('slurring', 'Slurring'),
        ('stuttering', 'Stuttering'),
        ('whispering', 'Whispering'),
        ('muttering', 'Muttering')
    ], string='Speech Initiation')
    
    reaction_time = fields.Selection([
        ('Normal', 'Normal'),
        ('Delayed', 'Delayed'),
        ('Acclerated', 'Acclerated')
    ], string='Reaction Time')
    
    intensity = fields.Selection([
        ('audible', 'Audible'),
        ('excessively_loud', 'Excessively Loud'), 
        ('abnormally_soft', 'Abnormally Soft')
    ], string='Intensity')
    
    pitch = fields.Selection([
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Low', 'Low')
    ], string='Pitch')
    
    speed = fields.Selection([
        ('Normal', 'Normal'),
        ('Fast', 'Fast'),
        ('Slow', 'Slow')
    ], string='Speed')
    
    pressure_speech = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Pressure of Speech')
    
    volume = fields.Selection([
        ('Normal', 'Normal'),
        ('Low', 'Low'),
        ('High', 'High')
    ], string='Volume')
    
    relevance = fields.Selection([
        ('Relevant', 'Relevant'),
        ('off_target', 'Off Target'),
        ('Irrelevant', 'Irrelevant')
    ], string='Relevance')
    
    coherence = fields.Selection([
        ('Coherent', 'Coherent'),
        ('Incoherent', 'Incoherent')
    ], string='Coherence')
    
    deviation = fields.Selection([
        ('nil', 'Nil'),
        ('rhyming_punning', 'Rhyming and punnin'),
        ('neologism', 'Neologism'),
        ('condensation', 'condensation'),
        ('clang', 'clang'),
        ('association', 'association'), 
        ('stereotyping', 'stereotyping'),
        ('perseveration', 'perseveration'),
        ('word_salad', 'word salad'),
        ('over_inclusion', 'over inclusion'),
        ('drivelling', 'Drivelling'),
        ('desultory', 'Desultory'),
        ('derailment', 'derailment'),
        ('loosening_association', 'loosening of association')
    ], string='Deviation')
    
    # Thought form
    check_for_disorder = fields.Selection([
        ('loosening_of_association', 'Loosening of Association'),
        ('derailment', 'Derailment'),
        ('neologism', 'Neologism'),
        ('perseveration', 'Perseveration'), 
        ('word_salad', 'Word Salad'),
        ('over_inclusion', 'Over Inclusion'),
        ('drivelling', 'Drivelling'),
        ('desultory', 'Desultory')
    ], string='Check for Formal thought disorder')
    # Thought form (continuing)
    flow_stream_normal = fields.Selection([
        ('Normal', 'Normal'),
        ('Abnormal', 'Abnormal')
    ], string='Flow/Stream of thought Normal')
    
    flow_stream_abnormal = fields.Selection([
        ('Flight of ideas', 'Flight of ideas'),
        ('Loosening of association', 'Loosening of association'),
        ('Tangentiality', 'Tangentiality'),
        ('Circumstantiality', 'Circumstantiality')
    ], string='Flow/Stream of thought Abnormal')
    
    relationship_in_patient = fields.Selection([
        ('illogical', 'Illogical'),
        ('tangential', 'Tangential'), 
        ('circumstantial', 'Circumstantial'),
        ('rambling', 'Rambling'),
        ('evasive', 'Evasive'),
        ('perseverative', 'Perseverative Statements')
    ], string='Relationship in Patient')
    
    blocking_distractibility = fields.Selection([
        ('flight_of_ideas', 'Flight of Ideas'),
        ('retardation_thinking', 'Retardation of thinking'),
        ('circumstantialities', 'circumstantialities')
    ], string='Blocking/Distractibility')
    
    # Possession
    possession = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Possession')
    
    obsession = fields.Selection([
        ('Dirt / contamination', 'Dirt / contamination'),
        ('ideas', 'ideas'),
        ('doubts', 'doubts'),
        ('imagery', 'imagery'),
        ('impulses and phobias', 'impulses and phobias')
    ], string='Obsessions')
    
    compulsions = fields.Selection([
        ('checking', 'Checking'),
        ('counting', 'Counting'),
        ('washing', 'Washing')
    ], string='Compulsions')
    
    thought_alienation = fields.Selection([
        ('Blocking', 'Blocking'),
        ('Insertion', 'Insertion'),
        ('Broadcasting', 'Broadcasting'),
        ('withdrawal', 'withdrawal')
    ], string='Thought Alienation')
    
    # Delusions
    delusions_prior = fields.Selection([
        ('preferencial', 'preferencial'),
        ('Persecutory', 'Persecutory')
    ], string='Delusions')
    
    delusion_persecutory = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Delusion Persecutory')
    
    delusion = fields.Selection([
        ('love', 'love'),
        ('control', 'control'), 
        ('infidelity', 'infidelity'),
        ('reference', 'reference'),
        ('persecution', 'persecution'),
        ('nihilism', 'nihilism'),
        ('sin & guilt', 'sin & guilt'),
        ('poverty', 'poverty')
    ], string='Delusion of')
    
    grandiose = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Grandiose')
    
    delusion_list = fields.Selection([
        ('Grandiose Identity', 'Grandiose Identity'),
        ('Ability', 'Ability'),
        ('Role', 'Role'),
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('complete', 'complete'),
        ('partial', 'partial'),
        ('systematized', 'systematized'),
        ('non-systematized', 'non-systematized'),
        ('mood congruent', 'mood congruent'),
        ('incongruent', 'incongruent')
    ], string='Delusion List')
    
    conviction_validity = fields.Selection([
        ('Yes', 'Yes'),
        ('No', 'No')
    ], string='Conviction of Validity')
    
    how_affects_life = fields.Selection([
        ('significantly', 'Significantly'), 
        ('not_significantly', 'Not Significantly')
    ], string='How it affects life')
    
    # Depressive cognition
    depressive_cognition = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Depressive Cognition')
    
    depressive_overhauled = fields.Selection([
        ('Hopelessness', 'Hopelessness'),
        ('Helplessness', 'Helplessness'),
        ('Worthlessness', 'Worthlessness'),
        ('Guilt', 'Guilt'),
        ('Sin', 'Sin'),
        ('Nihilism', 'Nihilism'),
        ('Death wishes', 'Death wishes'),
        ('Suicidal ideas', 'Suicidal ideas'),       
        ('Suicidal intent', 'Suicidal intent'),
        ('Suicidal plans', 'Suicidal plans')    
    ], string='Depressive Overhauled')
    
    # Preoccupation
    preoccupation = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Preoccupation')
    
    preoccupation_list = fields.Selection([
        ('about the Illness', 'about the Illness'),
        ('Environmental problems', 'Environmental problems'), 
        ('Obsessions', 'Obsessions'),
        ('Compulsions', 'Compulsions'),
        ('Phobias', 'Phobias'),
        ('Obsessions or plans about suicide', 'Obsessions or plans about suicide'),
        ('Homicide', 'Homicide'),
        ('Hypochondriacal symptoms', 'Hypochondriacal symptoms'),
        ('specific Antisocial urges or impulses', 'specific Antisocial urges or impulses')
    ], string='Preoccupation List')
    
    somatisation = fields.Text(string='Somatisation')
    thought_sample = fields.Text(string='Thought Sample')

    # Mood
    subjective = fields.Selection([
        # ('Depressed', 'Depressed'),
        # ('Despairing', 'Despairing'),
        # ('Irritable', 'Irritable'),
        # ('Anxious', 'Anxious'),
        # ('Terrified', 'Terrified'),
        # ('Angry', 'Angry'),
        # ('Expansive', 'Expansive'),
        # ('Euphoric', 'Euphoric'),
        # ('Empty', 'Empty'),
        # ('Guilty', 'Guilty'),
        # ('Awed', 'Awed'),
        # ('Futile', 'Futile'),
        # ('Self-Contemptuous', 'Self-Contemptuous'),
        # ('Anhedonic', 'Anhedonic'),
        # ('Alexithymic', 'Alexithymic')
    ], string='Subjective')
    
    fluctuation_of_mood = fields.Selection([
        ('Absent', 'Absent'),
        ('Normal/ Excessive', 'Normal/ Excessive')
    ], string='Fluctuations of Mood')
    
    objective = fields.Selection([
        ('euthymic', 'Euthymic'),
        ('fearful', 'Fearful'),
        ('afraid', 'Afraid'), 
        ('tense', 'Tense'),
        ('nervous', 'Nervous'),
        ('shy', 'Shy'),
        ('ashamed', 'Ashamed'),
        ('guilt', 'Guilt'),
        ('sad', 'Sad'),
        ('upset', 'Upset'),
        ('fatigue', 'Fatigue'),
        ('surprise', 'Surprise'),
        ('joviality', 'Joviality'),
        ('self_assurance', 'Self-Assurance'),
        ('attentiveness', 'Attentiveness'),
        ('serene', 'Serene'),
        ('annoyed', 'Annoyed'),
        ('irritable', 'Irritable'),
        ('resentment', 'Resentment'),
        ('hostile', 'Hostile'),
        ('fury_rage', 'Fury and Rage'),
        ('negativism', 'Negativism'),
        ('normal', 'Normal'),
        ('disturbed', 'Disturbed'),
        ('depressed', 'Depressed'),
        ('despairing', 'Despairing'),
        ('anxious', 'Anxious'),
        ('panicky', 'Panicky'),
        ('terrified', 'Terrified'),
        ('angry', 'Angry'),
        ('expansive', 'Expansive'),
        ('euphoric', 'Euphoric'),
        ('elated', 'Elated'),
        ('blunted', 'Blunted'),
        ('apathetic', 'Apathetic'),
        ('labile', 'Labile'),
        ('weeping', 'Weeping'),
        ('estrangement', 'Feelings of Estrangement'),
        ('la_belle_indifference', 'La-belle Indifference')
    ], string='Objective')
    
    intensity_mood = fields.Selection([
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe')
    ], string='Intensity')
    
    range = fields.Selection([
        ('normal_broad', 'Normal and Broad'),
        ('restricted', 'Constricted/Restricted'),
        ('blunted_flat', 'Blunted or Flat'),
        ('shallow', 'Shallow')
    ], string='Range')
    
    reactivity = fields.Text(string='Reactivity')
    communicability = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Communicability')
    
    appropriateness = fields.Selection([
        ('Appropriate', 'Appropriate'),
        ('Inappropriate', 'Inappropriate')
    ], string='Appropriateness')
    
    congruence = fields.Selection([
        ('Congruent', 'Congruent'),
        ('Incongruent', 'Incongruent')
    ], string='Congruence')
    
    # Perceptual disturbances
    perceptual_disturbances = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], string='Perceptual Disturbances')
    
    sense_distortion = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Probable', 'Probable')
    ], string='Sense Distortion')
    
    body_image_disturb = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Probable', 'Probable')
    ], string='Body Image Disturbance')
    
    sense_deception = fields.Selection([
        ('Hallucination', 'Hallucination'),
        ('Pseudo-Hallucination', 'Pseudo-Hallucination'),
        ('Imagery', 'Imagery'),
        ('Illusion', 'Illusion')
    ], string='Sense Deception')
    
    hallucination_illusion = fields.Selection([
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Probable', 'Probable')
    ], string='Hallucination/Illusion')
    
    sensory_modality = fields.Selection([
        ('Auditory', 'Auditory'),
        ('Visual', 'Visual'),
        ('Tactile', 'Tactile'),
        ('Gustatory', 'Gustatory'),
        ('Olfactory', 'Olfactory not a first hand symptom'),
    ], string='Sensory Modality')
    
    first_rank_symptom = fields.Selection([
        ('hypnogogic', 'Hypnagogic hallucination(While sleeping)'),
        ('hypnoponmic', 'Hypnoponmic hallucination(While waking up)'),
    ], string='First Rank Symptom')
    
    depersonalization = fields.Selection([
        ('Present', 'Present'),
        ('probable', 'Probable'),
        ('Absent', 'Absent')
    ], string='Depersonalization')
    
    hallucinations_describe = fields.Text(string='Describe Hallucinations')
    
    # Cognitive functions
    attention = fields.Selection([
        ('easily_sustained', 'Easily aroused & sustained'),
        ('easy_not_sustained', 'Easy to arouse but not sustained'),
        ('difficult_sustain', 'Difficult to arouse and sustain'),
        ('difficult_sustained', 'Difficult to arouse but sustained'),
        ('distractible', 'Distractible'),
      
    ], string='Attention and Concentration')
    
    orientation = fields.Selection([
        ('time_present', 'Time(P/A)'),
        ('date_present', 'Date(P/A)'),
        ('day_present', 'DAY(P/A)'),
        ('month_present', 'Month(P/A)'),
        ('year_present', 'Year(P/A)'),
        ('place_present', 'Place(P/A)'),
        ('state_present', 'State(P/A)'),
        ('country_present', 'Country(P/A)'),
        ('relatives_present', 'Person- relatives(P/A)'),
        ('staff_present', 'hospital staff (P/A)'),
        ('self_present', 'Self(P/A)')
    ], string='Orientation')
    
    memory = fields.Selection([
        ('Normal', 'Normal'),
        ('Impaired', 'Impaired')
    ], string='Memory')
    
    assess_by = fields.Selection([
        ('Clinical Behavior', 'Clinical Behavior'),
        ('Formal Tests', 'Formal Tests')
    ], string='Assess By')
    
    short_term_immediate = fields.Text(string='Short Term: Immediate')
    short_term_recent = fields.Text(string='Short Term: Recent')
    long_time_remote = fields.Text(string='Long Time: Remote')
    
    intelligence = fields.Selection([
        ('Below Average', 'Below Average'),
        ('Average', 'Average'),
        ('Above Average', 'Above Average')
    ], string='Intelligence')
    
    general_fund_information = fields.Text(string='General Fund of Information')
    comprehension = fields.Text(string='Comprehension')
    simple_arithmetic = fields.Text(string='Simple Arithmetic')
    
    abstract_thinking = fields.Selection([
        ('intact', 'Intact'),
        ('Impaired', 'Impaired'),
        ('Concentrate', 'Concentrate'),
        ('conceptual', 'Conceptual'),
        ('functional', 'Functional'),
        ('abstract', 'Abstract'),
    ], string='Abstract Thinking')
    
    differences = fields.Text(string='Differences')
    similarities = fields.Text(string='Similarities')
    proverb = fields.Text(string='Proverb')
    
    judgement = fields.Selection([
        ('Normal', 'Normal'),
        ('Impaired', 'Impaired')
    ], string='Judgement')
    
    test = fields.Text(string='Test')
    social = fields.Text(string='Social')
    personal = fields.Text(string='Personal')
    
    insight = fields.Selection([
        ('present', 'Present'),
        ('partial', 'Partial'),
        ('Impaired', 'Impaired')
    ], string='Insight')
    
    grade_1 = fields.Boolean(string='Grade I: Absence of Insight')
    grade_2 = fields.Boolean(string='Grade II: Complete denial of illness')
    grade_3 = fields.Boolean(string='Grade III: Slight awareness of being sick and needing help')
    grade_4 = fields.Boolean(string='Grade IV: Aware of being sick but blaming it on others, external factors')
    grade_5 = fields.Boolean(string='Grade V: Intellectual insight')
    grade_6 = fields.Boolean(string='Grade VI: True emotional insight')
    summary = fields.Text(string='Summary')
      # Basic patient information - missing name field
    name = fields.Char(string='Name', related='patient_id.name', store=True)
    
    # Social Functioning - Fields related to self-harm, social interactions, and tendencies
    self_harm_specify = fields.Text(string='Specify Self Harm')
    
    self_harm_others = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Self harm to others')
    
    self_harm_others_specify = fields.Text(string='Specify Self Harm to Others')
    
    goes_out = fields.Selection([
        ('Severely Abnormal', 'Severely Abnormal'),
        ('Moderately Abnormal', 'Moderately Abnormal'),
        ('Normal', 'Normal')
    ], string='Goes out')
    
    # Override these fields to be Boolean for visibility control
    suicidal_tendency = fields.Boolean(string='Suicidal Tendency', default=False)
    violence_tendency = fields.Boolean(string='Violence Tendency', default=False)
    
    # Suicidal Risk Assessment Fields
    date_assessment = fields.Date(string='Date of Assessment')
    date_attempt = fields.Date(string='Date of Attempt')
    patient_reliability = fields.Selection([
        ('reliable', 'Reliable'),
        ('unreliable', 'Unreliable'),
        ('partially_reliable', 'Partially Reliable')
    ], string='Patient Reliability')
    
    informant_reliability = fields.Selection([
        ('reliable', 'Reliable'),
        ('unreliable', 'Unreliable'),
        ('partially_reliable', 'Partially Reliable')
    ], string='Informant Reliability')
    
    patient_adequency = fields.Selection([
        ('adequate', 'Adequate'),
        ('inadequate', 'Inadequate'),
        ('partially_adequate', 'Partially Adequate')
    ], string='Patient Adequacy')
    
    informant_adequency = fields.Selection([
        ('adequate', 'Adequate'),
        ('inadequate', 'Inadequate'),
        ('partially_adequate', 'Partially Adequate')
    ], string='Informant Adequacy')
    
    #
    suicidal_lines = fields.One2many('hospital.suicidal.assessment.line', 'case_history_id', string='Suicidal Assessment Lines')
    total_score = fields.Integer(string='Total Score', compute='_compute_total_score', store=True)
    
    # Violence Risk Assessment Fields
    violence_assessment_date = fields.Date(string='Violence Assessment Date')
    
    # Historical Scale
    previous_violence = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Previous Violence')
    
    young_age = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Young Age')
    
    relnship_instability = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Relationship Instability')
    
    emp_prblms = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Employment Problems')
    
    substance_prblms = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Substance Problems')
    
    major_illness_violence = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Major Illness Violence')
    
    psycopathy = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Psychopathy')
    
    early_adjustment = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Early Adjustment')
    
    personality_disorder = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Personality Disorder')
    
    supervision_failure = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Supervision Failure')
    
    # Clinical Scale
    lack_insight = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Lack of Insight')
    
    neg_attitute = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Negative Attitude')
    
    active_symp_major_illness = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Active Symptoms of Major Illness')
    
    impulsivity = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Impulsivity')
    
    unresponsive_treatment = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Unresponsive to Treatment')
    
    # Risk Management Scale
    feasibility = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Feasibility')
    
    destabilizers = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Destabilizers')
    
    personal_support = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Personal Support')
    
    noncompliance_remediation_attempt = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Noncompliance Remediation Attempt')
    
    stress = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Stress')
    
    # Computed field for total score
    @api.depends('suicidal_lines.score')
    def _compute_total_score(self):
        for record in self:
            record.total_score = sum(record.suicidal_lines.mapped('score'))
    
    # Method for getting questions button
    def get_questions(self):
        """Method to populate suicidal assessment questions"""
        # Create suicidal assessment lines with predefined questions
        questions = self.env['hospital.suicidal.question'].search([])
        
        # Clear existing lines
        self.suicidal_lines.unlink()
        
        # Create new lines for each question
        lines = []
        for i, question in enumerate(questions, 1):
            lines.append({
                'serial_number': i,
                'quen_id': question.id,
                'case_history_id': self.id,
            })
        
        if lines:
            self.env['hospital.suicidal.assessment.line'].create(lines)
        
        return True

    @api.model_create_multi
    def create(self, vals_list):
        return super(CaseHistory, self).create(vals_list)
    
    def action_save(self):
        return True
    
    def action_discard(self):
        return {'type': 'ir.actions.act_window_close'}

class ChiefComplaint(models.Model):
    _name = 'hospital.chief.complaint'
    _description = 'Chief Complaint'
    _order = 'sequence, id'
    
    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    chrono_no = fields.Integer(string='Chrono. Order')
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    chief_compaints = fields.Text(string='Chief Complaints', required=True)
    duration = fields.Char(string='Duration')
    year = fields.Char(string='Year')


class PsychiatricMedication(models.Model):
    _name = 'hospital.psychiatric.medication'
    _description = 'Psychiatric Medication'
    
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    name = fields.Char(string='Name of Medication', required=True)
    dosage = fields.Char(string='Dosage')
    frequency = fields.Char(string='Frequency')
    administration = fields.Char(string='Administration')
    prescriber_name = fields.Char(string='Prescribers Name')


class GeneralMedication(models.Model):
    _name = 'hospital.general.medication'
    _description = 'General Medication'
    
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    name = fields.Char(string='Name of Medication', required=True)
    dosage = fields.Char(string='Dosage')
    frequency = fields.Char(string='Frequency')
    administration = fields.Char(string='Administration')
    prescriber_name = fields.Char(string='Prescribers Name')


class PsychiatricEffect(models.Model):
    _name = 'hospital.psychiatric.effect'
    _description = 'Psychiatric Medication Effect'
    
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    name = fields.Char(string='Name of Medication', required=True)
    side_effects = fields.Text(string='Side Effects')
    actions_taken = fields.Text(string='Actions Taken')


class GeneralEffect(models.Model):
    _name = 'hospital.general.effect'
    _description = 'General Medication Effect'
    
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    name = fields.Char(string='Name of Medication', required=True)
    side_effects = fields.Text(string='Side Effects')
    actions_taken = fields.Text(string='Actions Taken')


class RiskAssessment(models.Model):
    _name = 'hospital.risk.assessment'
    _description = 'Risk Assessment'
    
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    name = fields.Char(string='Risk Type')
    never = fields.Boolean(string='Never')
    past_week_month = fields.Boolean(string='Past Week - Month')
    past_month_year = fields.Boolean(string='Past Month - Year')
    past_2_years = fields.Boolean(string='Past 2 Years')
    details = fields.Text(string='Details')


class PhysicalIllness(models.Model):
    _name = 'hospital.physical.illness'
    _description = 'Physical Illness'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

class HospitalPsychiatricIllness(models.Model):
    _name = 'hospital.psychiatric.illness'
    _description = 'Psychiatric Illness'

    name = fields.Char(string='Illness Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

    
class PsychomotorActivity(models.Model):
    _name = 'hospital.psychomotor.activity'
    _description = 'Psychomotor Activity'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)


class CatatonicSign(models.Model):
    _name = 'hospital.catatonic.sign'
    _description = 'Catatonic Sign'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

class PatientOccupation(models.Model):
    _name = 'hospital.patient.occupation'
    _description = 'Patient Occupation'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)


class PatientRelationship(models.Model):
    _name = 'hospital.patient.relationship'
    _description = 'Patient Relationship'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)


class SuicidalQuestion(models.Model):
    _name = 'hospital.suicidal.question'
    _description = 'Suicidal Assessment Question'
    
    name = fields.Char(string='Question', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)


class SuicidalAnswer(models.Model):
    _name = 'hospital.suicidal.answer'
    _description = 'Suicidal Assessment Answer'
    
    name = fields.Char(string='Answer', required=True)
    question_id = fields.Many2one('hospital.suicidal.question', string='Question', required=True)
    score = fields.Integer(string='Score', default=0)
    active = fields.Boolean(default=True)


class SuicidalAssessmentLine(models.Model):
    _name = 'hospital.suicidal.assessment.line'
    _description = 'Suicidal Assessment Line'
    
    case_history_id = fields.Many2one('case.history', string='Case History', ondelete='cascade')
    serial_number = fields.Integer(string='Serial Number')
    quen_id = fields.Many2one('hospital.suicidal.question', string='Question', required=True)
    ans_id = fields.Many2one('hospital.suicidal.answer', string='Answer')
    score = fields.Integer(string='Score', related='ans_id.score', store=True)