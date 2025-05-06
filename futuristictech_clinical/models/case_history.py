# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CaseHistory(models.Model):
    _name = 'hospital.case.history'
    _description = 'Case History'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'
    
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    age = fields.Integer(string='Age', related='patient_id.age', store=True)
    date_of_birth = fields.Date(string='Date of Birth', related='patient_id.dob')
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
    
    religion = fields.Char(string='Religion')
    socio_economic_status = fields.Selection([
        ('low', 'Low'),
        ('middle', 'Middle'),
        ('high', 'High')
    ], string='Socio-Economic Status')
    occupation = fields.Many2one('hospital.patient.occupation', string='Occupation')
    
    # Informants
    informant_name = fields.Char(string='Name')
    relationship = fields.Many2one('hospital.patient.relationship', string='Relationship')
    duration_of_stay = fields.Char(string='Duration of Stay with Patient')
    
    information = fields.Text(string='INFORMATION : Reliable and Adequate')
    
    chief_complaint_ids = fields.One2many('hospital.chief.complaint', 'case_history_id', string='Chief Complaints')
    
    onset_of_illness = fields.Selection([
        ('abrupt', 'Abrupt (Sudden)'),
        ('acute', 'Acute (Few hours to few days)'),
        ('sub_acute', 'Sub-acute (Few days to few weeks)'),
        ('insidious', 'Insidious (Few weeks to few months)')
    ], string='Onset of Illness')
    
    course = fields.Text(string='Course')
    
    duration_of_illness = fields.Selection([
        ('months', 'Months'),
        ('years', 'Years')
    ], string='Duration of Illness')
    duration_value = fields.Integer(string='Duration Value')
    
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
    
    sequence = fields.Integer(string='Sequence', default=10)
    case_history_id = fields.Many2one('hospital.case.history', string='Case History', ondelete='cascade')
    name = fields.Text(string='Complaint', required=True)
    duration = fields.Char(string='Duration')
    year = fields.Char(string='Year')


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