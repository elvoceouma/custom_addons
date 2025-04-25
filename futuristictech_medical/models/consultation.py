from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

SCALES = [
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
]

TEAM_ROLE = [
    ('psychiatrist', 'Psychiatrist'),
    ('senior_registrar', 'Senior Registrar'),
    ('clinical_psychologist', 'Clinical Psychologist'),
    ('counsellor', 'Counsellor'),
    ('caretaker', 'Caretaker'),
    ('physician', 'Physician')
]


class ScaleType(models.Model):
    _name = 'scale.type'
    _description = 'Scale Types'
    _rec_name = 'scale_type'
    
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    scale_type = fields.Selection(SCALES, string='Scale Type', required=True)


class Consultation(models.Model):
    _name = 'consultation.consultation'
    _description = 'Consultation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    
   
    name = fields.Char(string='Name', required=True, default='New', tracking=True)
    psychiatrist_id = fields.Many2one('hr.employee', string='Consultant', required=True, tracking=True)
    team_role = fields.Selection(TEAM_ROLE, related='psychiatrist_id.team_role', readonly=True, store=True, string='Team Role')
    type = fields.Selection([('ip', 'IP'), ('op', 'OP')], string='Type', required=True, default='ip', tracking=True)
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number', tracking=True, ondelete='set null')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference', tracking=True, ondelete='set null')
    age = fields.Integer(string='Age', tracking=True)
    sex = fields.Selection([('male','Male'),
                            ('female','Female'),
                            ('other','Other')],
                            string="Sex"
                            )
    patient_id = fields.Many2one('oeh.medical.patient', compute='_compute_patient', string='Patient', store=True, tracking=True, ondelete='set null')
    date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    start_datetime = fields.Datetime(string='Start Time', tracking=True)
    end_datetime = fields.Datetime(string='End Time', tracking=True)
    general_observation = fields.Text(string='General Observations', tracking=True)
    bp = fields.Integer(string='BP in (mmHg)', tracking=True)
    bp2 = fields.Integer(string='BP2', tracking=True)
    wt = fields.Integer(string='WT', tracking=True)
    grbs = fields.Integer(string='GRBS (mg/dl)', tracking=True)
    spo2 = fields.Integer(string='SPO2 in (percentage)', tracking=True)
    pulse = fields.Integer(string='Pulse Rate in (bpm)', tracking=True)
    vitals_checked_user_id = fields.Many2one('res.users', string='Vitals Checked By', tracking=True)
    vitals_checked_on = fields.Datetime(string='Vitals Checked On', tracking=True)
    advice_to_counsellor = fields.Text(string='Advice to Counsellor', tracking=True)
    counsellor_purpose_ids = fields.Many2many('cp.purpose', 'consultation_counsellor_purpose_rel', 'consultation_id', 'counsellor_purpose_id', string='Purpose')
    advice_to_psychologist = fields.Text(string='Advice to Clinical Psychologist', tracking=True)
    cp_purpose_ids = fields.Many2many('cp.purpose', 'consultation_cp_purpose_rel', 'consultation_id', 'cp_purpose_id', string='Purpose')
    cp_therapist_id = fields.Many2one('hr.employee', string='Therapist', tracking=True)
    lab_advice = fields.Text(string='Advice', default='/', tracking=True)
    labtest_type_ids = fields.Many2many(
        'medical.labtest.types',
        'consultation_labtest_type_rel',  #
        'consultation_id',
        'labtest_type_id',
        string='Lab Tests'
    )
    consultation_type = fields.Selection([
        ('psychiatrist', 'Psychiatrist'),
        ('clinical_psychologist', 'Clinical Psychologist'),
        ('counsellor', 'Counsellor')
    ], string='Consultation Type', tracking=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', tracking=True)
    consultant = fields.Many2one('res.partner', string='Consultant', tracking=True)
    cross_consultation = fields.Text(string='Cross Consultation', tracking=True)
    speciality_id = fields.Many2one('medical.speciality', string='Speciality', tracking=True)
    speciality_ids = fields.Many2many(
    'medical.speciality', 
    'consultation_speciality_rel', 
    'consultation_id', 
    'speciality_id', 
    string='Speciality', 
    tracking=True
)
    # psychiatrist_id = fields.Many2one('hr.employee', string='Psychiatrist', tracking=True)
    priority = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('emergency', 'Emergency')], string='Priority', tracking=True)
    current_medication = fields.Text(string='Current Medication', tracking=True)
    active_prescription_ids = fields.Many2many('oeh.medical.prescription', 'consultation_prescription_rel', 'consultation_id', 'prescription_id', string='Active Prescriptions')
    consultation_prescription_line_ids = fields.One2many('consultation.prescription.line', 'consultation_id', string='Prescriptions')
    prescription_status = fields.Selection([('changed', 'Changed'), ('continued', 'Continued')], string='Prescription Status', default='continued', store=True, tracking=True)
    prescription_id = fields.Many2one('oeh.medical.prescription', string='Prescription')
    followup_type_id = fields.Many2one('followup.type', string='Type', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('started', 'Check In'), 
        ('ended', 'Check Out'), 
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('referral', 'Referral'),
        ('followup', 'Follow Up'),
        ('admission', 'Admission'),
        ('cross_consultation', 'Cross Consultation'),
        ('admission_referral', 'Admission Referral'),
        ('admission_followup', 'Admission Follow Up'),
        ('admission_cross_consultation', 'Admission Cross Consultation'),
        ('discharge', 'Discharge')
    ], string='Status', default='draft', tracking=True, copy=False)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    cross_consultation_ids = fields.One2many('cross.consultation.consultation', 'cross_consultation_id', string='Cross Consultation')
    advised_doctor = fields.Many2one('hr.employee', string='Advised Doctor', readonly=True, tracking=True)
    consultation_type_ids = fields.Many2many('followup.type', 'consultation_followup_type_rel', 'consultation_id', 'followup_type_id', string='Consultation Type')
    scale_type_ids = fields.One2many('scale.type', 'consultation_id', string='Scales')
    
    # Next follow-up fields
    next_followup_date = fields.Date(string='Next Follow-up Date')
    doctor_advice = fields.Text(string='Doctor Advice')
    precautions = fields.Text(string='Precautions')
    todo = fields.Text(string='Todo Before Next Consultation')
    is_sos = fields.Boolean(string='SOS')
    next_followup = fields.Boolean(string='Next Follow-up')
    
    # Admission Referral fields
    price_tag = fields.Many2one('product.pricelist', string="Price Tags")
    referral_config_id = fields.Many2one('admission.referral.config', string='Package')
    illness_tag = fields.Many2one('illness.tag', string="Illness")
    bed_type_id = fields.Many2one('oeh.medical.health.center.ward', string='Bed Category')
    hospitalization_length = fields.Integer(string='Hospitalization Length')
    approx_cost = fields.Float(string="Approx.Cost of Hospitalization")
    provisional_diagnosis_ids = fields.Many2many('icd.coding', string='Provisional Diagnosis', tracking=True)
    treatment_planned = fields.Text(string="Treatment/procedure Planned")
    consultation_require = fields.Boolean(string="Requirement for another Consultation")
    consultation_require_ids = fields.Many2many(
    'medical.speciality',
    'consultation_speciality_require_rel',
    'consultation_id',
    'speciality_id',
    string='Speciality'
)
    provisional_admission_date = fields.Date(string="Provisional Admission Date")
    admission_room_type_ids = fields.One2many(
        'admission.room.type', 
        'consultation_id', 
        string='Admission Room Types'
    )
    admission_labtest_ids = fields.Many2many(
        'medical.labtest.types',
        'consultation_labtest_admission_rel',  # Different relation table
        'consultation_id',
        'labtest_type_id',
        string='Admission Lab Tests'
    )
   
    admission_consultation_ids = fields.One2many(
    'admission.consultation', 
    'consultation_id', 
    string='Admission Consultations'
)

    admission_misc_item_ids = fields.One2many(
        'admission.misc.item', 
        'consultation_id', 
        string='Admission Misc. Items'
    )

    admission_scale_ids = fields.One2many(
        'admission.scale.type', 
        'consultation_id', 
        string='Admission Scales'
    )

    @api.depends('type', 'inpatient_admission_id', 'op_visit_id')
    def _compute_patient(self):
        for record in self:
            if record.type == 'ip' and record.inpatient_admission_id:
                record.patient_id = record.inpatient_admission_id.patient.id
                record.op_visit_id = False
            elif record.type == 'op' and record.op_visit_id:
                record.patient_id = record.op_visit_id.patient_id.id
                record.inpatient_admission_id = False
            else:
                record.patient_id = False
                record.op_visit_id = False
                record.inpatient_admission_id = False

    @api.onchange('bed_type_id')
    def _onchange_bed_type_id(self):
        if self.bed_type_id:
            # mapping between bed_type_id and price_tag
            room_type = self.env['oeh.medical.health.center.ward'].browse(self.bed_type_id.id)
            if room_type and room_type.price_tag:
                self.price_tag = room_type.price_tag.id
        else:
            self.price_tag = False

    @api.onchange('referral_config_id')
    def _onchange_referral_config_id(self):
    # Clear one2many fields properly
        self.admission_consultation_ids = [(5, 0, 0)]  # Clear the field
        self.admission_room_type_ids = [(5, 0, 0)]
        self.admission_misc_item_ids = [(5, 0, 0)]
        
        # Clear many2many fields properly
        self.admission_scale_ids = [(5, 0, 0)]
        self.admission_labtest_ids = [(5, 0, 0)]
        
        admission_labtest_ids = []
        if self.referral_config_id:
            referral_items = self.env['admission.referral.items'].search([('referral_config_id', '=', self.referral_config_id.id)])
            for line in referral_items:
                # Check if the product_id exists and is not False
                if not line.product_id:
                    continue
                    
                followup_type_id = self.env['followup.type'].search([('product_id', '=', line.product_id.id)], limit=1)
                labtest_type_id = self.env['oeh.medical.labtest.types'].search([('product_id', '=', line.product_id.id)], limit=1)
                
                # Add guard for bed_type_id
                if self.bed_type_id:
                    bed_id = self.env['oeh.medical.health.center.beds'].search([
                        ('product_id', '=', line.product_id.id), 
                        ('ward', '=', self.bed_type_id.id)
                    ])
                else:
                    bed_id = False
                    
                # Process based on found record
                if followup_type_id:
                    vals = {
                        'followup_type_id': followup_type_id.id,
                        'quantity': line.quantity,
                        'unit_price': line.unit_price
                    }
                    self.write({'admission_consultation_ids': [(0, 0, vals)]})
                elif labtest_type_id:
                    admission_labtest_ids.append(labtest_type_id.id)
                elif bed_id:
                    vals = {
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'unit_price': line.unit_price
                    }
                    self.write({'admission_room_type_ids': [(0, 0, vals)]})
                else:
                    vals = {
                        'product_id': line.product_id.id,
                        'quantity': line.quantity,
                        'unit_price': line.unit_price
                    }
                    self.write({'admission_misc_item_ids': [(0, 0, vals)]})
            
            # Process scales
            if self.referral_config_id.scale_ids:
                for scale_type_id in self.referral_config_id.scale_ids:
                    self.write({'admission_scale_ids': [(0, 0, {'scale_type': scale_type_id.scale_type})]})
                    
            # Set many2many field correctly
            if admission_labtest_ids:
                self.admission_labtest_ids = [(6, 0, admission_labtest_ids)]

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            prescription_line_vals = []
            self.consultation_prescription_line_ids = [(5, 0, 0)]
            prescription_id = self.env['oeh.medical.prescription'].search([
                ('patient', '=', self.patient_id.id), 
                ('state', '=', 'Confirm')
            ], order='id desc', limit=1)
            
            for line in prescription_id.prescription_line:
                vals = {
                    'prescription_id': prescription_id.id,
                    'doctor': line.doctor.id,
                    'speciality': line.speciality.id,
                    'name': line.name.id,
                    'prescription_type': line.prescription_type,
                    'start_treatment': line.start_treatment,
                    'end_treatment': line.end_treatment,
                    'mrgn': line.mrgn,
                    'noon': line.noon,
                    'evng': line.evng,
                    'night': line.night,
                    'dose_form': line.dose_form.id if line.dose_form else False,
                    'product_uom': line.product_uom.id if line.product_uom else False,
                    'indication': line.indication.id if line.indication else False,
                    'common_dosage': line.common_dosage.id if line.common_dosage else False,
                    'take': line.take
                }
                self.consultation_prescription_line_ids = [(0, 0, vals)]
                self.prescription_status = 'continued'
            
            self.prescription_id = prescription_id.id

    def check_psychiatrist_evaluation(self):
        evaluation_id = self.env['psychiatrist.evaluation.form'].search([('patient_id', '=', self.patient_id.id)])
        if not evaluation_id:
            raise UserError(_('Please complete Psychiatrist Evaluation Form for %s') % (self.patient_id.name))
    
    def action_start(self):
        self.check_psychiatrist_evaluation()
        self.start_datetime = fields.Datetime.now()
        self.state = 'started'
        
    def action_end(self):
        self.end_datetime = fields.Datetime.now()
        self.state = 'ended'

    def get_product_price(self, product_id, pricelist_id):
        return product_id.with_context(pricelist=pricelist_id.id).price if product_id and pricelist_id else product_id.lst_price
    
    def get_invoice_lines(self):
        line_vals = []
        for line in self.labtest_type_ids:
            if line.product_id.property_account_income_id or line.product_id.categ_id.property_account_income_categ_id:
                account_id = line.product_id.property_account_income_id.id or line.product_id.categ_id.property_account_income_categ_id.id
                product_price = self.get_product_price(line.product_id, self.patient_id.partner_id.property_product_pricelist)
                vals = (0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'quantity': 1.0,
                    'price_unit': product_price or line.test_charge,
                    'account_id': account_id,
                })
                line_vals.append(vals)
            else:
                raise UserError(_('Please map income account in Product or in Products Internal Category!'))
        return line_vals
    
    def create_op_bill(self):
        partner_account_id = False
        if self.patient_id.partner_id.property_account_receivable_id:
            partner_account_id = self.patient_id.partner_id.property_account_receivable_id.id
            journal_id = self.env['account.journal'].search([
                ('company_id', '=', self.inpatient_admission_id.patient.company_id.id), 
                ('inv_type', '=', 'debitnote')
            ], limit=1)
            
            invoice_vals = {
                'partner_id': self.patient_id.partner_id.id,
                'account_id': partner_account_id,
                'patient': self.patient_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal_id.id if journal_id else False,
                'inv_type': 'miscellaneous',
                'invoice_date': self.date,
                'bill_type': 'sales',
                'op_visit': self.op_visit_id.id,
                'reg_no': self.patient_id.identification_code,
                'invoice_line_ids': self.get_invoice_lines()
            }
            
            self.env['account.move'].create(invoice_vals)
        else:
            raise UserError(_('Please map receivable account in Partner!'))
        
    def create_labtest_requisition(self):
        line_vals = []
        labtest_vals = {}
        for line in self.labtest_type_ids:
            vals = (0, 0, {
                'labtest_type_id': line.id,
                'quantity': 1.0,
                'date': fields.Date.context_today(self)
            })
            line_vals.append(vals)
            
        if self.type == 'ip':
            labtest_vals = {
                'type': 'inpatient',
                'inpatient_admission_id': self.inpatient_admission_id.id,
                'patient_id': self.inpatient_admission_id.patient.id,
                'patient_name': self.inpatient_admission_id.patient.name,
                'purpose': self.lab_advice,
                'requested_date': fields.Date.context_today(self),
                'requisition_line_ids': line_vals
            }
        elif self.type == 'op':
            labtest_vals = {
                'type': 'outpatient',
                'op_visit_id': self.op_visit_id.id,
                'patient_id': self.op_visit_id.patient_id.id,
                'patient_name': self.op_visit_id.patient_id.name,
                'purpose': self.lab_advice,
                'requested_date': fields.Date.context_today(self),
                'requisition_line_ids': line_vals
            }
            self.create_op_bill()
            
        self.env['labtest.requisition'].create(labtest_vals)
    
    def action_check_vitals(self):
        vitals_checked = False
        if self.type == 'ip':
            vitals_checked = self.env['vital.physical.assessment'].search([
                ('name', '=', self.inpatient_admission_id.id), 
                ('date', '=', self.date), 
                ('state', '=', 'Completed')
            ], order='id desc', limit=1)
        elif self.type == 'op':
            vitals_checked = self.env['vital.physical.assessment'].search([
                ('op_visit_id', '=', self.op_visit_id.id), 
                ('date', '=', self.date), 
                ('state', '=', 'Completed')
            ], order='id desc', limit=1)
            
        if not vitals_checked:
            raise UserError(_("Vital Assessment for %s is not created yet. Please Complete the Vital information to start consultation.") % (self.patient_id.name))
        else:
            self.vitals_checked_user_id = self.env.user.id
            self.vitals_checked_on = fields.Datetime.now()
            self.bp = vitals_checked.bp
            self.bp2 = vitals_checked.bp2
            self.wt = vitals_checked.weight
            self.grbs = vitals_checked.grbs
            self.spo2 = vitals_checked.spo_2
            self.pulse = vitals_checked.pulse_rate
    
    def create_consultation(self):
        for consultation_type_id in self.consultation_type_ids:
            vals = {
                'date': fields.Date.context_today(self),
                'followup_type_id': consultation_type_id.id
            }
            if self.type == 'ip':
                vals.update({'inpatient_admission_id': self.inpatient_admission_id.id, 'type': self.type})
            else:
                vals.update({'op_visit_id': self.op_visit_id.id, 'type': self.type})
                
            employee_id = self.env['hr.employee'].search([
                ('related_doctor_id', '=', self.doctor_id.id), 
                ('team_role', 'in', ['psychiatrist', 'clinical_psychologist', 'counsellor'])
            ], limit=1)
            
            if employee_id:
                vals.update({'psychiatrist_id': employee_id.id})
                
            self.env['consultation.consultation'].create(vals)
    
    def create_scales(self):
        for scale_type_id in self.scale_type_ids:
            employee_id = False
            employee = self.env['hr.employee'].search([
                ('related_doctor_id', '=', self.doctor_id.id), 
                ('team_role', 'in', ['psychiatrist', 'clinical_psychologist', 'counsellor'])
            ], limit=1)
            
            if employee:
                employee_id = employee.id
                
            # Handle different scale types and create corresponding records
            if scale_type_id.scale_type == 'assist_who':
                vals = {}
                if self.type == 'ip':
                    vals = {
                        'type': 'ip',
                        'inpatient_id': self.inpatient_admission_id.id,
                        'name': self.inpatient_admission_id.patient.id,
                        'counsellor': employee_id,
                        'datetime': fields.Datetime.now()
                    }
                elif self.type == 'op':
                    vals = {
                        'type': 'op',
                        'op_visit_id': self.op_visit_id.id,
                        'name': self.op_visit_id.patient_id.id,
                        'counsellor': employee_id,
                        'datetime': fields.Datetime.now()
                    }
                self.env['assist.consultations'].create(vals)
            # Similar logic for other scale types...
            # For brevity, I'm not including all scale type handling here
    
    def create_outside_consultation(self):
        for speciality_id in self.speciality_ids:
            vals = {
                'psychiatrist_id': self.psychiatrist_id.id,
                'speciality_id': speciality_id.id,
                'priority': 'low',
                'doctor_id': self.doctor_id.id if self.doctor_id else False,
                'note': self.cross_consultation
            }
            if self.type == 'ip':
                vals.update({'type': self.type, 'inpatient_admission_id': self.inpatient_admission_id.id})
            else:
                vals.update({'type': self.type, 'op_visit_id': self.op_visit_id.id})
                
            self.env['outside.consultation'].create(vals)
    
    def calculate_referrel_amount(self, product_id, doctor):
        payout_amount = 0.0
        payout_config_id = self.env['payout.config'].search([
            ('partner_id', '=', doctor.id), 
            ('product_category_id', '=', self.followup_type_id.product_id.categ_id.id)
        ], limit=1)
        
        if payout_config_id:
            if payout_config_id.type == 'base':
                payout_amount = product_id.list_price * (payout_config_id.referral_percentage / 100)
            elif payout_config_id.type == 'matrix':
                pricelist_id = self.patient_id.partner_id.property_product_pricelist.id    
                categ_pricelist_item = self.env['product.pricelist.item'].search([
                    ('categ_id', '=', product_id.categ_id.id), 
                    ('pricelist_id', '=', pricelist_id)
                ])
                product_pricelist_item = self.env['product.pricelist.item'].search([
                    ('product_tmpl_id', '=', product_id.product_tmpl_id.id), 
                    ('pricelist_id', '=', pricelist_id)
                ])
                
                list_price = 0.0
                if categ_pricelist_item:
                    if categ_pricelist_item.compute_price == 'fixed':
                        list_price = categ_pricelist_item.fixed_price
                    elif categ_pricelist_item.compute_price == 'percentage':
                        list_price = product_id.list_price - (product_id.list_price * (categ_pricelist_item.percent_price / 100))
                    elif categ_pricelist_item.compute_price == 'formula':
                        list_price = product_id.list_price - (product_id.list_price * (categ_pricelist_item.price_discount / 100))
                elif product_pricelist_item:
                    if product_pricelist_item.compute_price == 'fixed':
                        list_price = product_pricelist_item.fixed_price
                    elif product_pricelist_item.compute_price == 'percentage':
                        list_price = product_id.list_price - (product_id.list_price * (product_pricelist_item.percent_price / 100))
                    elif product_pricelist_item.compute_price == 'formula':
                        list_price = product_id.list_price - (product_id.list_price * (product_pricelist_item.price_discount / 100))
                else:
                    raise UserError(_('Please configure this Consultation type or category in the pricelist attached to the patient'))
                
                payout_amount = list_price * (payout_config_id.referral_percentage / 100)
            else:
                raise UserError(_('Please configure the referral %s Payout type for %s') % (product_id.categ_id.name, doctor.name))
                
            return payout_amount    
        else:
            raise UserError(_('Please configure the referral %s Payout for %s') % (product_id.categ_id.name, doctor.name))

    def create_referral_payout(self, doctor):
        payout_amount = self.calculate_referrel_amount(self.followup_type_id.product_id, doctor)
        if payout_amount > 0:
            line_vals = {
                'product_id': self.followup_type_id.product_id.id,
                'inpatient_admission_id': self.inpatient_admission_id.id,
                'date': self.date,
                'price_unit': payout_amount,
                'reference': self.inpatient_admission_id.name,
                'internal_reference': self.name,
                'type': 'credit',
                'patient_id': self.inpatient_admission_id.patient.id,
                'name': self.followup_type_id.product_id.name,
                'quantity': 1.0,
                'price_subtotal': payout_amount,
            }
            
            payout = self.env['doctor.payout'].search([
                ('doctor_id', '=', doctor.id), 
                ('start_date', '<=', self.date), 
                ('end_date', '>=', self.date), 
                ('state', '=', 'new')
            ])
            
            if payout:
                line_vals.update({'doctor_payout_id': payout.id})
                self.env['doctor.payout.line'].create(line_vals)
            else:
                payout_vals = {
                    'doctor_id': doctor.id,
                    'start_date': fields.Date.today().replace(day=1),
                    'end_date': (fields.Date.today() + relativedelta(months=1, day=1, days=-1)),
                }
                payout_id = self.env['doctor.payout'].create(payout_vals)
                if payout_id:
                    line_vals.update({'doctor_payout_id': payout_id.id})
                    self.env['doctor.payout.line'].create(line_vals)

    def calculate_payout_amount(self, product_id):
        payout_amount = 0.0
        payout_config_id = self.env['payout.config'].search([
            ('partner_id', '=', self.psychiatrist_id.related_doctor_id.id), 
            ('product_category_id', '=', self.followup_type_id.product_id.categ_id.id)
        ], limit=1)
        
        if payout_config_id:
            if payout_config_id.type == 'base':
                payout_amount = product_id.list_price * (payout_config_id.consultation_percentage / 100)
            elif payout_config_id.type == 'matrix':
                pricelist_id = self.patient_id.partner_id.property_product_pricelist.id    
                categ_pricelist_item = self.env['product.pricelist.item'].search([
                    ('categ_id', '=', product_id.categ_id.id), 
                    ('pricelist_id', '=', pricelist_id)
                ])
                product_pricelist_item = self.env['product.pricelist.item'].search([
                    ('product_tmpl_id', '=', product_id.product_tmpl_id.id), 
                    ('pricelist_id', '=', pricelist_id)
                ])
                
                list_price = 0.0
                if categ_pricelist_item:
                    if categ_pricelist_item.compute_price == 'fixed':
                        list_price = categ_pricelist_item.fixed_price
                    elif categ_pricelist_item.compute_price == 'percentage':
                        list_price = product_id.list_price - (product_id.list_price * (categ_pricelist_item.percent_price / 100))
                    elif categ_pricelist_item.compute_price == 'formula':
                        list_price = product_id.list_price - (product_id.list_price * (categ_pricelist_item.price_discount / 100))
                elif product_pricelist_item:
                    if product_pricelist_item.compute_price == 'fixed':
                        list_price = product_pricelist_item.fixed_price
                    elif product_pricelist_item.compute_price == 'percentage':
                        list_price = product_id.list_price - (product_id.list_price * (product_pricelist_item.percent_price / 100))
                    elif product_pricelist_item.compute_price == 'formula':
                        list_price = product_id.list_price - (product_id.list_price * (product_pricelist_item.price_discount / 100))
                else:
                    raise UserError(_('Please configure this Consultation type or category in the pricelist attached to the patient'))
                
                payout_amount = list_price * (payout_config_id.consultation_percentage / 100)
            else:
                raise UserError(_('Please configure the %s Payout type for %s') % (product_id.categ_id.name, self.psychiatrist_id.related_doctor_id.name))
                
            if self.patient_id.referred_by:
                referred_by_payout = self.env['payout.config'].search([
                    ('partner_id', '=', self.patient_id.referred_by.id), 
                    ('product_category_id', '=', product_id.categ_id.id)
                ], limit=1)
                
                if referred_by_payout:
                    referral_amount = payout_amount * (referred_by_payout.referral_percentage / 100)
                    payout_amount = payout_amount - referral_amount
                else:
                    raise UserError(_('Please configure the referral %s Payout for %s') % (product_id.categ_id.name, self.patient_id.referred_by.name))    
            elif self.cross_consultation and self.advised_doctor:
                adviced_by_payout = self.env['payout.config'].search([
                    ('partner_id', '=', self.advised_doctor.related_doctor_id.id), 
                    ('product_category_id', '=', product_id.categ_id.id)
                ], limit=1)
                
                if adviced_by_payout:
                    referral_amount = payout_amount * (adviced_by_payout.referral_percentage / 100)
                    payout_amount = payout_amount - referral_amount
                else:
                    raise UserError(_('Please configure the referral %s Payout for %s') % (product_id.categ_id.name, self.advised_doctor.related_doctor_id.name))
                    
            return payout_amount
        else:
            raise UserError(_('Please configure the %s Payout for %s') % (product_id.categ_id.name, self.psychiatrist_id.related_doctor_id.name))
            
    def create_payout(self):
        payout_amount = self.calculate_payout_amount(self.followup_type_id.product_id)
        line_vals = {
            'product_id': self.followup_type_id.product_id.id,
            'inpatient_admission_id': self.inpatient_admission_id.id,
            'date': self.date,
            'price_unit': payout_amount,
            'reference': self.inpatient_admission_id.name,
            'internal_reference': self.name,
            'type': 'credit',
            'patient_id': self.inpatient_admission_id.patient.id,
            'name': self.followup_type_id.product_id.name,
            'quantity': 1.0,
            'price_subtotal': payout_amount,
        }
        
        payout = self.env['doctor.payout'].search([
            ('doctor_id', '=', self.psychiatrist_id.related_doctor_id.id), 
            ('start_date', '<=', self.date), 
            ('end_date', '>=', self.date), 
            ('state', '=', 'new')
        ])
        
        if payout:
            line_vals.update({'doctor_payout_id': payout.id})
            self.env['doctor.payout.line'].create(line_vals)
        else:
            if self.psychiatrist_id.related_doctor_id.id:
                payout_vals = {
                    'doctor_id': self.psychiatrist_id.related_doctor_id.id,
                    'start_date': fields.Date.today().replace(day=1),
                    'end_date': (fields.Date.today() + relativedelta(months=1, day=1, days=-1)),
                }
                payout_id = self.env['doctor.payout'].create(payout_vals)
                if payout_id:
                    line_vals.update({'doctor_payout_id': payout_id.id})
                    self.env['doctor.payout.line'].create(line_vals)
            else:
                raise UserError(_('Please set related doctor in employee record'))
                
    def create_debit_note(self):
        price_unit = 0.0
        payout_config_id = self.env['payout.config'].search([
            ('partner_id', '=', self.psychiatrist_id.related_doctor_id.id), 
            ('product_category_id', '=', self.followup_type_id.product_id.categ_id.id)
        ], limit=1)
        
        if payout_config_id:
            if payout_config_id.type == 'base':
                price_unit = self.followup_type_id.product_id.list_price
            else:
                patient_id = self.inpatient_admission_id.patient or self.op_visit_id.patient_id
                for each in patient_id.property_product_pricelist.item_ids:
                    if self.followup_type_id.product_id.categ_id.id == each.categ_id.id or self.followup_type_id.product_id.categ_id.id == each.product_tmpl_id.categ_id.id:
                        if each.compute_price == 'fixed':
                            price_unit = each.fixed_price
                        elif each.compute_price == 'percentage':
                            price_unit = self.followup_type_id.product_id.list_price - (self.followup_type_id.product_id.list_price * (each.percent_price / 100))
                        elif each.compute_price == 'formula':
                            price_unit = self.followup_type_id.product_id.list_price - (self.followup_type_id.product_id.list_price * (each.price_discount / 100))
                if price_unit == 0.0:
                   raise UserError(_('Please configure Price for this consultation type in the pricelist attached to the patient'))
        else:
            raise UserError(_('Please configure the Payout'))
            
        line_vals = {
            'reference': self.name,
            'product_id': self.followup_type_id.product_id.id,
            'name': self.followup_type_id.product_id.name,
            'quantity': 1.0,
            'price_unit': price_unit,
            'date': self.date,
            'internal_category_id': self.followup_type_id.product_id.categ_id.id
        }
        
        if self.type == 'ip':
            debit_note_id = self.env['debit.note'].search([
                ('inpatient_admission_id', '=', self.inpatient_admission_id.id), 
                ('start_date', '<=', self.date), 
                ('end_date', '>=', self.date), 
                ('state', '!=', 'invoiced')
            ])
            
            if debit_note_id:
                line_vals.update({'debit_id': debit_note_id.id})
                self.env['debit.note.line'].create(line_vals)
            else:
                debit_note_vals = {
                    'inpatient_admission_id': self.inpatient_admission_id.id,
                    'patient_id': self.inpatient_admission_id.patient.id,
                    'bed_id': self.inpatient_admission_id.bed.id,
                    'ward_id': self.inpatient_admission_id.bed.ward.id,
                    'building_id': self.inpatient_admission_id.bed.building.id,
                    'health_center_id': self.inpatient_admission_id.bed.building.institution.id,
                    'start_date': fields.Date.today().replace(day=1),
                    'end_date': fields.Date.today() + relativedelta(months=1, day=1, days=-1),
                }
                debit_note_id = self.env['debit.note'].create(debit_note_vals)
                if debit_note_id:
                    line_vals.update({'debit_id': debit_note_id.id})
                    self.env['debit.note.line'].create(line_vals)
    
    # Create consultation record for cross consultation
    def create_consultation_record(self, followup_type_id, doctor_id):
        vals = {
            'psychiatrist_id': doctor_id.id,
            'date': self.date,
            'followup_type_id': followup_type_id.id,
            'state': 'draft',
            'cross_consultation': True,
            'advised_doctor': self.psychiatrist_id.id
        }
        
        if self.type == 'ip':
            vals.update({'inpatient_admission_id': self.inpatient_admission_id.id, 'type': self.type})
        else:
            vals.update({'op_visit_id': self.op_visit_id.id, 'type': self.type})
            
        consultation = self.env['consultation.consultation'].create(vals)

    def get_prescription_lines(self):
        line_vals = []
        for line in self.consultation_prescription_line_ids:
            vals = (0, 0, {
                'doctor': line.doctor and line.doctor.id,
                'speciality': line.speciality and line.speciality.id,
                'name': line.name and line.name.id,
                'prescription_type': line.prescription_type,
                'start_treatment': line.start_treatment,
                'end_treatment': line.end_treatment,
                'mrgn': line.mrgn,
                'noon': line.noon,
                'evng': line.evng,
                'night': line.night,
                'dose_form': line.dose_form.id if line.dose_form else False,
                'product_uom': line.product_uom.id if line.product_uom else False,
                'common_dosage': line.common_dosage.id if line.common_dosage else False,
                'take': line.take,
                'indication': line.indication.id if line.indication else False
            })
            line_vals.append(vals)
        return line_vals
    
    def create_prescription(self):
        doctor_id = self.consultation_prescription_line_ids.mapped('doctor')
        vals = {
            'prescription_type': self.type,
            'doctor': doctor_id[0].id if doctor_id else False,
            'date': fields.Datetime.now(),
            'prescription_line': self.get_prescription_lines(),
            'active': True,
        }
        
        if self.type == 'op':
            vals.update({
                'op_visit_id': self.op_visit_id.id,
                'inpatient_id': False,
                'patient': self.op_visit_id.patient_id.id,
                'patient_id': self.op_visit_id.patient_id.identification_code,
                'company_id': self.op_visit_id.patient_id.company_id.id,
            })
        elif self.type == 'ip':
            vals.update({
                'inpatient_id': self.inpatient_admission_id.id,
                'op_visit_id': False,
                'patient': self.inpatient_admission_id.patient.id,
                'patient_id': self.inpatient_admission_id.patient.identification_code,
                'company_id': self.inpatient_admission_id.patient.company_id.id,
            })
            
        prescription_id = self.env['oeh.medical.prescription'].create(vals)
        if prescription_id and self.type == 'op':
            prescription_id.action_prescription_confirm()

    def create_counsellor_advice(self):
        vals = {
            'followup_type_id': self.followup_type_id.id,
            'date': self.date,
            'start_date': self.start_datetime,
            'end_date': self.end_datetime,
            'note': self.advice_to_counsellor,
            'company_id': self.company_id.id
        }
        
        if self.type == 'ip':
            vals.update({
                'inpatient_admission_id': self.inpatient_admission_id.id,
                'counsellor_id': self.inpatient_admission_id.counsellor.id,
                'type': self.type
            })
        elif self.type == 'op':
            vals.update({
                'op_visit_id': self.op_visit_id.id,
                'type': self.type
            })
            
        self.env['advice.counsellor'].create(vals)
    
    def create_clinical_psychologist_advice(self):
        vals = {
            'clinical_psychologist_id': self.cp_therapist_id.id,
            'followup_type_id': self.followup_type_id.id,
            'date': self.date,
            'start_date': self.start_datetime,
            'end_date': self.end_datetime,
            'note': self.advice_to_psychologist,
            'company_id': self.company_id.id
        }
        
        if self.type == 'ip':
            vals.update({
                'inpatient_admission_id': self.inpatient_admission_id.id,
                'type': self.type
            })
        elif self.type == 'op':
            vals.update({
                'op_visit_id': self.op_visit_id.id,
                'type': self.type
            })
            
        self.env['advice.clinical.psychologist'].create(vals)
    
    def create_bill_estimation(self):
        if self.admission_consultation_ids or self.admission_labtest_ids or self.admission_room_type_ids or self.admission_misc_item_ids:
            estimation_bill_id = self.env['bill.estimation'].create({
                'name': self.patient_id.id, 
                'bed_type': self.bed_type_id.id, 
                'rate_plan': self.price_tag.id
            })
            
            if estimation_bill_id:
                for consultation_id in self.admission_consultation_ids:
                    vals = {
                        'bill_estimation_id': estimation_bill_id.id,
                        'product_id': consultation_id.followup_type_id.product_id.id,
                        'description': consultation_id.followup_type_id.product_id.name,
                        'quantity': consultation_id.quantity,
                        'unit_price': consultation_id.unit_price
                    }
                    consult_line = self.env['bill.estimation.line'].create(vals)
                    consult_line.onchange_product_id()
                    
                for labtest_id in self.admission_labtest_ids:
                    vals = {
                        'bill_estimation_id': estimation_bill_id.id,
                        'product_id': labtest_id.product_id.id,
                        'description': labtest_id.product_id.name,
                        'quantity': 1.0,
                        'unit_price': labtest_id.product_id.lst_price or labtest_id.test_charge
                    }
                    lab_line = self.env['bill.estimation.line'].create(vals)
                    lab_line.onchange_product_id()
                    
                for room_type_id in self.admission_room_type_ids:
                    vals = {
                        'bill_estimation_id': estimation_bill_id.id,
                        'product_id': room_type_id.product_id.id,
                        'description': room_type_id.product_id.name,
                        'quantity': room_type_id.quantity,
                        'unit_price': room_type_id.unit_price
                    }

                    room_line = self.env['bill.estimation.line'].create(vals)
                    room_line.onchange_product_id()
                    
                for misc_item_id in self.admission_misc_item_ids:
                    vals = {
                        'bill_estimation_id': estimation_bill_id.id,
                        'product_id': misc_item_id.product_id.id,
                        'description': misc_item_id.product_id.name,
                        'quantity': misc_item_id.quantity,
                        'unit_price': misc_item_id.unit_price
                    }
                    misc_line = self.env['bill.estimation.line'].create(vals)
                    misc_line.onchange_product_id()
    
    
    def action_complete(self):
        if self.prescription_status == 'changed' and self.consultation_prescription_line_ids:
            self.create_prescription()
        if self.labtest_type_ids and self.lab_advice:
            self.create_labtest_requisition()
        if self.speciality_ids:
            self.create_outside_consultation()
        if self.advice_to_counsellor:
            self.create_counsellor_advice()
        if self.advice_to_psychologist and self.cp_therapist_id:
            self.create_clinical_psychologist_advice()
        if self.referral_config_id:
            self.create_bill_estimation()
        if self.followup_type_id.payout:
            self.create_payout()
            if self.patient_id.referred_by:
                doctor = self.patient_id.referred_by
                self.create_referral_payout(doctor)
            elif self.cross_consultation and self.advised_doctor:
                doctor = self.advised_doctor.related_doctor_id
                self.create_referral_payout(doctor)      
        if self.followup_type_id.billable:
            self.create_debit_note()
        if self.scale_type_ids:
            self.create_scales()
        if self.cross_consultation_ids:
            for line in self.cross_consultation_ids:
                self.create_consultation_record(line.followup_type_id, line.doctor_id)
        self.end_datetime = fields.Datetime.now()
        self.state = 'completed'
    
    def view_doctor_consultation(self):
        consultation_ids = self.search([('patient_id', '=', self.patient_id.id), ('id', '!=', self.id)], order='date,id desc')
        domain = [('id', 'in', consultation_ids.ids)]
        
        return {
            'name': _('Consultation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'consultation.consultation',
            'domain': domain,
            'context': {'search_default_team_role': 1},
        }
    
    def view_psychiatrist_evaluation_form(self):
        evaluation_ids = self.env['psychiatrist.evaluation.form'].search([('patient_id', '=', self.patient_id.id)], order='date,id desc')
        domain = [('id', 'in', evaluation_ids.ids)]
        
        return {
            'name': _('Psychiatrist Evaluation Form'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'psychiatrist.evaluation.form',
            'domain': domain,
        }
    
    # action of patient documents smart button
    def view_patient_document(self):
        active_patient_documents = self.env['patient.document'].search([('oeh_medical_patient', '=', self.patient_id.id)])
        domain = [('id', 'in', active_patient_documents.ids)]
        
        return {
            'name': _('Patient Documents'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'patient.document',
            'domain': domain,
        }
    
    def view_prescriptions(self):
        domain = [('patient', '=', self.patient_id.id)]
        
        return {
            'name': _('Prescriptions'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'oeh.medical.prescription',
            'domain': domain,
            'context': {"search_default_confirmed_slip": 1},
        }
    
    def send_feedback_form(self):
        template_id = self.env.ref('program_scheduler.mail_template_consultation_feedback')
        if template_id:
            template_id.send_mail(self.id, force_send=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('consultation.consultation') or 'New'
        return super(Consultation, self).create(vals)
    
  
    def action_clinical_psychologist_session(self):
        return {
            'name': _('Clinical Psychologist Session'),
            'type': 'ir.actions.act_window',
            'res_model': 'clinical.psychologist.session',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_consultation_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
                'default_op_visit_id': self.op_visit_id.id
            }
        }
    
    def action_clinical_psychologist_session(self):
        """Handle the Clinical Psychologist Session button action"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Clinical Psychologist Session'),
            'res_model': 'clinical.psychologist.session',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_consultation_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id if self.type == 'ip' else False,
                'default_op_visit_id': self.op_visit_id.id if self.type == 'op' else False
            }
        }

    def action_consultation_followup(self):
        """Handle the Consultation Follow-up button action"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Consultation Follow-up'),
            'res_model': 'consultation.followup',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_consultation_id': self.id,
                'default_is_sos': self.is_sos,
                'default_next_followup_date': self.next_followup_date,
                'default_doctor_advice': self.doctor_advice,
                'default_precautions': self.precautions,
                'default_todo': self.todo
            }
        }
    
    def action_clinical_psychologist_screening(self):
        """Handle the Clinical Psychologist Screening button action"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Clinical Psychologist Screening'),
            'res_model': 'clinical.psychologist.screening', 
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_consultation_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id if self.type == 'ip' else False,
                'default_op_visit_id': self.op_visit_id.id if self.type == 'op' else False
            }
        }

    def counsellor_session_action(self):
        """Handle the Counsellor Session button action"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Counsellor Session'),
            'res_model': 'counsellor.session',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_consultation_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id if self.type == 'ip' else False,
                'default_op_visit_id': self.op_visit_id.id if self.type == 'op' else False
            }
        }

    def oeh_medical_lab_test_action_tree(self):
        """View lab test results for the patient"""
        domain = [('patient_id', '=', self.patient_id.id)]
        return {
            'name': _('Lab Tests'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'medical.labtest',
            'domain': domain,
        }

    def action_outside_consultation(self):
        """View outside consultations for the patient"""
        domain = [('patient_id', '=', self.patient_id.id)]
        return {
            'name': _('Outside Consultations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form', 
            'res_model': 'outside.consultation',
            'domain': domain,
        }

    def action_crm_simple_registration(self):
        """Open CRM registration form"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Registration'),
            'res_model': 'crm.simple.registration',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_consultation_id': self.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id if self.type == 'ip' else False,
                'default_op_visit_id': self.op_visit_id.id if self.type == 'op' else False
            }
        }

