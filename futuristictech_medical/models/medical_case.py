from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalCase(models.Model):
    _name = 'medical.case'
    _description = 'Patient Medical Case'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Case Reference', required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'medical.patient', string='Patient', required=True, tracking=True)
    doctor_id = fields.Many2one(
        'medical.doctor', string='Doctor', required=True, tracking=True)
    department_id = fields.Many2one(
        'medical.department', string='Department',
        related='doctor_id.department_id', store=True)
    hospital_id = fields.Many2one(
        'medical.hospital', string='Hospital',
        related='department_id.hospital_id', store=True)
    symptoms = fields.Text(string='Symptoms', tracking=True)
    diagnosis = fields.Text(string='Diagnosis', tracking=True)
    treatment_ids = fields.One2many(
        'medical.treatment', 'case_id', string='Treatments')
    prescription_ids = fields.One2many(
        'medical.prescription', 'case_id', string='Prescriptions')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    date_start = fields.Datetime(
        string='Start Date', default=fields.Datetime.now)
    date_end = fields.Datetime(string='End Date')
    note = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.case') or _('New')
        return super(MedicalCase, self).create(vals)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({
            'state': 'completed',
            'date_end': fields.Datetime.now()
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            return {
                'domain': {
                    'doctor_id': [('department_id', '=', self.patient_id.department_id.id)]
                }
            }
        return {}