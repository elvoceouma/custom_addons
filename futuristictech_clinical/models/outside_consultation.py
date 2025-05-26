# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class OutsideConsultation(models.Model):
    _name = 'hospital.outside.consultation'
    _description = 'Outside Consultation Advice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    
    # Basic information fields from screenshots
    age = fields.Integer(string='Age', related='patient_id.age', readonly=True)
    sex = fields.Selection(related='patient_id.gender', string='Sex', readonly=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    specialist_id = fields.Many2one('res.partner', string='Specialist')
    # speciality_id = fields.Many2one('medical.speciality', string='Speciality')
    # Fields from original implementation
    admission_id = fields.Many2one('hospital.admission', string='Admission', tracking=True)
    speciality_id = fields.Many2one('hospital.physician.speciality', string='Speciality', required=True, tracking=True)
    reason_for_referral = fields.Text(string='Reason for Referral')
    referral_date = fields.Date(string='Referral Date', default=fields.Date.context_today, tracking=True)
    advice = fields.Text(string='Advice')
    referred_by = fields.Char(string='Referred By')
    
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
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    
    # Additional fields for new UI
    type = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP')
    ], string='Type', default='op', required=True, tracking=True)
    
    op_visit_id = fields.Many2one('hospital.appointment', string='OP Reference', 
                                  domain="[('state', '=', 'confirmed')]", tracking=True)
    
    campus_id = fields.Many2one('hospital.hospital', string='Campus', tracking=True)
    psychiatrist_id = fields.Many2one('hospital.physician', string='Psychiatrist', tracking=True)
    doctor_id = fields.Many2one('hospital.physician', string='Doctor', tracking=True)
    
    partner_id = fields.Many2one('res.partner', string='Company', tracking=True)
    
    advised_date = fields.Date(string='Advised Date', tracking=True)
    planned_date = fields.Date(string='Planned Date', tracking=True)
    next_followup_date = fields.Date(string='Next Followup Date', tracking=True)
    next_followup_id = fields.Many2one('hospital.appointment', string='Next Followup', tracking=True)
    
    # Note field for advice page
    note = fields.Text(string='Advice')
    doctor_advice = fields.Text(string='Doctor Advice')
    precautions = fields.Text(string='Precautions')
    todo = fields.Text(string='Todo Before Next Consultation')
    
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # Extended states for new UI
    state = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('trip_planned', 'Trip Planned'),
        ('advised', 'Advised'),
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
                
            # If type is OP, find active OP visit
            if self.type == 'op':
                visit = self.env['hospital.appointment'].search([
                    ('patient_id', '=', self.patient_id.id),
                    ('state', '=', 'confirmed')
                ], limit=1)
                if visit:
                    self.op_visit_id = visit.id
    
    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'op':
            self.admission_id = False
        elif self.type == 'ip':
            self.op_visit_id = False
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_trip_planned(self):
        for record in self:
            record.state = 'trip_planned'
    
    def action_advise(self):
        for record in self:
            record.state = 'advised'
            record.advised_date = fields.Date.context_today(self)
    
    def action_done(self):
        for record in self:
            record.state = 'done'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'