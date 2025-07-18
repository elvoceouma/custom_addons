# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class MedicinePacking(models.Model):
    _name = 'hospital.medicine.packing'
    _description = 'Medicine Packing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'), tracking=True)
    
    packing_for = fields.Selection([
        ('inpatient', 'Inpatient'),
        ('discharge', 'Discharge'),
        ('outpatient', 'Outpatient')
    ], string='Packing For', default='inpatient', tracking=True)
    
    loa = fields.Boolean(string='LOA', default=False, tracking=True)
    discharge = fields.Boolean(string='Discharge', default=False, tracking=True)
    ip_number = fields.Char(string='IP Number', tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today, required=True, tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    discharge_date = fields.Date(string='Discharge Date', tracking=True)
    days_packed = fields.Integer(string='No. of Days Medicines Packed', default=1, tracking=True)
    
    medicine_line_ids = fields.One2many('hospital.medicine.packing.line', 'packing_id', string='Medicine Lines')
    
    notes = fields.Text(string='Notes')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    picking_type = fields.Many2one('stock.picking.type', string='Picking Type', required=True, tracking=True)
    packing_location = fields.Many2one('stock.location', string='Packing Location', required=True, tracking=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company, tracking=True)
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription', tracking=True)
    invisible_return_btn = fields.Boolean(string='Invisible Return Button', default=False)
    
    # Additional fields from the package details form
    bed_type_id = fields.Many2one('hospital.bed.type', string='Bed Type')
    referral_item_ids = fields.One2many('hospital.referral.item', 'referral_config_id', string='Referral Items')
    scale_ids = fields.One2many('hospital.referral.scale', 'referral_config_id', string='Scales')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.medicine.packing') or _('New')
        return super(MedicinePacking, self).create(vals_list)
    
    @api.onchange('days_packed', 'start_date')
    def _onchange_days_packed(self):
        if self.start_date and self.days_packed > 0:
            self.end_date = self.start_date + timedelta(days=self.days_packed)
    
    @api.onchange('ip_number')
    def _onchange_ip_number(self):
        if self.ip_number:
            admission = self.env['hospital.admission'].search([('name', '=', self.ip_number)], limit=1)
            if admission:
                self.patient_id = admission.patient_id
    
    def action_confirm(self):
        for record in self:
            record.state = 'in_progress'
    
    def action_in_progress(self):
        for record in self:
            record.state = 'in_progress'
    
    def action_close(self):
        for record in self:
            record.state = 'closed'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'


class MedicinePackingLine(models.Model):
    _name = 'hospital.medicine.packing.line'
    _description = 'Medicine Packing Line'
    
    packing_id = fields.Many2one('hospital.medicine.packing', string='Packing', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    type = fields.Selection([
        ('regular', 'Regular'),
        ('sos', 'SOS')
    ], string='Type', default='regular')
    
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    
    morning = fields.Boolean(string='M', default=False)
    afternoon = fields.Boolean(string='AN', default=False)
    evening = fields.Boolean(string='E', default=False)
    night = fields.Boolean(string='N', default=False)
    notes = fields.Text(string='Notes')
    
    @api.onchange('packing_id')
    def _onchange_packing_id(self):
        if self.packing_id:
            self.start_date = self.packing_id.start_date
            self.end_date = self.packing_id.end_date


class HospitalReferralItem(models.Model):
    _name = 'hospital.referral.item'
    _description = 'Hospital Referral Item'
    
    referral_config_id = fields.Many2one('hospital.medicine.packing', string='Referral Configuration')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price', default=0.0)


class HospitalReferralScale(models.Model):
    _name = 'hospital.referral.scale'
    _description = 'Hospital Referral Scale'
    
    referral_config_id = fields.Many2one('hospital.medicine.packing', string='Referral Configuration')
    scale_type = fields.Char(string='Scale Type', required=True)

class HospitalBedType(models.Model):
    _name = 'hospital.bed.type'
    _description = 'Hospital Bed Type'
    
    name = fields.Char(string='Bed Type', required=True)
    description = fields.Text(string='Description')
    capacity = fields.Integer(string='Capacity', default=1)
    hospital_id = fields.Many2one('hospital.hospital', string='Hospital', required=True)
    
  