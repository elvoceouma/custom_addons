from odoo import models, fields, api, _
from datetime import datetime


class DrugChart(models.Model):
    _name = 'hospital.drug.chart'
    _description = 'Drug Chart'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'), tracking=True)
    name_seq = fields.Char(string='Drug Chart Number', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Patient Information
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    admission_id = fields.Many2one('hospital.admission', string='Admission')
    ip_number = fields.Char(string='IP Number', store=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    age = fields.Integer(string='Age', store=True)
    mrn_no = fields.Char(string='MRN No', store=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', store=True)
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string="Gender")
    # drug_allergies = fields.Text(string='Drug Hypersensitivity/Allergies')
    drug_allergies = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Drug Allergies', default='no')
    # Medical Information
    date = fields.Date(string='Date', default=fields.Date.context_today, tracking=True)
    start_date = fields.Date(string='Start', default=fields.Date.context_today)
    end_date = fields.Date(string='End')
    doctor = fields.Many2one('res.partner', string='Doctor', store=True, tracking=True)
    ward = fields.Many2one('hospital.block', string='Ward', store=True)
    room = fields.Char(string='Room')
    diet = fields.Selection([
        ('veg_diet', 'Vegetable Diet'),
        ('non_veg_diet', 'Non-Vegetable Diet'),
        ('mixed_diet', 'Mixed Diet'),
    ], string='Diet', default='veg_diet', store=True)
    blood_group = fields.Selection([
        ('a_positive', 'A+'),
        ('a_negative', 'A-'),
        ('b_positive', 'B+'),
        ('b_negative', 'B-'),
        ('ab_positive', 'AB+'),
        ('ab_negative', 'AB-'),
        ('o_positive', 'O+'),
        ('o_negative', 'O-')
    ], string='Blood Group', store=True)
    type = fields.Selection([
        ('inpatient', 'Inpatient'),
        ('outpatient', 'Outpatient'),
    ], string='Type', default='inpatient', store=True)
    # Prescription Lines
    prescription_line_ids = fields.One2many('hospital.drug.chart.prescription', 'drug_chart_id', string='Prescription Lines')
    regular_prescription_line_ids = fields.One2many('hospital.drug.chart.regular', 'drug_chart_id', string='Regular Prescription Lines')
    only_once_drug_chart_line_ids = fields.One2many('hospital.drug.chart.once', 'drug_chart_id', string='Only Once Drug Lines')
    variable_drug_chart_line_ids = fields.One2many('hospital.drug.chart.variable', 'drug_chart_id', string='Variable Drug Lines')
    
    # Legacy field for compatibility
    line_ids = fields.One2many('hospital.drug.chart.line', 'drug_chart_id', string='Drug Lines')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.drug.chart') or _('New')
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('hospital.drug.chart.seq') or _('New')
        return super(DrugChart, self).create(vals_list)

    def action_confirm(self):
        """Confirm the drug chart"""
        self.write({'state': 'confirmed'})
        return True

    def action_inprogress(self):
        """Set drug chart to in progress"""
        self.write({'state': 'in_progress'})
        return True

    def action_cancel(self):
        """Cancel the drug chart"""
        self.write({'state': 'cancelled'})
        return True

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.patient_name = self.patient_id.name
            self.age = self.patient_id.age
            self.mrn_no = self.patient_id.mrn_no
            self.patient_gender = self.patient_id.gender
            self.blood_group = self.patient_id.blood_group


class DrugChartPrescription(models.Model):
    _name = 'hospital.drug.chart.prescription'
    _description = 'Drug Chart Prescription Line'

    drug_chart_id = fields.Many2one('hospital.drug.chart', string='Drug Chart', ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    drug_name = fields.Many2one('product.product', string='Drug Name', domain=[('medicine_product', '=', True)])
    route = fields.Char(string='Route')
    frequency = fields.Many2one('hospital.medicine.frequency', string='Frequency')
    prescription_type = fields.Selection([
        ('regular', 'Regular'),
        ('prn', 'PRN'),
        ('stat', 'STAT'),
        ('sos', 'SOS')
    ], string='Prescription Type', default='regular')
    take = fields.Char(string='Take')
    start_presc = fields.Date(string='Start Date')
    end_presc = fields.Date(string='End Date')
    approved_doctor = fields.Many2one('res.partner', string='Approved Doctor')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('InProgress', 'In Progress'),
        ('completed', 'Completed'),
        ('stopped', 'Stopped')
    ], string='Status', default='draft')
    action_taken = fields.Char(string='Action Taken')
    action_taken_time = fields.Datetime(string='Action Taken Time')

    def update_prescription_drug(self):
        """Update prescription drug status"""
        return True

    def action_stop(self):
        """Stop the prescription"""
        self.write({'status': 'stopped'})
        return True


class DrugChartRegular(models.Model):
    _name = 'hospital.drug.chart.regular'
    _description = 'Regular Prescription Line'

    drug_chart_id = fields.Many2one('hospital.drug.chart', string='Drug Chart', ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    drug_name = fields.Many2one('product.product', string='Drug Name')
    mor = fields.Boolean(string='Morning')
    morning_time = fields.Float(string='Morning Time')
    mor_given_by = fields.Many2one('res.partner', string='Morning Given By')
    aft = fields.Boolean(string='Afternoon')
    afternoon_time = fields.Float(string='Afternoon Time')
    an_given_by = fields.Many2one('res.partner', string='Afternoon Given By')
    nit = fields.Boolean(string='Night')
    night_time = fields.Float(string='Night Time')
    nit_given_by = fields.Many2one('res.partner', string='Night Given By')


class DrugChartOnce(models.Model):
    _name = 'hospital.drug.chart.once'
    _description = 'Only Once Drug Chart Line'

    drug_chart_id = fields.Many2one('hospital.drug.chart', string='Drug Chart', ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    drug_name = fields.Many2one('product.product', string='Drug Name', domain=[('medicine_product', '=', True)])
    route = fields.Char(string='Route')
    approved_doctor = fields.Many2one('res.partner', string='Approved Doctor')
    given_time = fields.Float(string='Given Time')
    given_time_am_pm = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM')
    ], string='AM/PM', required=True)
    given_by = fields.Many2one('res.partner', string='Given By')
    checked_time = fields.Float(string='Checked Time')
    check_time_am_pm = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM')
    ], string='Check AM/PM', required=True)
    checked_by = fields.Many2one('res.partner', string='Checked By')


class DrugChartVariable(models.Model):
    _name = 'hospital.drug.chart.variable'
    _description = 'Variable Drug Chart Line'

    drug_chart_id = fields.Many2one('hospital.drug.chart', string='Drug Chart', ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    drug_name = fields.Many2one('product.product', string='Drug Name', domain=[('medicine_product', '=', True)])
    route = fields.Char(string='Route')
    approved_doctor = fields.Many2one('res.partner', string='Approved Doctor')
    given_time = fields.Float(string='Given Time')
    given_time_am_pm = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM')
    ], string='AM/PM', required=True)
    given_by = fields.Many2one('res.partner', string='Given By')
    checked_time = fields.Float(string='Checked Time')
    check_time_am_pm = fields.Selection([
        ('am', 'AM'),
        ('pm', 'PM')
    ], string='Check AM/PM', required=True)
    checked_by = fields.Many2one('res.partner', string='Checked By')


# Legacy model for compatibility
class DrugChartLine(models.Model):
    _name = 'hospital.drug.chart.line'
    _description = 'Drug Chart Line'

    drug_chart_id = fields.Many2one('hospital.drug.chart', string='Drug Chart', ondelete='cascade')
    medicine_id = fields.Many2one('product.product', string='Medicine')
    dosage = fields.Char(string='Dosage')
    frequency_id = fields.Many2one('hospital.medicine.frequency', string='Frequency')
    route_id = fields.Many2one('hospital.medicine.route', string='Route')
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    morning = fields.Boolean(string='Morning')
    noon = fields.Boolean(string='Noon')
    evening = fields.Boolean(string='Evening')
    night = fields.Boolean(string='Night')

class HospitalMedicineFrequency(models.Model):
    _name = 'hospital.medicine.frequency'
    _description = 'Hospital Medicine Frequency'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')


class HospitalMedicineRoute(models.Model):
    _name = 'hospital.medicine.route'
    _description = 'Hospital Medicine Route'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Description')