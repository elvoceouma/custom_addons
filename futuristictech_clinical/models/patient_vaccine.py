# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta

class PatientVaccine(models.Model):
    _name = 'hospital.patient.vaccine'
    _description = 'Patient Vaccine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'vaccine_id'
    
    name = fields.Char(string='Name', required=True, tracking=True)
    vaccine_id = fields.Many2one('hospital.vaccine', string='Vaccine', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    dose_number = fields.Integer(string='Dose #', default=1, tracking=True)
    vaccination_date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)], tracking=True)
    institution = fields.Char(string='Institution', tracking=True)
    observations = fields.Text(string='Observations')
    next_dose_date = fields.Date(string='Next Dose Date', compute='_compute_next_dose_date', store=True)
    dose_number = fields.Integer(string="Dose number")
    name = fields.Char(string='Name', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    vaccine_id = fields.Many2one('hospital.vaccine', string='Vaccine')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    next_dose_date = fields.Date(string='Next Dose Date')
    note = fields.Text(string='Notes')

    @api.depends('vaccination_date', 'vaccine_id')
    def _compute_next_dose_date(self):
        for record in self:
            if record.vaccination_date and record.vaccine_id and record.vaccine_id.days_between_doses > 0:
                record.next_dose_date = record.vaccination_date + timedelta(days=record.vaccine_id.days_between_doses)
            else:
                record.next_dose_date = False
    
    def action_save(self):
        # Return a client action that refreshes the form view
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
    def action_discard(self):
        # Return to the list view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.patient.vaccine',
            'view_mode': 'tree,form',
            'target': 'current',
        }


class Vaccine(models.Model):
    _name = 'hospital.vaccine'
    _description = 'Vaccine'
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                       default=lambda: _('New'))
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    days_between_doses = fields.Integer(string='Days Between Doses', default=0,
                                      help='Number of days between doses. If 0, no next dose is required.')
    num_doses = fields.Integer(string='Number of Doses', default=1,
                             help='Total number of doses required for this vaccine.')
    manufacturer = fields.Char(string='Manufacturer')
    active = fields.Boolean(default=True)
    patient_vaccine_ids = fields.One2many('hospital.patient.vaccine', 'vaccine_id', string='Patient Vaccines')
    vaccine_type_id = fields.Many2one('hospital.vaccine.type', string='Vaccine Type', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    dose_number = fields.Integer(string='Dose Number', default=1)
    next_dose_date = fields.Date(string='Next Dose Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('administered', 'Administered'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Vaccine name must be unique!'),
    ]