from odoo import models, fields, api, _

class VisitsActivities(models.Model):
    _name = 'visits.activities'
    _description = 'Visit Activities'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    lead_id = fields.Many2one('crm.lead', string='Lead')
    activity_type = fields.Selection([
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('email', 'Email'),
        ('followup', 'Follow Up'),
        ('other', 'Other')
    ], string='Activity Type')
    activity_date = fields.Datetime(string='Activity Date')
    activity_owner = fields.Many2one('res.users', string='Activity Owner')
    activity_status = fields.Selection([
        ('planned', 'Planned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled')
    ], string='Activity Status')
    rescheduled_date = fields.Datetime(string='Rescheduled Date')
    reschedule_reason = fields.Char(string='Reschedule Reason')
    activity_description = fields.Text(string='Activity Description')
    clinical_trail = fields.Boolean(string='Clinical Trail')
    events = fields.Boolean(string='Events')


class OpVisit(models.Model):
    _name = 'op.visit'
    _description = 'OP Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    patient_id = fields.Many2one('medical.patient', string='Patient')
    visit_date = fields.Datetime(string='Visit Date')
    visit_type = fields.Selection([
        ('new', 'New'),
        ('followup', 'Follow Up'),
        ('emergency', 'Emergency')
    ], string='Visit Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    doctor_id = fields.Many2one('medical.doctor', string='Doctor')
    visit_reason = fields.Text(string='Visit Reason')
    visit_notes = fields.Text(string='Visit Notes')