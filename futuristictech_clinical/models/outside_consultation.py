# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class OutsideConsultation(models.Model):
    _name = 'hospital.outside.consultation'
    _description = 'Outside Consultation Advice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission', tracking=True)
    
    speciality_id = fields.Many2one('hospital.physician.speciality', string='Speciality', required=True, tracking=True)
    reason_for_referral = fields.Text(string='Reason for Referral')
    referral_date = fields.Date(string='Referral Date', default=fields.Date.context_today, tracking=True)
    
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='low', tracking=True)
    
    advisor_id = fields.Many2one('res.users', string='Advisor', default=lambda self: self.env.user, tracking=True)
    external_doctor = fields.Char(string='External Doctor', tracking=True)
    
    findings = fields.Text(string='Findings')
    recommendations = fields.Text(string='Recommendations')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.outside.consultation') or _('New')
        return super(OutsideConsultation, self).create(vals_list)
    
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            # Find active admission for this patient
            admission = self.env['hospital.admission'].search([
                ('patient_id', '=', self.patient_id.id),
                ('state', 'in', ['admission_confirmed', 'invoiced', 'completed'])
            ], limit=1)
            if admission:
                self.admission_id = admission.id
    
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