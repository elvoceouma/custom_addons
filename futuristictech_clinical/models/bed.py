# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Bed(models.Model):
    _name = 'hospital.bed'
    _description = 'Hospital Bed'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    room_id = fields.Many2one('hospital.room', string='Room', required=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True)
    bed_type = fields.Selection([
        ('gatoh', 'Gatoh Bed'),
        ('standard', 'Standard Bed'),
        ('icu', 'ICU Bed'),
    ], string='Bed Type', default='gatoh', required=True, tracking=True)
    telephone_number = fields.Char(string='Telephone Number', tracking=True)
    reservation_charge = fields.Float(string='Reservation Charge')
    related_product = fields.Char(string='Related Product')
    
    status = fields.Selection([
        ('free', 'Free'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('not_available', 'Not Available')
    ], string='Status', default='free', tracking=True)
    
    current_patient_id = fields.Many2one('hospital.patient', string='Current Patient')
    
    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.block_id = self.room_id.block_id

    def action_change_bed_status(self):
        for record in self:
            if record.status == 'free':
                record.status = 'occupied'
            elif record.status == 'occupied':
                record.status = 'free'
            elif record.status == 'reserved':
                record.status = 'not_available'
            else:
                record.status = 'reserved'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Bed status changed successfully!',      
            }}