# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class DischargeRecord(models.Model):
    _name = 'hospital.discharge'
    _description = 'Patient Discharge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission', required=True)
    discharge_date = fields.Datetime(string='Discharge Date', default=fields.Datetime.now)
    discharge_type = fields.Selection([
        ('regular', 'Regular'),
        ('dama', 'DAMA (Discharge Against Medical Advice)'),
        ('lama', 'LAMA (Leave Against Medical Advice)')
    ], string='Discharge Type', default='regular', required=True)
    primary_diagnosis = fields.Text(string='Primary Diagnosis')
    secondary_diagnoses = fields.Text(string='Secondary Diagnoses')
    procedures_performed = fields.Text(string='Procedures Performed')
    discharge_medications = fields.Text(string='Discharge Medications')
    follow_up_instructions = fields.Text(string='Follow-up Instructions')
    discharge_condition = fields.Selection([
        ('improved', 'Improved'),
        ('stable', 'Stable'),
        ('unchanged', 'Unchanged'),
        ('deteriorated', 'Deteriorated')
    ], string='Discharge Condition', default='improved')
    discharged_by = fields.Many2one('res.users', string='Discharged By', default=lambda self: self.env.user)
    counsellor_clearance = fields.Boolean(string='Counsellor Clearance')
    store_clearance = fields.Boolean(string='Store Clearance')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge') or _('New')
        return super(DischargeRecord, self).create(vals_list)
    
    def action_complete_discharge(self):
        for record in self:
            if record.admission_id:
                record.admission_id.action_complete_discharge()


class DischargeSummary(models.Model):
    _name = 'hospital.discharge.summary'
    _description = 'Discharge Summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission', required=True)
    discharge_id = fields.Many2one('hospital.discharge', string='Discharge Record')
    discharge_date = fields.Datetime(related='discharge_id.discharge_date', string='Discharge Date')
    summary = fields.Text(string='Summary', required=True)
    admission_reason = fields.Text(string='Reason for Admission')
    hospital_course = fields.Text(string='Hospital Course')
    discharge_medications = fields.Text(string='Discharge Medications')
    discharge_instructions = fields.Text(string='Discharge Instructions')
    follow_up_plan = fields.Text(string='Follow-up Plan')
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge.summary') or _('New')
        return super(DischargeSummary, self).create(vals_list)