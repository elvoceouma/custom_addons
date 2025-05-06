# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class InitialAssessment(models.Model):
    _name = 'hospital.initial.assessment'
    _description = 'Initial Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    assessment_date = fields.Date(string='Assessment Date', default=fields.Date.context_today)
    physician_id = fields.Many2one('res.partner', string='Physician')
    chief_complaint = fields.Text(string='Chief Complaint')
    history_present_illness = fields.Text(string='History of Present Illness')
    past_medical_history = fields.Text(string='Past Medical History')
    family_history = fields.Text(string='Family History')
    social_history = fields.Text(string='Social History')
    allergies = fields.Text(string='Allergies')
    current_medications = fields.Text(string='Current Medications')
    physical_examination = fields.Text(string='Physical Examination')
    assessment = fields.Text(string='Assessment')
    plan = fields.Text(string='Plan')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.initial.assessment') or _('New')
        return super(InitialAssessment, self).create(vals_list)


class VitalChart(models.Model):
    _name = 'hospital.vital.chart'
    _description = 'Vital Chart'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'datetime desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    datetime = fields.Datetime(string='Date and Time', default=fields.Datetime.now)
    temperature = fields.Float(string='Temperature (°C)')
    pulse = fields.Integer(string='Pulse (bpm)')
    respiratory_rate = fields.Integer(string='Respiratory Rate (bpm)')
    blood_pressure_systolic = fields.Integer(string='Blood Pressure (Systolic)')
    blood_pressure_diastolic = fields.Integer(string='Blood Pressure (Diastolic)')
    oxygen_saturation = fields.Float(string='Oxygen Saturation (%)')
    pain_score = fields.Integer(string='Pain Score (0-10)')
    recorded_by = fields.Many2one('res.users', string='Recorded By', default=lambda self: self.env.user)
    notes = fields.Text(string='Notes')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.vital.chart') or _('New')
        return super(VitalChart, self).create(vals_list)


class MentalStatusExamination(models.Model):
    _name = 'hospital.mental.status.examination'
    _description = 'Mental Status Examination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    appearance = fields.Text(string='Appearance')
    behavior = fields.Text(string='Behavior')
    attitude = fields.Text(string='Attitude')
    mood = fields.Text(string='Mood')
    affect = fields.Text(string='Affect')
    speech = fields.Text(string='Speech')
    thought_process = fields.Text(string='Thought Process')
    thought_content = fields.Text(string='Thought Content')
    perception = fields.Text(string='Perception')
    cognition = fields.Text(string='Cognition')
    insight = fields.Text(string='Insight')
    judgment = fields.Text(string='Judgment')
    examiner_id = fields.Many2one('res.users', string='Examiner', default=lambda self: self.env.user)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.mental.status.examination') or _('New')
        return super(MentalStatusExamination, self).create(vals_list)


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