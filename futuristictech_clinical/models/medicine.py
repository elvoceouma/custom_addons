# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Medicine(models.Model):
    _name = 'hospital.medicine'
    _description = 'Medicine'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    medicine_type_id = fields.Many2one('hospital.medication.type', string='Medicine Type')
    medicine_category_id = fields.Many2one('hospital.medication.category', string='Medicine Category')
    dosage_ids = fields.One2many('hospital.medicine.dosage', 'medicine_id', string='Dosages')
    form_id = fields.Many2one('hospital.drug.form', string='Drug Form')
    active = fields.Boolean(default=True)
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy', required=True)
    quantity_available = fields.Float(string='Quantity Available', compute='_compute_quantity_available', store=True)
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy')

class MedicineDosage(models.Model):
    _name = 'hospital.medicine.dosage'
    _description = 'Medicine Dosage'
    
    name = fields.Char(string='Name', required=True)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    strength = fields.Char(string='Strength')
    unit_id = fields.Many2one('hospital.dose.unit', string='Unit')


class MedicationCategory(models.Model):
    _name = 'hospital.medication.category'
    _description = 'Medication Category'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


class MedicationType(models.Model):
    _name = 'hospital.medication.type'
    _description = 'Medication Type'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)


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