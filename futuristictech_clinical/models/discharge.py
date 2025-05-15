# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class DischargeRecord(models.Model):
    _name = 'hospital.discharge'
    _description = 'Patient Discharge'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Inpatient Admission', required=True, tracking=True)
    discharge_date = fields.Datetime(string='Discharge Date', default=fields.Datetime.now, tracking=True)
    
    # Fields from the form view
    requested_by = fields.Many2one('res.users', string='Requested By', tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', tracking=True)
    approved_date = fields.Datetime(string='Approved Date', tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription', tracking=True)
    
    # Clearance related fields
    counsellor = fields.Many2one('res.users', string='Counsellor', tracking=True)
    nurse = fields.Many2one('res.users', string='Nurse', tracking=True)
    store_incharge = fields.Many2one('res.users', string='Store Incharge', tracking=True)
    
    # Additional fields
    description = fields.Text(string='Description', tracking=True)
    
    # State field for status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approve', 'Approved'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge') or _('New')
        return super(DischargeRecord, self).create(vals_list)

    def action_confirm(self):
        for record in self:
            record.state = 'waiting_for_approval'
    
    def action_approve(self):
        for record in self:
            record.state = 'approve'
            record.approved_by = self.env.user.id
            record.approved_date = fields.Datetime.now()
    
    def action_close(self):
        for record in self:
            record.state = 'close'
            if record.inpatient_admission_id:
                record.inpatient_admission_id.state = 'Discharged'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_medicine_packing(self):
            self.ensure_one()
            return {
                'name': _('Medicine Packing'),
                'type': 'ir.actions.act_window',
                'res_model': 'hospital.medicine.packing',
                'view_mode': 'tree,form',
                'domain': [('discharge_id', '=', self.id)],
                'context': {
                    'default_discharge_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_inpatient_admission_id': self.inpatient_admission_id.id,
                },
                'target': 'current',
            }
        
    def action_requisition_clearance(self):
        self.ensure_one()
        return {
            'name': _('Requisition Clearance'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.requisition.clearance',
            'view_mode': 'tree,form',
            'domain': [('discharge_id', '=', self.id)],
            'context': {
                'default_discharge_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
            },
            'target': 'current',
        }
    
    def action_store_clearance(self):
        self.ensure_one()
        return {
            'name': _('Store Clearance'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.store.clearance',
            'view_mode': 'tree,form',
            'domain': [('discharge_id', '=', self.id)],
            'context': {
                'default_discharge_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
            },
            'target': 'current',
        }
    
    def action_discharge_summary(self):
        self.ensure_one()
        return {
            'name': _('Discharge Summary'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.discharge.summary',
            'view_mode': 'tree,form',
            'domain': [('inpatient_admission_id', '=', self.inpatient_admission_id.id)],
            'context': {
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
                'default_patient_id': self.patient_id.id,
                'default_campus': self.campus,
                'default_discharge_id': self.id,
            },
            'target': 'current',
        }






class DischargeSummary(models.Model):
    _name = 'hospital.discharge.summary'
    _description = 'Discharge Summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Admission', required=True, tracking=True)
    discharge_id = fields.Many2one('hospital.discharge', string='Discharge Record', tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # Approvals related fields
    clinical_psychologist = fields.Many2one('res.users', string='Clinical Psychologist', tracking=True)
    psychiatrist = fields.Many2one('res.users', string='Psychiatrist', tracking=True)
    registrar = fields.Many2one('res.users', string='Registrar', tracking=True)
    clinical_psychologist_bool = fields.Boolean(string='Clinical Psychologist Approved', tracking=True)
    psychiatrist_bool = fields.Boolean(string='Psychiatrist Approved', tracking=True)
    registrar_bool = fields.Boolean(string='Registrar Approved', tracking=True)
    
    description = fields.Text(string='Description', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('approve', 'Approved')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge.summary') or _('New')
        return super(DischargeSummary, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'inprogress'
    
    def action_approve_clinical_psychologist(self):
        for record in self:
            record.clinical_psychologist_bool = True
            record.clinical_psychologist = self.env.user.id
            self._check_all_approvals()
    
    def action_approve_psychiatrist(self):
        for record in self:
            record.psychiatrist_bool = True
            record.psychiatrist = self.env.user.id
            self._check_all_approvals()
    
    def action_approve_registrar(self):
        for record in self:
            record.registrar_bool = True
            record.registrar = self.env.user.id
            self._check_all_approvals()
    
    def _check_all_approvals(self):
        for record in self:
            if record.clinical_psychologist_bool and record.psychiatrist_bool and record.registrar_bool:
                record.state = 'approve'