# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Pharmacy(models.Model):
    _name = 'hospital.pharmacy'
    _description = 'Hospital Pharmacy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    location_id = fields.Many2one('stock.location', string='Stock Location')
    active = fields.Boolean(default=True)
    hospital_id = fields.Many2one('hospital.hospital', string='Campus', required=True)
    stock_picking_type_ids = fields.Many2many(
        'stock.picking.type', 
        string='Operation Types',
        help="Operation types associated with this pharmacy"
    )
    medicine_ids = fields.One2many(
        'hospital.medicine', 
        'pharmacy_id',  
        string='Medicines',
        help="Medicines available in this pharmacy"
    )
    # staff_ids = fields.One2many(
    #     '', 
    #     'pharmacy_id',  
    #     string='Staff',
    #     help="Staff members working in this pharmacy"
    # )
    working_hours = fields.Text(string='Working Hours', help="Working hours of the pharmacy")   
    emergency_service = fields.Boolean(string='Emergency Service', help="Indicates if the pharmacy provides emergency services")
    notes = fields.Text(string='Notes', help="Additional notes about the pharmacy")


class HospitalTabletCapsule(models.Model):
    _name = 'hospital.tablet.capsule'
    _description = 'Hospital Tablet Capsule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    active = fields.Boolean(default=True)
    hospital_id = fields.Many2one('hospital.hospital', string='Campus', required=True)
    pharmacy_id = fields.Many2one('hospital.pharmacy', string='Pharmacy', required=True)