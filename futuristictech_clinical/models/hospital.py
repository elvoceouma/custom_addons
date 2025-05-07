# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Hospital(models.Model):
    _name = 'hospital.hospital'
    _description = 'Hospital'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    type = fields.Selection([
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('nursing_home', 'Nursing Home'),
        ('community_health_centre', 'Community Health Centre'),
        ('military_health_facility', 'Military Health Facility'),
        ('others', 'Others'),
    ], string='Type', default='hospital')
    image = fields.Binary(string='Image')
    notes = fields.Text(string='Note')
    # Address fields
    address = fields.Text(string='Address')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip = fields.Char(string='ZIP')
    country = fields.Char(string='Country')
    
    # Contact fields
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    
    active = fields.Boolean(default=True)
    
    # Relationships
    block_ids = fields.One2many('hospital.block', 'hospital_id', string='Blocks')
    pharmacy_ids = fields.One2many('hospital.pharmacy', 'hospital_id', string='Pharmacies')
    block_count = fields.Integer(compute='_compute_block_count', string='Blocks')
    pharmacy_count = fields.Integer(compute='_compute_pharmacy_count', string='Pharmacies')
    
    # Inventory-related fields
    patient_requisition_picking_type_id = fields.Many2one('stock.picking.type', string='Patient Requisition Picking Type')
    store_clearance_picking_type_id = fields.Many2one('stock.picking.type', string='Store Clearance Picking Type')
    medicine_packing_picking_type_id = fields.Many2one('stock.picking.type', string='Medicine Packing Picking Type')
    
    @api.depends('block_ids')
    def _compute_block_count(self):
        for record in self:
            record.block_count = len(record.block_ids)
    
    @api.depends('pharmacy_ids')
    def _compute_pharmacy_count(self):
        for record in self:
            record.pharmacy_count = len(record.pharmacy_ids)

    def action_hospital_room(self):
        return {
            'name': _('Rooms'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.room',
            'type': 'ir.actions.act_window',
            'domain': [('hospital_id', '=', self.id)],
        }