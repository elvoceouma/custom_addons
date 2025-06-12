from odoo import models, fields, api
from datetime import datetime


class PsychometricAssessment(models.Model):
    _name = 'psychometric.assessment'
    _description = 'Psychometric Assessment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        tracking=True
    )
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        readonly=True,
        tracking=True
    )
    patient_age = fields.Integer(
        string='Age',
        # related='patient_id.age',
        readonly=True
    )
    sex = fields.Selection(
        [('male', 'Male'),
         ('female', 'Female')],
        string='Sex',
        readonly=True
    )
    
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    psychiatrist_id = fields.Many2one(
        'res.users',
        string='Psychiatrist',
        # domain="[('team_role', '=', 'psychiatrist')]",
        tracking=True
    )
    assessment_type_id = fields.Many2one(
        'assessment.type',
        string='Assessment Type',
        tracking=True
    )
    
    note = fields.Html(string='Notes')
    
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('psychometric.assessment') or 'New'
        return super().create(vals)

    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id