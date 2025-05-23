# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Prescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('res.partner', string='Physician', required=True)
    prescription_date = fields.Date(string='Prescription Date', default=fields.Date.context_today)
    op_visit_id = fields.Many2one('op.visit', string='OP Visit')
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    line_ids = fields.One2many('hospital.prescription.line', 'prescription_id', string='Prescription Lines')
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    type = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP')
    ], string='Type', default='op', tracking=True)
    ip_number = fields.Char(string='IP Number', tracking=True)
    mrn_no = fields.Char(string='MRN No', tracking=True)
    picking_type = fields.Char(string='Picking Type', tracking=True)
    source_location = fields.Char(string='Source Location', tracking=True)
    destination_location = fields.Char(string='Destination Location', tracking=True)
    request_picking_type = fields.Text(string='Request Picking Type', tracking=True)
    return_picking_type = fields.Text(string='Return Picking Type', tracking=True)
    receive_method = fields.Selection([
        ('partial', 'Partial'),
        ('full', 'Full')
    ], string='Receive Method', default='partial', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    notes = fields.Text(string='Notes')
    medicine_register_ids = fields.One2many('medicine.register', 'prescription_id', string='Medicine Registers')
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.prescription') or _('New')
        return super(Prescription, self).create(vals_list)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.prescription') or _('New')
        return super(Prescription, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirm'
    
    def action_done(self):
        for record in self:
            record.state = 'done'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'

class PrescriptionLine(models.Model):
    _name = 'hospital.prescription.line'
    _description = 'Prescription Line'
    
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription', required=True)
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    dosage = fields.Char(string='Dosage')
    frequency_id = fields.Many2one('hospital.drug.frequency', string='Frequency')
    duration = fields.Char(string='Duration')
    route_id = fields.Many2one('hospital.drug.route', string='Route')
    note = fields.Text(string='Notes')

    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    speciality = fields.Char(string='Speciality')
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine')
    medicine_type = fields.Char(string='Type')
    start_date = fields.Date(string='From')
    end_date = fields.Date(string='TO')
    morning = fields.Boolean(string='M')
    afternoon = fields.Boolean(string='AN')
    evening = fields.Boolean(string='E')
    night = fields.Boolean(string='N')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    take = fields.Char(string='Take')
    form = fields.Char(string='Form')
    indication = fields.Char(string='Indication')
    frequency = fields.Char(string='Frequency')
