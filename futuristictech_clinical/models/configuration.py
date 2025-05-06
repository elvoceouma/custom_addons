# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PsychologistPartnerExtension(models.Model):
    _inherit = 'res.partner'
    
    is_psychiatrist = fields.Boolean(string='Is Psychiatrist')
    is_clinical_psychologist = fields.Boolean(string='Is Clinical Psychologist')
    is_physician = fields.Boolean(string='Is Physician')
    is_counsellor = fields.Boolean(string='Is Counsellor')
    is_caretaker = fields.Boolean(string='Is Caretaker')
    is_family_therapist = fields.Boolean(string='Is Family Therapist')
    speciality_id = fields.Many2one('hospital.physician.speciality', string='Speciality')
    degree_ids = fields.Many2many('hospital.physician.degree', string='Degrees')


class PhysicianSpeciality(models.Model):
    _name = 'hospital.physician.speciality'
    _description = 'Physician Speciality'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class PhysicianDegree(models.Model):
    _name = 'hospital.physician.degree'
    _description = 'Physician Degree'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)