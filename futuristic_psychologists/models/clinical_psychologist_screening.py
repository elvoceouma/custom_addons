from odoo import models, fields, api
from datetime import datetime, timedelta


class ClinicalPsychologistScreening(models.Model):
    _name = 'clinical.psychologist.screening'
    _description = 'Clinical Psychologist Screening'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    user_id = fields.Many2one(
        'res.users', 
        string='Created By', 
        default=lambda self: self.env.user,
        readonly=True
    )
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
        readonly=True,
        tracking=True
    )
    patient_age = fields.Integer(
        string='Age', 
        readonly=True,
        # related='patient_id.age'
    )
    sex = fields.Selection(
        [('male', 'Male'),
         ('female', 'Female'),
         ('other', 'Other')],
        string='Sex',
        readonly=True
    )
    
    date = fields.Date(
        string='Screening Date', 
        default=fields.Date.context_today, 
        required=True, 
        tracking=True
    )
    
    note = fields.Html(string='Notes', required=True)
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company,
        readonly=True
    )
    psychologist_id = fields.Many2one(
        'res.users',
        string='Psychologist',
        required=True,
        tracking=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('clinical.psychologist.screening') or 'New'
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

    def action_view_screening(self):
        """View Screening Details"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Screening Details',
            'res_model': 'clinical.psychologist.screening',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
    
    def action_next_followup(self):
        """Action to set next follow-up date"""
        next_followup_date = datetime.now().date() + timedelta(days=30)
        self.write({
            'date': next_followup_date
        })

    def action_counsellor_session(self):
        """Action to create a new counsellor session"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Counsellor Session',
            'res_model': 'counsellor.session',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
                'default_op_visit_id': self.op_visit_id.id
            }
        }