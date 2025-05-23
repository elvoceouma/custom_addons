from odoo import models, fields, api, _

class CarePlan(models.Model):
    _name = 'hospital.care.plan'
    _description = 'Care Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    name_seq = fields.Char(string='Care Plan Number', readonly=True)
    ip_number = fields.Char(string='IP Number')
    patient_name = fields.Char(string='Patient Name')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    age = fields.Integer(string='Age')
    mrn_no = fields.Char(string='MRN No')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    care_plan = fields.Text(string='Care Plan')
    diet_type = fields.Selection([
        ('regular', 'Regular'),
        ('soft', 'Soft'),
        ('liquid', 'Liquid'),
        ('diabetic', 'Diabetic'),
        ('other', 'Other')
    ], string='Diet Type')
    diet_consultation = fields.Boolean(string='Diet Consultation')
    diet_note = fields.Text(string='Diet Note')
    diet_screening = fields.Boolean(string='Diet Screening')
    labtest_ids = fields.Many2many('hospital.lab.test', string='Lab Tests')
    physio_required = fields.Boolean(string='Physio Required')
    physio_note = fields.Text(string='Physio Note')
    restraint_required = fields.Boolean(string='Restraint Required')
    restraint_note = fields.Text(string='Restraint Note')
    procedures_theraphy = fields.Text(string='Procedures / Therapies planned and special order')
    additional_notes = fields.Text(string='Additional Notes')
    
    # One2many fields
    miscellaneous_line_ids = fields.One2many(
        'hospital.care.plan.miscellaneous', 
        'care_plan_id', 
        string='Miscellaneous'
    )
    cross_consultationline_ids = fields.One2many(
        'hospital.care.plan.consultation', 
        'care_plan_id', 
        string='Cross Consultations'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.care.plan') or _('New')
            if not vals.get('name_seq'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.care.plan.seq') or _('New')
        return super(CarePlan, self).create(vals_list)
    
    def action_confirm(self):
        self.write({'state': 'confirmed'})
    
    def action_in_progress(self):
        self.write({'state': 'in_progress'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        self.write({'state': 'cancelled'})
 
    def action_inprogress(self):
        self.write({'state': 'in_progress'})

class CarePlanMiscellaneous(models.Model):
    _name = 'hospital.care.plan.miscellaneous'
    _description = 'Care Plan Miscellaneous Items'
    
    care_plan_id = fields.Many2one('hospital.care.plan', string='Care Plan')
    miscellaneous_id = fields.Many2one('hospital.miscellaneous', string='Miscellaneous')
    miscellaneous_note = fields.Text(string='Note')

class CarePlanConsultation(models.Model):
    _name = 'hospital.care.plan.consultation'
    _description = 'Care Plan Cross Consultation'
    
    care_plan_id = fields.Many2one('hospital.care.plan', string='Care Plan')
    consulation_doctor = fields.Many2one('hospital.doctor', string='Consultation Doctor')
    consultation_department = fields.Many2one('hospital.department', string='Consultation Department')