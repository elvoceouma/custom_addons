# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class MedicineBox(models.Model):
    _name = 'hospital.medicine.box'
    _description = 'Medicine Box'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    ip_number = fields.Char(string='IP Number', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    
    box_location = fields.Char(string='Box Location')
    source_return_location = fields.Char(string='Source/Return Location')
    request_picking_type = fields.Char(string='Request Picking Type')
    return_picking_type = fields.Char(string='Return Picking Type')
    
    medicine_line_ids = fields.One2many('hospital.medicine.box.line', 'medicine_box_id', string='Medicine Lines')
    
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
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.medicine.box') or _('New')
        return super(MedicineBox, self).create(vals_list)
    
    @api.onchange('ip_number')
    def _onchange_ip_number(self):
        if self.ip_number:
            admission = self.env['hospital.admission'].search([('name', '=', self.ip_number)], limit=1)
            if admission:
                self.patient_id = admission.patient_id
    
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


class MedicineBoxLine(models.Model):
    _name = 'hospital.medicine.box.line'
    _description = 'Medicine Box Line'
    
    medicine_box_id = fields.Many2one('hospital.medicine.box', string='Medicine Box', required=True, ondelete='cascade')
    medicine_id = fields.Many2one('hospital.medicine', string='Medicine', required=True)
    quantity = fields.Float(string='Qty', default=1.0)
    outhand_qty = fields.Float(string='Outhand Qty')
    end_date = fields.Date(string='End Date')
    
    @api.onchange('medicine_id')
    def _onchange_medicine_id(self):
        if self.medicine_id:
            # You can set default values based on the selected medicine
            pass