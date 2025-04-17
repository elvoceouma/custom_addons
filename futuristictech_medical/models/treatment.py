from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalTreatment(models.Model):
    _name = 'medical.treatment'
    _description = 'Medical Treatment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Treatment Reference', required=True, readonly=True, default=lambda self: _('New'))
    case_id = fields.Many2one(
        'medical.case', string='Medical Case', required=True, ondelete='cascade')
    patient_id = fields.Many2one(
        'medical.patient', string='Patient',
        related='case_id.patient_id', store=True)
    doctor_id = fields.Many2one(
        'medical.doctor', string='Doctor',
        related='case_id.doctor_id', store=True)
    treatment_type_id = fields.Many2one(
        'medical.treatment.type', string='Treatment Type', required=True)
    description = fields.Text(string='Description')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    duration = fields.Float(string='Duration (hours)')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')],
        string='Status', default='planned', tracking=True)
    notes = fields.Text(string='Notes')
    cost = fields.Float(string='Cost')
    payment_ids = fields.One2many(
        'medical.payment', 'treatment_id', string='Payments')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.treatment') or _('New')
        return super(MedicalTreatment, self).create(vals)

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.constrains('duration')
    def _check_duration(self):
        for treatment in self:
            if treatment.duration <= 0:
                raise ValidationError(
                    _('Treatment duration must be positive!'))
            

class MedicalTreatmentType(models.Model):
    _name = 'medical.treatment.type'
    _description = 'Medical Treatment Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Treatment Type', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')
    treatment_ids = fields.One2many(
        'medical.treatment', 'treatment_type_id', string='Treatments')