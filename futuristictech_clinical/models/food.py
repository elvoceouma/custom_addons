# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FoodRequisition(models.Model):
    _name = 'hospital.food.requisition'
    _description = 'Food Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='IP Number', domain="[('state','!=','discharge_advised')]")
    purpose = fields.Char(string='Purpose')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Date fields
    date_selection = fields.Selection([
        ('by_date', 'By Date'),
        ('by_period', 'By Period')
    ], string='Date Selection')
    requested_date = fields.Date(string='Requested Date')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    required_date = fields.Date(string='Required Date')
    approved_date = fields.Date(string='Approved Date', readonly=True)
    
    # Related documents
    debit_note_id = fields.Many2one('account.move', string='Debit Note', readonly=True)
    
    # User fields
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    
    # Lines
    requisition_line_ids = fields.One2many('hospital.food.requisition.line', 'requisition_id', string='Requisition Lines')
    
    # Statistics
    food_register_count = fields.Integer(string='Food Register Count', compute='_compute_food_register_count')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.food.requisition') or _('New')
        return super(FoodRequisition, self).create(vals_list)
    
    def action_approve(self):
        for record in self:
            record.state = 'approved'
            record.approved_by = self.env.user.id
            record.approved_date = fields.Date.today()
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def _compute_food_register_count(self):
        for record in self:
            record.food_register_count = self.env['hospital.food.register'].search_count([
                ('patient_id', '=', record.patient_id.id)
            ])
    
    def view_food_register(self):
        self.ensure_one()
        return {
            'name': _('Food Register'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.food.register',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id},
        }


class FoodRequisitionLine(models.Model):
    _name = 'hospital.food.requisition.line'
    _description = 'Food Requisition Line'
    
    requisition_id = fields.Many2one('hospital.food.requisition', string='Requisition')
    date = fields.Date(string='Date', related='requisition_id.requested_date')
    product_id = fields.Many2one('product.product', string='Product', 
                                domain=[('type', '=', 'service'), ('food_product', '=', True)])
    name = fields.Char(string='Description', related='product_id.name')
    internal_category_id = fields.Many2one('product.category', string='Product Category', 
                                          related='product_id.categ_id')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price


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
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', tracking=True)
    
    # Header Fields
    food_requisition_id = fields.Many2one('hospital.food.requisition', string='Food Requisition')
    inpatient_admission_id = fields.Many2one('hospital.inpatient.admission', string='Inpatient Admission', 
                                           domain=[('state', '!=', 'discharge_advised')])
    patient_id = fields.Many2one('hospital.patient', string='Patient', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)], required=True)
    
    # Product Fields
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    qty = fields.Float(string='Quantity', readonly=True)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    amount = fields.Float(string='Amount', readonly=True)
    
    # Company Fields
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, readonly=True)
    
    # Methods
    def action_approve(self):
        self.write({'state': 'approved'})
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.food.register') or _('New')
        return super(HospitalFoodRegister, self).create(vals_list)


class HospitalFoodServicePayout(models.Model):
    _name = 'hospital.food.service.payout'
    _description = 'Hospital Food Service Payout'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Food Service Payout ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    # Header Fields
    partner_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier', '=', True)])
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    
    # Payout Lines
    payout_line_ids = fields.One2many('hospital.food.service.payout.line', 'payout_id', string='Payout Lines')
    
    # Company Fields
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    
    # Methods
    def action_complete(self):
        self.write({'state': 'completed'})
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.food.service.payout') or _('New')
        return super(HospitalFoodServicePayout, self).create(vals_list)


class HospitalFoodServicePayoutLine(models.Model):
    _name = 'hospital.food.service.payout.line'
    _description = 'Food Service Payout Line'
    
    payout_id = fields.Many2one('hospital.food.service.payout', string='Payout')
    date = fields.Date(string='Date')
    reference = fields.Char(string='Reference')
    product_id = fields.Many2one('product.product', string='Product', domain=[('food_product', '=', True)])
    name = fields.Char(string='Description')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

class HospitalFoodBill(models.Model):
    _name = 'hospital.food.bill'
    _description = 'Hospital Food Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Food Bill ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    state = fields.Selection([
        ('new', 'New'),
        ('invoiced', 'Invoiced'),
    ], string='Status', default='new', tracking=True)
    
    # Header Fields
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        domain=[('state', '!=', 'discharge_advised')]
    )
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    bed_id = fields.Many2one('hospital.bed', string='Bed', required=True, tracking=True)
    ward_id = fields.Many2one('hospital.block', string='Block', required=True, tracking=True)
    building_id = fields.Many2one('hospital.block', string='Block', required=True, tracking=True)
    health_center_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    
    # Bill Lines
    bill_line_ids = fields.One2many('hospital.food.bill.line', 'bill_id', string='Bill Lines')
    
    # Company Fields
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user)
    
    # Methods
    def set_to_invoiced(self):
        self.write({'state': 'invoiced'})
    
    def view_invoice(self):
        # Implement your invoice viewing logic here
        pass
    
    def compute_price(self):
        # Implement your price computation logic here
        pass
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.food.bill') or _('New')
        return super(HospitalFoodBill, self).create(vals_list)


class HospitalFoodBillLine(models.Model):
    _name = 'hospital.food.bill.line'
    _description = 'Food Bill Line'
    
    bill_id = fields.Many2one('hospital.food.bill', string='Bill')
    date = fields.Date(string='Date')
    reference = fields.Char(string='Reference')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal', store=True)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit