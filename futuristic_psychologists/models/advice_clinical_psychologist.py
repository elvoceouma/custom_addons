from odoo import models, fields, api
from datetime import datetime


class AdviceClinicalPsychologist(models.Model):
    _name = 'advice.clinical.psychologist'
    _description = 'Advice to Clinical Psychologist'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    
    clinical_psychologist_id = fields.Many2one(
        'res.users',
        string='Clinical Psychologist',
        required=True,
        # domain="[('team_role', '=', 'clinical_psychologist')]",
        tracking=True
    )
    followup_type_id = fields.Many2one(
        'followup.type',
        string='Follow-up Type',
        tracking=True
    )
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    
    type = fields.Selection([
        ('ip', 'Inpatient'),
        ('op', 'Outpatient')
    ], string='Type', required=True, default='op', tracking=True)
    
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        tracking=True
    )
    op_visit_id = fields.Many2one(
        'op.visit',
        string='OP Visit',
        tracking=True
    )
    patient_id = fields.Many2one(
        'res.partner', 
        string='Patient',
        required=True,
        tracking=True
    )

    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    
    note = fields.Html(string='Advice', required=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('advice.clinical.psychologist') or 'New'
        return super().create(vals)

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'ip':
            self.op_visit_id = False
        else:
            self.inpatient_admission_id = False

    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id

    @api.onchange('op_visit_id')
    def _onchange_op_visit_id(self):
        if self.op_visit_id:
            self.patient_id = self.op_visit_id.patient_id