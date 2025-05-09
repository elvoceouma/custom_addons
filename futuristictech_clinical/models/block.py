# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Block(models.Model):
    _name = 'hospital.block'
    _description = 'Hospital Block'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    floor_number = fields.Selection([
        ('0', 'GROUND FLOOR'),
        ('1', '1st FLOOR'),
        ('2', '2nd FLOOR'),
        ('3', '3rd FLOOR'),
    ], string='Floor Number', required=True, tracking=True)
    active = fields.Boolean(string='Active', default=True)
    dispensing_store = fields.Many2one('stock.location', string='Dispensing Store')
    emergency_store = fields.Many2one('stock.location', string='Emergency Store')
    request_picking_type = fields.Many2one('stock.picking.type', string='Request Picking Type')
    return_picking_type = fields.Many2one('stock.picking.type', string='Return Picking Type')
    emergency_picking_type = fields.Many2one('stock.picking.type', string='Emergency Picking Type')
    
    room_count = fields.Integer(compute='_compute_room_count', string='Rooms')
    bed_count = fields.Integer(compute='_compute_bed_count', string='Beds')
    hospital_id = fields.Many2one('hospital.hospital', string='Campus', required=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    room_ids = fields.One2many('hospital.room', 'block_id', string='Rooms')
    bed_ids = fields.One2many('hospital.bed', 'block_id', string='Beds')
    
    # Additional field for extra information
    notes = fields.Text(string='Extra Information')
    description = fields.Text(string='Description')
    @api.depends('room_ids')
    def _compute_room_count(self):
        for record in self:
            record.room_count = len(record.room_ids)
            
    @api.depends('bed_ids')
    def _compute_bed_count(self):
        for record in self:
            record.bed_count = len(record.bed_ids)

    def action_view_rooms(self):
        """Smart button action to view rooms"""
        self.ensure_one()
        return {
            'name': _('Rooms'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.room',
            'type': 'ir.actions.act_window',
            'domain': [('block_id', '=', self.id)],
            'context': {
                'default_block_id': self.id,
                'default_hospital_id': self.hospital_id.id,
            }
        }
    
    def action_view_beds(self):
        """Smart button action to view beds"""
        self.ensure_one()
        return {
            'name': _('Beds'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.bed',
            'type': 'ir.actions.act_window',
            'domain': [('block_id', '=', self.id)],
            'context': {
                'default_block_id': self.id,
                'default_hospital_id': self.hospital_id.id,
            }
        }

    def action_hospital_room(self):
        return self.action_view_rooms()
    
    def action_hospital_bed(self):
        return self.action_view_beds()