# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Room(models.Model):
    _name = 'hospital.room'
    _description = 'Hospital Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True)
    # floor_number = fields.Selection(related='block_id.floor_number', string='Floor Number', store=True)
    # In block.py
    floor_number = fields.Selection([
        ('0', 'GROUND FLOOR'),
        ('1', '1st FLOOR'),
        ('2', '2nd FLOOR'),
        ('3', '3rd FLOOR'),
    ], string='Floor Number', required=True, tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex')
    ], string='Gender', default='unisex', tracking=True)
    
    room_type = fields.Selection([
        ('private', 'PRIVATE'),
        ('private_room', 'PRIVATE ROOM'),
        ('semi_private', 'SEMI PRIVATE'),
        ('suite_room', 'SUITE ROOM'),
        ('deluxe_room', 'DELUXE ROOM'),
        ('recovery_room', 'RECOVERY ROOM'),
        ('emergency', 'EMERGENCY'),
        ('day_care', 'DAY CARE'),
        ('dormitory', 'Dormitory')
    ], string='Room Type', required=True, tracking=True)
    
    bed_ids = fields.One2many('hospital.bed', 'room_id', string='Beds')
    bed_count = fields.Integer(compute='_compute_bed_count', string='Bed Count')
    
    @api.depends('bed_ids')
    def _compute_bed_count(self):
        for record in self:
            record.bed_count = len(record.bed_ids)