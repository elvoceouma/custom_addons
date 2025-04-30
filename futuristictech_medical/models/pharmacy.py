from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalMedication(models.Model):
    _name = 'medical.medication'
    _description = 'Medication'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Medication Name', required=True, tracking=True)
    code = fields.Char(string='Code', required=True, tracking=True)
    product_id = fields.Many2one(
        'product.product', string='Related Product', required=True,
        domain=[('type', '=', 'product')])
    active_ingredient = fields.Char(string='Active Ingredient')
    dosage_form = fields.Selection([
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('liquid', 'Liquid'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('other', 'Other')], string='Dosage Form')
    strength = fields.Char(string='Strength')
    manufacturer = fields.Char(string='Manufacturer')
    stock_quantity = fields.Float(
        string='Stock Quantity', compute='_compute_stock_quantity', store=True)
    reorder_level = fields.Float(string='Reorder Level')
    note = fields.Text(string='Notes')
    appointment_id = fields.Many2one(
        'medical.appointment', string='Appointment') 
    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code)',
         'Medication code must be unique!'),
    ]

    @api.depends('product_id')
    def _compute_stock_quantity(self):
        for medication in self:
            if medication.product_id:
                medication.stock_quantity = medication.product_id.qty_available
            else:
                medication.stock_quantity = 0.0

    def action_view_stock(self):
        self.ensure_one()
        action = self.env.ref('stock.product_open_quants').read()[0]
        action['domain'] = [('product_id', '=', self.product_id.id)]
        return action

class MedicalPrescription(models.Model):
    _name = 'medical.prescription'
    _description = 'Medical Prescription'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Prescription Reference', required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'medical.patient', string='Patient', required=True, tracking=True)
    doctor_id = fields.Many2one(
        'medical.doctor', string='Doctor', required=True, tracking=True)
    case_id = fields.Many2one(
        'medical.case', string='Medical Case')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    medication_lines = fields.One2many(
        'medical.prescription.line', 'prescription_id', string='Medications')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('dispensed', 'Dispensed'),
        ('cancelled', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    notes = fields.Text(string='Notes')
    pharmacy_notes = fields.Text(string='Pharmacy Notes')
    consultation_id = fields.Many2one('medical.consultation', string='Consultation')
    appointment_id = fields.Many2one(
        'medical.appointment', string='Appointment') 
    patient_history = fields.Text(string='Patient History')
    __count = fields.Integer(string='Count', compute='_compute_count')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.prescription') or _('New')
        return super(MedicalPrescription, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_dispense(self):
        self.write({'state': 'dispensed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_case(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_case_form').read()[0]
        action['res_id'] = self.case_id.id
        action['views'] = [(self.env.ref('futuristictech_medical.view_medical_case_form').id, 'form')]
        return action
    
    def action_view_medication(self):
        self.ensure_one()
        action = self.env.ref('futuristictech_medical.action_medical_medication_form').read()[0]
        action['res_id'] = self.medication_lines[0].medication_id.id
        action['views'] = [(self.env.ref('futuristictech_medical.view_medical_medication_form').id, 'form')]
        return action
    
    def action_print_prescription(self):
        self.ensure_one()
        return self.env.ref('futuristictech_medical.action_report_medical_prescription').report_action(self)
    def action_send_prescription(self):
        self.ensure_one()
        template_id = self.env.ref('futuristictech_medical.email_template_medical_prescription').id
        template = self.env['mail.template'].browse(template_id)
        if not template:
            raise ValidationError(_('Email template not found.'))
        template.send_mail(self.id, force_send=True)
        return True
    
    def _compute_count(self):
        for record in self:
            record.__count = len(record.medication_lines)
    

class MedicalPrescriptionLine(models.Model):
    _name = 'medical.prescription.line'
    _description = 'Prescription Line'

    prescription_id = fields.Many2one(
        'medical.prescription', string='Prescription', ondelete='cascade')
    medication_id = fields.Many2one(
        'medical.medication', string='Medication', required=True)
    dosage = fields.Char(string='Dosage', required=True)
    frequency = fields.Char(string='Frequency', required=True)
    duration = fields.Char(string='Duration', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    notes = fields.Text(string='Notes')
    morning = fields.Boolean(string='Morning')
    afternoon = fields.Boolean(string='Afternoon')
    evening = fields.Boolean(string='Evening')
    night = fields.Boolean(string='Night')
    is_dispensed = fields.Boolean(string='Is Dispensed', default=False)
    take_with_food = fields.Boolean(string='Take with Food')
    special_instructions = fields.Text(string='Special Instructions')