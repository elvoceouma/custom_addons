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
    op_visit_id = fields.Many2one('hospital.op.visit', string='OP Visit')
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
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.prescription') or _('New')
        return super(Prescription, self).create(vals_list)


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