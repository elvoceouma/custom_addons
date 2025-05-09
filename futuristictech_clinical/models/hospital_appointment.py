from odoo import _, api, fields, models

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Appointment #', required=True, readonly=True, copy=False, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    physician_id = fields.Many2one('hospital.physician', string='Physician', required=True)
    appointment_date = fields.Datetime(string='Appointment Date', required=True)
    health_center_id = fields.Many2one('hospital.campus', string='Health Center')
    duration = fields.Float(string='Duration (Hours)', default=1.0)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)

    # Added patient status and urgency level
    patient_status = fields.Selection([
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
        ('emergency', 'Emergency')
    ], string='Patient Status', default='outpatient')
    
    urgency_level = fields.Selection([
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency')
    ], string='Urgency Level', default='normal')
    
    # Comments section
    comments = fields.Text(string='Comments')
    
    # Updated state to match the UI
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    appointment_type_id = fields.Many2one('hospital.appointment.type', string='Appointment Type')
    
    # For evaluations tab
    evaluation_ids = fields.One2many('hospital.appointment.evaluation', 'appointment_id', string='Evaluations')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        return super(HospitalAppointment, self).create(vals_list)
    
    def action_schedule(self):
        for record in self:
            record.state = 'scheduled'
    
    def action_complete(self):
        for record in self:
            record.state = 'completed'
    
    def action_invoice(self):
        for record in self:
            record.state = 'invoiced'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'


class HospitalAppointmentEvaluation(models.Model):
    _name = 'hospital.appointment.evaluation'
    _description = 'Hospital Appointment Evaluation'
    
    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    evaluation_type = fields.Char(string='Evaluation Type')
    results = fields.Text(string='Results')
    evaluator_id = fields.Many2one('res.users', string='Evaluator', default=lambda self: self.env.user)
    notes = fields.Text(string='Notes')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

class HospitalAppointmentType(models.Model):
    _name = 'hospital.appointment.type'
    _description = 'Hospital Appointment Type'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    duration = fields.Float(string='Default Duration (Hours)', default=1.0)
    color = fields.Integer(string='Color Index')
    active = fields.Boolean(string='Active', default=True)