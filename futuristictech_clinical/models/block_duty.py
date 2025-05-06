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


