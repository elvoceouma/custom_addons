# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Admission(models.Model):
    _name = 'hospital.admission'
    _description = 'Inpatient Admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    patient_title = fields.Selection([
        ('mr', 'MR'),
        ('mrs', 'MRS'),
        ('miss', 'MISS'),
        ('ms', 'MS')
    ], string='Patient Title', tracking=True)

    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True, tracking=True)
    room_id = fields.Many2one('hospital.room', string='Room', required=True, tracking=True)
    bed_id = fields.Many2one('hospital.bed', string='Bed', required=True, tracking=True)
    condition_before_admission = fields.Text(string='Condition Before Admission')
    condition_after_admission = fields.Text(string='Condition After Admission')
    admitting_person = fields.Char(string='Admitting Person')
    admission_date = fields.Datetime(string='Admission Date', default=fields.Datetime.now, tracking=True)
    next_bill_date = fields.Datetime(string='Next Bill Date', tracking=True)
    discharge_date = fields.Datetime(string='Discharge Date', tracking=True)
    discharge_plan = fields.Text(string='Discharge Plan')
    advised_discharge_date = fields.Datetime(string='Advised Discharge Date', tracking=True)
    advice_for_discharge = fields.Text(string='Advice for Discharge')
    nursing_plan = fields.Text(string='Nursing Plan')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admission_confirmed', 'Admission Confirmed'),
        ('invoiced', 'Invoiced'),
        ('completed', 'Completed'),
        ('discharge_initiated', 'Discharge Initiated'),
        ('discharged', 'Discharged')
    ], string='State', default='draft', tracking=True)
    
    next_barcode_number = fields.Integer(string='Next Bar-code Number')
    admission_type_id = fields.Many2one('hospital.admission.type', string='Admission Type', tracking=True)
    psychiatrist_id = fields.Many2one('res.partner', string='Psychiatrist', domain=[('is_psychiatrist', '=', True)])
    clinical_psychologist_id = fields.Many2one('res.partner', string='Clinical Psychologist', domain=[('is_clinical_psychologist', '=', True)])
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    counsellor_id = fields.Many2one('res.partner', string='Counsellor', domain=[('is_counsellor', '=', True)])
    acting_counsellor_id = fields.Many2one('res.partner', string='Acting Counsellor', domain=[('is_counsellor', '=', True)])
    caretaker_id = fields.Many2one('res.partner', string='Caretaker', domain=[('is_caretaker', '=', True)])
    family_therapist_id = fields.Many2one('res.partner', string='Family Therapist', domain=[('is_family_therapist', '=', True)])
    reason_for_admission = fields.Text(string='Reason for Admission')
    attending_physician_id = fields.Many2one('res.partner', string='Attending Physician', domain=[('is_physician', '=', True)])
    operating_physician_id = fields.Many2one('res.partner', string='Operating Physician', domain=[('is_physician', '=', True)])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.admission') or _('New')
        return super(Admission, self).create(vals_list)
    
    def action_confirm_admission(self):
        for record in self:
            record.state = 'admission_confirmed'
            if record.bed_id:
                record.bed_id.write({
                    'status': 'occupied',
                    'current_patient_id': record.patient_id.id
                })
    
    def action_initiate_discharge(self):
        for record in self:
            record.state = 'discharge_initiated'
    
    def action_complete_discharge(self):
        for record in self:
            record.state = 'discharged'
            if record.bed_id:
                record.bed_id.write({
                    'status': 'free',
                    'current_patient_id': False
                })

    def action_draft(self):
        for record in self:
            record.state = 'draft'
            if record.bed_id:
                record.bed_id.write({
                    'status': 'free',
                    'current_patient_id': False
                })
    
    def action_invoice(self):
        for record in self:
            record.state = 'invoiced'
            # Logic to create invoice can be added here
            # Example: self.env['account.move'].create_invoice(record)

    def action_invoiced(self):
        for record in self:
            record.state = 'invoiced'
            # Logic to create invoice can be added here
            # Example: self.env['account.move'].create_invoice(record)

    def action_discharged(self):
        for record in self:
            record.state = 'discharged'
            # Logic to create discharge summary can be added here
            # Example: self.env['hospital.discharge.summary'].create_discharge_summary(record)

    def action_hospitalized(self):
        for record in self:
            record.state = 'hospitalized'
            # Logic to create hospitalization record can be added here
            # Example: self.env['hospital.hospitalization'].create_hospitalization(record)

    
class HospitalAdmissionType(models.Model):
    _name = 'hospital.admission.type'
    _description = 'Admission Type'
    
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    admission_ids = fields.One2many('hospital.admission', 'admission_type_id', string='Admissions')
    active = fields.Boolean(string='Active', default=True)
    code = fields.Char(string='Code', required=True)

class OPVisit(models.Model):
    _name = 'hospital.op.visit'
    _description = 'Outpatient Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    date = fields.Datetime(string='Visit Date', default=fields.Datetime.now)
    physician_id = fields.Many2one('res.partner', string='Physician')
    reason = fields.Text(string='Reason for Visit')
    diagnosis = fields.Text(string='Diagnosis')
    prescription_ids = fields.One2many('hospital.prescription', 'op_visit_id', string='Prescriptions')
    type = fields.Selection([
        ('follow_up', 'Follow Up'),
        ('new_case', 'New Case')
    ], string='Visit Type', default='new_case')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.op.visit') or _('New')
        return super(OPVisit, self).create(vals_list)