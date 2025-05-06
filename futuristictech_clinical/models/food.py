# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FoodRequisition(models.Model):
    _name = 'hospital.food.requisition'
    _description = 'Food Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    meal_type = fields.Selection([
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack')
    ], string='Meal Type')
    food_item_ids = fields.One2many('hospital.food.requisition.line', 'requisition_id', string='Food Items')
    special_instructions = fields.Text(string='Special Instructions')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.food.requisition') or _('New')
        return super(FoodRequisition, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_deliver(self):
        for record in self:
            record.state = 'delivered'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'


class FoodRequisitionLine(models.Model):
    _name = 'hospital.food.requisition.line'
    _description = 'Food Requisition Line'
    
    requisition_id = fields.Many2one('hospital.food.requisition', string='Requisition')
    food_item_id = fields.Many2one('hospital.food.item', string='Food Item')
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    note = fields.Text(string='Note')


class FoodItem(models.Model):
    _name = 'hospital.food.item'
    _description = 'Food Item'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    category = fields.Selection([
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('diabetic', 'Diabetic'),
        ('low_sodium', 'Low Sodium'),
        ('liquid', 'Liquid Diet')
    ], string='Category')
    calories = fields.Float(string='Calories')
    active = fields.Boolean(default=True)


class HospitalFoodRegister(models.Model):
    _name = 'hospital.food.register'
    _description = 'Hospital Food Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Food Register ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
    food_type = fields.Selection([
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
    ], string='Food Type', required=True)
    food_allergies = fields.Text(string='Food Allergies')
    food_preferences = fields.Text(string='Food Preferences')
    food_intolerance = fields.Text(string='Food Intolerance')
    food_restrictions = fields.Text(string='Food Restrictions')
    food_intake = fields.Text(string='Food Intake')
    food_intake_time = fields.Datetime(string='Food Intake Time')
    food_intake_quantity = fields.Float(string='Food Intake Quantity')
    food_intake_unit = fields.Selection([
        ('grams', 'Grams'),
        ('liters', 'Liters'),
        ('pieces', 'Pieces'),
    ], string='Food Intake Unit')
    food_intake_notes = fields.Text(string='Food Intake Notes')
    food_intake_status = fields.Selection([
        ('satisfied', 'Satisfied'),
        ('unsatisfied', 'Unsatisfied'),
        ('neutral', 'Neutral'),
    ], string='Food Intake Status')
    food_intake_feedback = fields.Text(string='Food Intake Feedback')
    food_intake_rating = fields.Integer(string='Food Intake Rating', default=0, required=True)
    food_intake_rating_comment = fields.Text(string='Food Intake Rating Comment')
    food_intake_rating_date = fields.Datetime(string='Food Intake Rating Date')
    food_intake_rating_time = fields.Datetime(string='Food Intake Rating Time')
    food_intake_rating_quantity = fields.Float(string='Food Intake Rating Quantity')
    food_intake_rating_unit = fields.Selection([
        ('grams', 'Grams'),
        ('liters', 'Liters'),
        ('pieces', 'Pieces'),
    ], string='Food Intake Rating Unit')
    food_intake_rating_notes = fields.Text(string='Food Intake Rating Notes')
    food_intake_rating_status = fields.Selection([
        ('satisfied', 'Satisfied'),
        ('unsatisfied', 'Unsatisfied'),
        ('neutral', 'Neutral'),
    ], string='Food Intake Rating Status')
    food_intake_rating_feedback = fields.Text(string='Food Intake Rating Feedback')
    food_intake_rating_feedback_date = fields.Datetime(string='Food Intake Rating Feedback Date')
    food_intake_rating_feedback_time = fields.Datetime(string='Food Intake Rating Feedback Time')
    food_intake_rating_feedback_quantity = fields.Float(string='Food Intake Rating Feedback Quantity')
    food_intake_rating_feedback_unit = fields.Selection([
        ('grams', 'Grams'),
        ('liters', 'Liters'),
        ('pieces', 'Pieces'),
    ], string='Food Intake Rating Feedback Unit')
    food_intake_rating_feedback_notes = fields.Text(string='Food Intake Rating Feedback Notes')
    food_intake_rating_feedback_status = fields.Selection([
        ('satisfied', 'Satisfied'),
        ('unsatisfied', 'Unsatisfied'),
        ('neutral', 'Neutral'),
    ], string='Food Intake Rating Feedback Status')
    food_intake_rating_feedback_feedback = fields.Text(string='Food Intake Rating Feedback Feedback')
    food_intake_rating_feedback_feedback_date = fields.Datetime(string='Food Intake Rating Feedback Feedback Date')
    food_intake_rating_feedback_feedback_time = fields.Datetime(string='Food Intake Rating Feedback Feedback Time')
    food_intake_rating_feedback_feedback_quantity = fields.Float(string='Food Intake Rating Feedback Feedback Quantity')
    food_intake_rating_feedback_feedback_unit = fields.Selection([
        ('grams', 'Grams'),
        ('liters', 'Liters'),
        ('pieces', 'Pieces'),
    ], string='Food Intake Rating Feedback Feedback Unit')


class HospitalFoodServicePayout(models.Model):
    _name = 'hospital.food.service.payout'
    _description = 'Hospital Food Service Payout'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Food Service Payout ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
    food_service_type = fields.Selection([
        ('hospital', 'Hospital'),
        ('home', 'Home'),
        ('other', 'Other'),
    ], string='Food Service Type', required=True)


class HospitalFoodbill(models.Model):
    _name = 'hospital.food.bill'
    _description = 'Hospital Food Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Food Bill ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
