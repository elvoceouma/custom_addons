# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FollowUpSheet(models.Model):
    _name = 'hospital.follow.up.sheet'
    _description = 'Follow-Up Sheet'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    
    title = fields.Char(string='Title', default='Follow-Up Sheet')
    ip_number = fields.Char(string='IP Number', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    last_updated_date = fields.Date(string='Last Updated Date')
    
    hygiene_detail_ids = fields.One2many('hospital.hygiene.detail', 'follow_up_sheet_id', string='Hygiene Details')
    formal_activity_ids = fields.One2many('hospital.activity.record', 'follow_up_sheet_id', string='Formal Activities',
                                        domain=[('activity_type', '=', 'formal')])
    informal_activity_ids = fields.One2many('hospital.activity.record', 'follow_up_sheet_id', string='Informal Activities',
                                          domain=[('activity_type', '=', 'informal')])
    family_session_ids = fields.One2many('hospital.family.session', 'follow_up_sheet_id', string='Family Sessions')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        return super(FollowUpSheet, self).create(vals_list)
    
    @api.onchange('ip_number')
    def _onchange_ip_number(self):
        if self.ip_number:
            admission = self.env['hospital.admission'].search([('name', '=', self.ip_number)], limit=1)
            if admission:
                self.patient_id = admission.patient_id
    
    def action_get_details(self):
        self.ensure_one()
        self.last_updated_date = fields.Date.today()
        return True
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_done(self):
        for record in self:
            record.state = 'done'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'


class HygieneDetail(models.Model):
    _name = 'hospital.hygiene.detail'
    _description = 'Hygiene Detail'
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    parameter = fields.Char(string='Parameter', required=True)
    value = fields.Char(string='Value')
    notes = fields.Text(string='Notes')


class ActivityRecord(models.Model):
    _name = 'hospital.activity.record'
    _description = 'Activity Record'
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    activity = fields.Char(string='Activity')
    comments = fields.Text(string='Comments')
    activity_type = fields.Selection([
        ('formal', 'Formal'),
        ('informal', 'Informal')
    ], string='Activity Type', required=True, default='formal')


class FamilySession(models.Model):
    _name = 'hospital.family.session'
    _description = 'Family Session'
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    purpose = fields.Char(string='Purpose of the Session')
    matters_discussed = fields.Text(string='Matters Discussed')
    observation = fields.Text(string='Observation')
    outcome = fields.Text(string='Outcome')
    future_plan = fields.Text(string='Future Plan')