# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class BlockDutyAssignment(models.Model):
    _name = 'hospital.block.duty.assignment'
    _description = 'Block Duty Assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    block_id = fields.Many2one('hospital.block', string='Block', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    shift = fields.Selection([
        ('morning', 'Morning Shift'),
        ('afternoon', 'Afternoon Shift'),
        ('night', 'Night Shift')
    ], string='Shift', required=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', required=True)
    assistant_ids = fields.Many2many('res.users', 'block_duty_user_rel', 'duty_id', 'user_id', string='Assistants')
    note = fields.Text(string='Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    code = fields.Char(string='Code')
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    duty_roster_id = fields.Many2one('hospital.duty.roster', string='Duty Roster', tracking=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    assignment_line_ids = fields.One2many('hospital.block.duty.assignment.line', 'assignment_id', string='Assignment Lines')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.block.duty.assignment') or _('New')
        return super(BlockDutyAssignment, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_done(self):
        for record in self:
            record.state = 'done'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'


class BlockDutyRegister(models.Model):
    _name = 'hospital.block.duty.register'
    _description = 'Block Duty Register'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    assignment_id = fields.Many2one('hospital.block.duty.assignment', string='Assignment', required=True)
    block_id = fields.Many2one(related='assignment_id.block_id', string='Block', store=True)
    date = fields.Date(related='assignment_id.date', string='Date', store=True)
    shift = fields.Selection(related='assignment_id.shift', string='Shift', store=True)
    responsible_id = fields.Many2one(related='assignment_id.responsible_id', string='Responsible', store=True)
    registration_time = fields.Datetime(string='Registration Time', default=fields.Datetime.now)
    checklist_ids = fields.One2many('hospital.block.duty.checklist.line', 'register_id', string='Checklist Items')
    notes = fields.Text(string='Notes')

    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True)
    duty_roster_id = fields.Many2one('hospital.duty.roster', string='Duty Roster', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    register_line_ids = fields.One2many('hospital.block.duty.register.line', 'register_id', string='Register Lines')
    notes = fields.Text(string='Notes')
    
    # Patient related fields for reporting
    patient_reporting_ids = fields.One2many('hospital.block.duty.patient.reporting', 'register_id', string='Patient Reporting')
    
    # Block related fields for reporting
    block_reporting_ids = fields.One2many('hospital.block.duty.block.reporting', 'register_id', string='Block Reporting')
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.block.duty.register') or _('New')
            if vals.get('assignment_id'):
                assignment = self.env['hospital.block.duty.assignment'].browse(vals['assignment_id'])
                checklist_items = self.env['hospital.block.duty.checklist'].search([('block_id', '=', assignment.block_id.id)])
                checklist_lines = []
                for item in checklist_items:
                    checklist_lines.append((0, 0, {
                        'checklist_id': item.id,
                        'name': item.name,
                        'completed': False
                    }))
                vals['checklist_ids'] = checklist_lines
        return super(BlockDutyRegister, self).create(vals_list)

     
    def action_assign(self):
        for record in self:
            record.state = 'assigned'
    
    def action_complete(self):
        for record in self:
            record.state = 'completed'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'


class BlockDutyChecklist(models.Model):
    _name = 'hospital.block.duty.checklist'
    _description = 'Block Duty Checklist'
    
    name = fields.Char(string='Name', required=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)


class BlockDutyChecklistLine(models.Model):
    _name = 'hospital.block.duty.checklist.line'
    _description = 'Block Duty Checklist Line'
    
    register_id = fields.Many2one('hospital.block.duty.register', string='Register')
    checklist_id = fields.Many2one('hospital.block.duty.checklist', string='Checklist Item')
    name = fields.Char(string='Name', required=True)
    completed = fields.Boolean(string='Completed')
    completion_time = fields.Datetime(string='Completion Time')
    completed_by = fields.Many2one('res.users', string='Completed By')
    remarks = fields.Text(string='Remarks')
    
    def action_complete(self):
        for record in self:
            record.completed = True
            record.completion_time = fields.Datetime.now()
            record.completed_by = self.env.user.id


class HospitalBlockDutyReport(models.Model):
    _name = 'hospital.block.duty.report'
    _description = 'Block Duty Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    # block_id = fields.Many2one('hospital.block', string='Block', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    shift = fields.Selection([
        ('morning', 'Morning Shift'),
        ('afternoon', 'Afternoon Shift'),
        ('night', 'Night Shift')
    ], string='Shift', required=True)
    # responsible_id = fields.Many2one('res.users', string='Responsible', required=True)
    report_time = fields.Datetime(string='Report Time', default=fields.Datetime.now)
    # report_lines = fields.One2many('hospital.block.duty.report.line', 'report_id', string='Report Lines')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.block.duty.report') or _('New')
        return super(HospitalBlockDutyReport, self).create(vals_list)

class HospitalBlockDutyAssignmentLine(models.Model):
    _name = 'hospital.block.duty.assignment.line'
    _description = 'Block Duty Assignment Line'
    
    assignment_id = fields.Many2one('hospital.block.duty.assignment', string='Assignment')
    date = fields.Date(string='Date')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    duty_roster_id = fields.Many2one('hospital.duty.roster', string='Duty Roster')
    block_id = fields.Many2one('hospital.block', string='Block')
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

class HospitalDutyRoster(models.Model):
    _name = 'hospital.duty.roster'
    _description = 'Hospital Duty Roster'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    active = fields.Boolean(default=True)

class HospitalBlockDutyRegisterLine(models.Model):
    _name = 'hospital.block.duty.register.line'
    _description = 'Block Duty Register Line'
    
    register_id = fields.Many2one('hospital.block.duty.register', string='Register')
    name = fields.Char(string='Name')
    response = fields.Char(string='Response')


class HospitalBlockDutyPatientReporting(models.Model):
    _name = 'hospital.block.duty.patient.reporting'
    _description = 'Block Duty Patient Reporting'
    
    register_id = fields.Many2one('hospital.block.duty.register', string='Register')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    type = fields.Char(string='Type')
    description = fields.Text(string='Description')


class HospitalBlockDutyBlockReporting(models.Model):
    _name = 'hospital.block.duty.block.reporting'
    _description = 'Block Duty Block Reporting'
    
    register_id = fields.Many2one('hospital.block.duty.register', string='Register')
    type = fields.Char(string='Type')
    description = fields.Text(string='Description')
