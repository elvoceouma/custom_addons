# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Physician(models.Model):
    _name = 'hospital.physician'
    _description = 'Physician'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Physician Name', required=True, tracking=True)
    image = fields.Binary(string='Photo')
    
    # Qualifications
    degree_ids = fields.Many2many('hospital.physician.degree', string='Degrees', tracking=True)
    speciality_id = fields.Many2one('hospital.physician.speciality', string='Speciality', tracking=True)
    
    # Professional Info
    licence_id = fields.Char(string='Licence ID', tracking=True)
    consultancy_type = fields.Selection([
        ('residential', 'Residential'),
        ('visiting', 'Visiting'),
        ('consultant', 'Consultant'),
        ('honorary', 'Honorary')
    ], string='Consultancy Type', default='residential', tracking=True)
    
    consultancy_charge = fields.Float(string='Consultancy Charge', tracking=True)
    graduation_institute = fields.Char(string='Graduation Institute', tracking=True, 
                                     help='Institution where doctor completed education')
    is_pharmacist = fields.Boolean(string='Pharmacist?', default=False, tracking=True)
    
    # Contact Information
    working_institution = fields.Char(string='Working Institution', tracking=True)
    working_address = fields.Text(string='Working Address', tracking=True)
    work_mobile = fields.Char(string='Work Mobile', tracking=True)
    work_phone = fields.Char(string='Work Phone', tracking=True)
    work_email = fields.Char(string='Work Email', tracking=True)
    work_location = fields.Char(string='Work Location', tracking=True)
    
    responsible = fields.Char(string='Responsible', tracking=True)
    
    # Schedule
    availability_ids = fields.One2many('hospital.physician.availability', 'physician_id', string='Weekly Availability')
    
    # Stats
    appointment_count = fields.Integer(string='Appointments', compute='_compute_appointment_count')
    prescription_count = fields.Integer(string='Prescriptions', compute='_compute_prescription_count')
    
    # System Fields
    active = fields.Boolean(default=True, tracking=True)
    user_id = fields.Many2one('res.users', string='Related User', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                # Create a partner if needed
                partner = self.env['res.partner'].create({
                    'name': vals.get('name'),
                    'phone': vals.get('work_phone'),
                    'mobile': vals.get('work_mobile'),
                    'email': vals.get('work_email'),
                    'is_physician': True,
                })
                vals['partner_id'] = partner.id
                
        return super(Physician, self).create(vals_list)
    
    def _compute_appointment_count(self):
        for record in self:
            record.appointment_count = self.env['hospital.appointment'].search_count([
                ('physician_id', '=', record.id)
            ])
    
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = self.env['hospital.prescription'].search_count([
                ('physician_id', '=', record.id)
            ])
    
    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': _('Appointments'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.appointment',
            'view_mode': 'tree,form,calendar',
            'domain': [('physician_id', '=', self.id)],
            'context': {'default_physician_id': self.id},
        }
    
    def action_view_prescriptions(self):
        self.ensure_one()
        return {
            'name': _('Prescriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('physician_id', '=', self.id)],
            'context': {'default_physician_id': self.id},
        }


class PhysicianAvailability(models.Model):
    _name = 'hospital.physician.availability'
    _description = 'Physician Availability'
    
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True, ondelete='cascade')
    day = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string='Day', required=True)
    
    start_time = fields.Float(string='Start Time (24h format)', required=True)
    end_time = fields.Float(string='End Time (24h format)', required=True)
    
    @api.constrains('start_time', 'end_time')
    def _check_time_validity(self):
        for record in self:
            if record.start_time < 0 or record.start_time > 24:
                raise ValidationError(_('Start time must be between 0 and 24'))
            if record.end_time < 0 or record.end_time > 24:
                raise ValidationError(_('End time must be between 0 and 24'))
            if record.start_time >= record.end_time:
                raise ValidationError(_('End time must be greater than start time'))