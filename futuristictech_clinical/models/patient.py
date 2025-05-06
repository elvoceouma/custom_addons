# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Patient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    image = fields.Binary(string='Image')
    reference = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    mrn = fields.Char(string='MRN', readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    dob = fields.Date(string='Date of Birth')
    blood_group = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string='Blood Group', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    address = fields.Text(string='Address')
    
    admission_ids = fields.One2many('hospital.admission', 'patient_id', string='Admissions')
    document_ids = fields.One2many('hospital.patient.document', 'patient_id', string='Documents')
    vaccine_ids = fields.One2many('hospital.patient.vaccine', 'patient_id', string='Vaccines')
    op_visit_ids = fields.One2many('hospital.op.visit', 'patient_id', string='OP Visits')
    
    illness_tag_ids = fields.Many2many('hospital.illness.tag', string='Illness Tags')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
            if not vals.get('mrn'):
                vals['mrn'] = self.env['ir.sequence'].next_by_code('hospital.patient.mrn') or 'MRN00000'
        return super(Patient, self).create(vals_list)


class PatientDocument(models.Model):
    _name = 'hospital.patient.document'
    _description = 'Patient Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    document_type_id = fields.Many2one('hospital.document.type', string='Document Type')
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Name')
    note = fields.Text(string='Notes')
    date = fields.Date(string='Date', default=fields.Date.context_today)


    def save(self):
        # Save the document and return to the list view
        self.ensure_one()
        if not self.file:
            raise ValidationError(_('Please upload a file.'))
        if not self.file_name:
            raise ValidationError(_('Please provide a file name.'))
        self.write({'file_name': self.file_name})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }




class IllnessTag(models.Model):
    _name = 'hospital.illness.tag'
    _description = 'Illness Tag'
    
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')


class DocumentType(models.Model):
    _name = 'hospital.document.type'
    _description = 'Document Type'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)

class HospitalPatientEthnicGroup(models.Model):
    _name = 'hospital.patient.ethnic.group'
    _description = 'Hospital Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'          

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')


class HospitalPatientGeneticRisk(models.Model):
    _name = 'hospital.patient.genetic.risk'
    _description = 'Hospital Patient Genetic Risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'          

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')


class HospitalPatientRecreationalDrug(models.Model):
    _name = 'hospital.patient.recreational.drug'
    _description = 'Hospital Patient Recreational Drug'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'          

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')


class HospitalAwsFileType(models.Model):
    _name = 'hospital.aws.file.type'
    _description = 'Hospital AWS File Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'          

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    color = fields.Integer(string='Color Index')