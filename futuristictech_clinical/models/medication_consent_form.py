# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicationConsentForm(models.Model):
    _name = 'medication.consent.form'
    _description = 'Informed Consent for Medication Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    
    date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    
    # Patient information
    ip_number = fields.Char(string='IP Number', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    age = fields.Integer(related='patient_id.age', string='Age', store=True)
    mrn_no = fields.Char(related='patient_id.mrn_no', string='MRN No', store=True)
    campus = fields.Many2one('hospital.hospital', string='Campus')
    
    # Representative information
    nominated_representative = fields.Char(string='Nominated Representative')
    
    # Medication information
    medication_type = fields.Many2one('hospital.medicine.type', string='Medication Type')
    medical_officer = fields.Many2one('res.users', string='Medical Officer', domain=[('is_medical_officer', '=', True)])
    
    # Diagnosis
    diagnosis = fields.Text(string='Diagnosis: (Use ICD 10 or 11)')
    
    # Medication line items
    medication_line_ids = fields.One2many('medication.consent.form.line', 'consent_form_id', string='Medications')
    
    # Administration method
    orally = fields.Boolean(string='Orally')
    injection = fields.Boolean(string='Injection')
    other_specify = fields.Boolean(string='If Others Specify')
    other_specify_text = fields.Char(string='Others Specify')
    
    # Other consequences
    other_consequences = fields.Text(string='Other Consequences')
    
    # Status and approval
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    company = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    confirmed_by = fields.Many2one('res.users', string='Confirmed By')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medication.consent.form') or _('New')
        return super(MedicationConsentForm, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            record.confirmed_by = self.env.user.id
    
    def action_complete(self):
        for record in self:
            record.state = 'completed'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'


class MedicationConsentFormLine(models.Model):
    _name = 'medication.consent.form.line'
    _description = 'Medication Consent Form Line'
    
    consent_form_id = fields.Many2one('medication.consent.form', string='Consent Form', ondelete='cascade')
    medication_category_id = fields.Many2one('hospital.medicine.category', string='Medication Category')
    medication_id = fields.Many2one('hospital.medicine', string='Medication')
    dosage_range = fields.Char(string='Dosage Range')
    planned_dosage_range = fields.Char(string='Planned Dosage Range')
    

class HospitalMedicineType(models.Model):
    _name = 'hospital.medicine.type'
    _description = 'Medicine Type'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class HospitalMedicineCategory(models.Model):
    _name = 'hospital.medicine.category'
    _description = 'Medicine Category'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class HospitalMedicineForm(models.Model):
    _name = 'hospital.medicine.form'
    _description = 'Medicine Form'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)




class HospitalMedicineUnit(models.Model):
    _name = 'hospital.medicine.unit'
    _description = 'Medicine Unit'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)

class MedicineCategory(models.Model):
    _name = 'medicine.category'
    _description = 'Medicine Category'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Medicine category name must be unique!')
    ]