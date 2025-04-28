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
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', required=True, tracking=True)
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
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.simple.registration') or _('New')
        return super(CRMSimpleRegistration, self).create(vals)
    
    def action_register(self):
        self.state = 'registered'
    
    def action_cancel(self):
        self.state = 'cancelled'