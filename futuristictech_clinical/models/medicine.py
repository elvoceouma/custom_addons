# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Medicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'Hospital Medicine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    description = fields.Text(string='Description')
    
    medicine_type_id = fields.Many2one('hospital.medication.type', string='Medicine Type')
    medicine_category_id = fields.Many2one('hospital.medication.category', string='Medicine Category')
    
    dosage_ids = fields.One2many('hospital.medicine.dosage', 'medicine_id', string='Dosages')
    quantity_available = fields.Float(string='Quantity Available', readonly=True)
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    prescription_ids = fields.One2many('hospital.prescription.line', 'medicine_id', string='Prescriptions')
    form_id = fields.Many2one('hospital.drug.form', string='Form')
    
    @api.onchange('medicine_type_id')
    def _onchange_medicine_type(self):
        if self.medicine_type_id and not self.medicine_category_id:
            self.medicine_category_id = self.medicine_type_id.default_category_id



class MedicineDosage(models.Model):
    _name = 'hospital.medicine.dosage'
    _description = 'Medicine Dosage'
    
    name = fields.Char(string='Name', required=True)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    dose = fields.Float(string='Dose')
    dose_unit_id = fields.Many2one('hospital.dose.unit', string='Dose Unit')
    frequency = fields.Selection([
        ('once', 'Once'),
        ('twice', 'Twice'),
        ('thrice', 'Thrice'),
        ('4x', 'Four times'),
        ('6h', 'Every 6 hours'),
        ('8h', 'Every 8 hours'),
        ('12h', 'Every 12 hours'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Frequency')
    strength = fields.Selection([
        ('weak', 'Weak'),
        ('moderate', 'Moderate'),
        ('strong', 'Strong'),
    ], string='Strength')
    unit = fields.Selection([
        ('mg', 'mg'),
        ('g', 'g'),
        ('ml', 'ml'),
        ('l', 'l'),
        ('units', 'Units'),
    ], string='Unit')
    unit_id = fields.Many2one('hospital.dose.unit', string='Unit')
    route_id = fields.Many2one('hospital.drug.route', string='Route')
    form_id = fields.Many2one('hospital.drug.form', string='Form')
    active = fields.Boolean(default=True)


class MedicationCategory(models.Model):
    _name = 'hospital.medication.category'
    _description = 'Medication Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    parent_id = fields.Many2one('hospital.medication.category', string='Parent Category')
    child_ids = fields.One2many('hospital.medication.category', 'parent_id', string='Child Categories')



class MedicationType(models.Model):
    _name = 'hospital.medication.type'
    _description = 'Medication Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    default_category_id = fields.Many2one('hospital.medication.category', string='Default Category')


class DrugFrequency(models.Model):
    _name = 'hospital.drug.frequency'
    _description = 'Drug Frequency'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class DrugRoute(models.Model):
    _name = 'hospital.drug.route'
    _description = 'Drug Route'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class DrugForm(models.Model):
    _name = 'hospital.drug.form'
    _description = 'Drug Form'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class DoseUnit(models.Model):
    _name = 'hospital.dose.unit'
    _description = 'Dose Unit'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class HospitalMedicineConsumption(models.Model):
    _name = 'hospital.medicine.consumption'
    _description = 'Hospital Medicine Consumption'
    
    name = fields.Char(string='Name', required=True)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy', required=True)




    