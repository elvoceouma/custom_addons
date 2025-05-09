# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Pharmacy(models.Model):
    _name = 'hospital.pharmacy'
    _description = 'Hospital Pharmacy'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    image = fields.Binary(string='Image')
    # Contact fields
    address = fields.Text(string='Address')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    state = fields.Char(string='State')
    zip = fields.Char(string='ZIP')
    country = fields.Char(string='Country')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    fax = fields.Char(string='Fax')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    location = fields.Char(string='Location')
    # Pharmacist
    pharmacist_id = fields.Many2one('res.users', string='Pharmacist')
    
    location_id = fields.Many2one('stock.location', string='Stock Location')
    active = fields.Boolean(default=True)
    hospital_id = fields.Many2one('hospital.hospital', string='Campus', required=True)
    
    # Related fields
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
    prescription_ids = fields.One2many(
        'hospital.prescription',
        'pharmacy_id',
        string='Prescriptions',
        help="Prescriptions processed at this pharmacy"
    )
    
    # Additional fields
    working_hours = fields.Text(string='Working Hours', help="Working hours of the pharmacy")
    emergency_service = fields.Boolean(string='Emergency Service', help="Indicates if the pharmacy provides emergency services")
    notes = fields.Text(string='Notes', help="Additional notes about the pharmacy")
    
    # Computed fields
    medicine_count = fields.Integer(compute='_compute_medicine_count', string='Medicines')
    prescription_count = fields.Integer(compute='_compute_prescription_count', string='Prescriptions')
    
    @api.depends('medicine_ids')
    def _compute_medicine_count(self):
        for record in self:
            record.medicine_count = len(record.medicine_ids)
    
    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = len(record.prescription_ids)
    
    def action_view_medicines(self):
        """Smart button action to view medicines"""
        self.ensure_one()
        return {
            'name': _('Medicines'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.medicine',
            'type': 'ir.actions.act_window',
            'domain': [('pharmacy_id', '=', self.id)],
            'context': {
                'default_pharmacy_id': self.id,
                'default_hospital_id': self.hospital_id.id,
            }
        }
    
    def action_view_prescriptions(self):
        """Smart button action to view prescriptions"""
        self.ensure_one()
        return {
            'name': _('Prescriptions'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.prescription',
            'type': 'ir.actions.act_window',
            'domain': [('pharmacy_id', '=', self.id)],
            'context': {
                'default_pharmacy_id': self.id,
            }
        }