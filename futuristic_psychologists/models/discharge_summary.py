from odoo import models, fields, api
from datetime import datetime


class DischargeSummary(models.Model):
    _name = 'discharge.summary'
    _description = 'Discharge Summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Reference', default='New', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('approve', 'Approved')
    ], string='State', default='draft', tracking=True)
    
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        required=True,
        tracking=True
    )
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        tracking=True
    )
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )
    
    # Approvers
    clinical_psychologist = fields.Many2one(
        'res.users',
        string='Clinical Psychologist',
        # domain="[('team_role', '=', 'clinical_psychologist')]",
        tracking=True
    )
    psychiatrist = fields.Many2one(
        'res.users',
        string='Psychiatrist',
        # domain="[('team_role', '=', 'psychiatrist')]",
        tracking=True
    )
    registrar = fields.Many2one(
        'res.users',
        string='Senior Registrar',
        # domain="[('team_role', '=', 'registrar')]",
        tracking=True
    )
    
    # Approval flags
    clinical_psychologist_bool = fields.Boolean(
        string='Clinical Psychologist Approved',
        default=False,
        invisible=True
    )
    psychiatrist_bool = fields.Boolean(
        string='Psychiatrist Approved',
        default=False,
        invisible=True
    )
    registrar_bool = fields.Boolean(
        string='Registrar Approved',
        default=False,
        invisible=True
    )
    
    description = fields.Html(string='Description')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('discharge.summary') or 'New'
        return super().create(vals)

    def action_confirm(self):
        """Confirm discharge summary"""
        self.write({'state': 'inprogress'})

    def action_approve_clinical_psychologist(self):
        """Approve by clinical psychologist"""
        self.write({
            'clinical_psychologist_bool': True,
            'clinical_psychologist': self.env.user.id
        })
        self._check_final_approval()

    def action_approve_psychiatrist(self):
        """Approve by psychiatrist"""
        self.write({
            'psychiatrist_bool': True,
            'psychiatrist': self.env.user.id
        })
        self._check_final_approval()

    def action_approve_registrar(self):
        """Approve by registrar"""
        self.write({
            'registrar_bool': True,
            'registrar': self.env.user.id
        })
        self._check_final_approval()

    def _check_final_approval(self):
        """Check if all approvals are done and finalize"""
        if (self.clinical_psychologist_bool and 
            self.psychiatrist_bool and 
            self.registrar_bool):
            self.write({'state': 'approve'})

    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id
            self.campus = self.inpatient_admission_id.campus