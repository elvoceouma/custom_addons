from odoo import _, api, fields, models

class Evaluation(models.Model):
    _name = 'hospital.evaluation'
    _description = 'Patient Evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    
    name = fields.Char(string='Evaluation #', required=True, readonly=True, default=lambda self: 'New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', tracking=True)
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment #')
    date = fields.Date(string='Evaluation Date', default=fields.Date.context_today, tracking=True)
    
    # Clinical data
    indication = fields.Char(string='Indication')
    height = fields.Float(string='Height (cm)')
    weight = fields.Float(string='Weight (kg)')
    bmi = fields.Float(string='Body Mass Index (BMI)', compute='_compute_bmi', store=True)
    temperature = fields.Float(string='Temperature (°C)')
    pulse = fields.Integer(string='Pulse')
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    systolic_bp = fields.Integer(string='Systolic BP')
    diastolic_bp = fields.Integer(string='Diastolic BP')
    
    evaluation_type = fields.Selection([
        ('initial', 'Initial'),
        ('followup', 'Follow-up'),
        ('annual', 'Annual'),
        ('emergency', 'Emergency'),
    ], string='Evaluation Type', default='initial', tracking=True)
    
    observation = fields.Text(string='Observation')
    diagnosis = fields.Text(string='Diagnosis')
    treatment_plan = fields.Text(string='Treatment Plan')
    notes = fields.Text(string='Notes')
    
    @api.depends('height', 'weight')
    def _compute_bmi(self):
        for record in self:
            if record.height and record.weight and record.height > 0:
                record.bmi = record.weight / ((record.height / 100) ** 2)
            else:
                record.bmi = 0
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.evaluation') or 'New'
        return super(Evaluation, self).create(vals)


class HospitalGynacology(models.Model):
    _name = 'hospital.gynecology'
    _description = 'Hospital Gynacology'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Gynacology ID', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    evaluation_date = fields.Datetime(string='Evaluation Date', required=True)
    evaluation_type_id = fields.Many2one('hospital.evaluation.type', string='Evaluation Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')
    notes = fields.Text(string='Notes')
