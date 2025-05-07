# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Room(models.Model):
    _name = 'hospital.room'
    _description = 'Hospital Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True)
    hospital_id = fields.Many2one(related='block_id.hospital_id', string='Campus', store=True)
    floor_number = fields.Selection(related='block_id.floor_number', string='Floor Number', store=True)
    
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
    
    # Location details
    location = fields.Char(string='Location', help="Specific location identifier for the room")
    is_private_room = fields.Boolean(string='Private Room')
    
    # Facilities
    telephone_access = fields.Boolean(string='Telephone access')
    private_bathroom = fields.Boolean(string='Private Bathroom')
    television = fields.Boolean(string='Television')
    refrigerator = fields.Boolean(string='Refrigerator')
    air_conditioning = fields.Boolean(string='Air Conditioning')
    guest_sofa_bed = fields.Boolean(string='Guest sofa-bed')
    internet_access = fields.Boolean(string='Internet Access')
    microwave = fields.Boolean(string='Microwave')
    
    # Additional information
    bio_hazard = fields.Boolean(string='Bio Hazard')
    price_tags = fields.Char(string='Price Tags')
    notes = fields.Text(string='Extra Information')
    
    # Related fields
    bed_ids = fields.One2many('hospital.bed', 'room_id', string='Beds')
    bed_count = fields.Integer(compute='_compute_bed_count', string='Bed Count')
    available_beds = fields.Integer(compute='_compute_available_beds', string='Available Beds')
    
    @api.depends('bed_ids')
    def _compute_bed_count(self):
        for record in self:
            record.bed_count = len(record.bed_ids)
    
    @api.depends('bed_ids.status')
    def _compute_available_beds(self):
        for record in self:
            record.available_beds = len(record.bed_ids.filtered(lambda b: b.status == 'available'))

    def action_view_beds(self):
        """Smart button action to view beds"""
        self.ensure_one()
        return {
            'name': _('Beds'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.bed',
            'type': 'ir.actions.act_window',
            'domain': [('room_id', '=', self.id)],
            'context': {
                'default_room_id': self.id,
                'default_block_id': self.block_id.id,
                'default_hospital_id': self.hospital_id.id,
            }
        }