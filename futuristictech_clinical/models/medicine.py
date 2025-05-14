# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

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
    type_id = fields.Many2one('medicine.type', string='Type')
    form_id = fields.Many2one('hospital.drug.form', string='Form')
    generic_name = fields.Char(string='Generic Name')
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string='Description')
    manufacturer = fields.Char(string='Manufacturer')
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
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    register_type = fields.Selection([
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('injection', 'Injection'),
        ('application', 'Application'),
    ], string='Register Type', required=True)
    name = fields.Char(string='Name', required=True)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    quantity = fields.Float(string='Quantity', required=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy', required=True)
    time = fields.Char(string='Time', required=True)
    campus_id = fields.Many2one('hospital.campus', string='Campus', required=True)

class MedicineRegister(models.Model):
    _name = 'medicine.register'
    _description = 'Medicine Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    ip_number = fields.Char(string='IP Number', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    campus_id = fields.Many2one('hospital.campus', string='Campus', tracking=True)
    
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription', tracking=True)
    date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    type_id = fields.Many2one('medicine.type', string='Type', tracking=True)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', tracking=True)
    form_id = fields.Many2one('hospital.medicine.form', string='Form', tracking=True)
    quantity = fields.Float(string='Quantity', default=0.0, tracking=True)
    time = fields.Char(string='Time', tracking=True)
    hours = fields.Float(string='Hours', default=0.0, tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medicine.register') or _('New')
        return super(MedicineRegister, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_done(self):
        for record in self:
            record.state = 'done'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
            
    def action_draft(self):
        for record in self:
            record.state = 'draft'

class MedicineType(models.Model):
    _name = 'medicine.type'
    _description = 'Medicine Type'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Medicine type name must be unique!')
    ]


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
    
    # Products related to this category
    product_ids = fields.One2many('hospital.medication.product', 'category_id', string='Medication Products')


class MedicationProduct(models.Model):
    _name = 'hospital.medication.product'
    _description = 'Medication Product'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    category_id = fields.Many2one('hospital.medication.category', string='Medication Category', required=True)
    product_id = fields.Many2one('product.product', string='Related Product')
    default_dosage = fields.Char(string='Default Dosage')
    dosage_range = fields.Char(string='Dosage Range')
    active = fields.Boolean(default=True)
    medication_type_id = fields.Many2one('hospital.medication.type', string='Medication Type')
    
    # Technical field to show in lists
    display_name = fields.Char(compute='_compute_display_name', store=True)
    
    @api.depends('name', 'category_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.category_id.name:
                record.display_name = f"{record.name} ({record.category_id.name})"
            else:
                record.display_name = record.name


class MedicationType(models.Model):
    _name = 'hospital.medication.type'
    _description = 'Medication Type'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    
    # Products related to this type
    product_ids = fields.One2many('hospital.medication.product', 'medication_type_id', string='Medication Products')

# Inheriting the product.product model to add medication-related fields
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    is_medication = fields.Boolean(string='Is Medication', default=False)
    medication_product_ids = fields.One2many('hospital.medication.product', 'product_id', 
                                           string='Medication Products')
    medication_type_id = fields.Many2one('hospital.medication.type', string='Medication Type')
    debit_note = fields.Boolean(string='Debit Note')
    medicine_product = fields.Boolean(string='Medicine Product')