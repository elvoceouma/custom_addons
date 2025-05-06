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
    
    dispensing_store = fields.Char(string='Dispensing Store')
    emergency_store = fields.Char(string='Emergency Store')
    request_picking_type = fields.Char(string='Request Picking Type')
    return_picking_type = fields.Char(string='Return Picking Type')
    emergency_picking_type = fields.Char(string='Emergency Picking Type')
    
    room_count = fields.Integer( string='Rooms')
    bed_count = fields.Integer( string='Beds')
    hospital_id = fields.Many2one('hospital.hospital', string='Campus', required=True)
    
    room_ids = fields.One2many('hospital.room', 'block_id', string='Rooms')
    bed_ids = fields.One2many('hospital.bed', 'block_id', string='Beds')
    @api.depends('room_ids')
    def _compute_room_count(self):
        for record in self:
            record.room_count = len(record.room_ids)
            
    @api.depends('bed_ids')
    def _compute_bed_count(self):
        for record in self:
            record.bed_count = len(record.bed_ids)

    def action_hospital_bed(self):
        return {
            'name': _('Beds'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.bed',
            'type': 'ir.actions.act_window',
            'domain': [('block_id', '=', self.id)],
        }
    
    def action_hospital_room(self):
        return {
            'name': _('Rooms'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.room',
            'type': 'ir.actions.act_window',
            'domain': [('block_id', '=', self.id)],
        }