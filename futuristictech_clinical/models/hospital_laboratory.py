#  -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LabTestType(models.Model):
    _name = 'hospital.lab.test.type'
    _description = 'Lab Test Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    category = fields.Selection([
        ('hematology', 'Hematology'),
        ('biochemistry', 'Biochemistry'),
        ('microbiology', 'Microbiology'),
        ('immunology', 'Immunology'),
        ('urine', 'Urine Analysis'),
        ('molecular', 'Molecular Biology'),
        ('other', 'Other')
    ], string='Category', default='other')



    def save(self):
        # Save the document and return to the list view
        self.ensure_one()
        if not self.file:
            raise ValidationError(_('Please upload a file.'))
        if not self.file_name:
            raise ValidationError(_('Please provide a file name.'))
        self.write({'file_name': self.file_name})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
    
# Individual Test Type Models
class HematologyTest(models.Model):
    _name = 'hematology.test'
    _description = 'Hematology Test'
    _inherit = 'hospital.lab.test.type'

class BiochemistryTest(models.Model):
    _name = 'biochemistry.test'
    _description = 'Biochemistry Test'
    _inherit = 'hospital.lab.test.type'

class HormonesTest(models.Model):
    _name = 'hormones.test'
    _description = 'Hormones Test'
    _inherit = 'hospital.lab.test.type'

class MicrobiologyTest(models.Model):
    _name = 'microbiology.test'
    _description = 'Microbiology Test'
    _inherit = 'hospital.lab.test.type'

class ImmunologyTest(models.Model):
    _name = 'immunology.test'
    _description = 'Immunology Test'
    _inherit = 'hospital.lab.test.type'

class UrineChemistryTest(models.Model):
    _name = 'urine.chemistry.test'
    _description = 'Urine Chemistry Test'
    _inherit = 'hospital.lab.test.type'

class UrineScreeningTest(models.Model):
    _name = 'urine.screening.test'
    _description = 'Urine Screening Test'
    _inherit = 'hospital.lab.test.type'

class DrugAssaysTest(models.Model):
    _name = 'drug.assays.test'
    _description = 'Drug Assays Test'
    _inherit = 'hospital.lab.test.type'

class MolecularBiologyTest(models.Model):
    _name = 'molecular.biology.test'
    _description = 'Molecular Biology Test'
    _inherit = 'hospital.lab.test.type'

class MiscelleneousTest(models.Model):
    _name = 'miscelleneous.test'
    _description = 'Miscelleneous Test'
    _inherit = 'hospital.lab.test.type'

class ProfileTest(models.Model):
    _name = 'profile.test'
    _description = 'Profile Test'
    _inherit = 'hospital.lab.test.type'

class HospitalLab(models.Model):
    _name = 'hospital.lab'
    _description = 'Hospital Lab'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True, tracking=True)
    lab_test_type_ids = fields.Many2many('hospital.lab.test.type', string='Lab Test Types')
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)

class HospitalLabTestRequisition(models.Model):
    _name = 'hospital.lab.test.requisition'
    _description = 'Laboratory Test Requisition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Requisition Reference', required=True, copy=False, readonly=True, default='New')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('sample_received', 'Sample Received'),
        ('sent_for_testing', 'Sent for Testing'),
        ('report_generated', 'Report Generated'),
        ('sample_rejected', 'Sample Rejected')
    ], string='Status', default='draft', tracking=True)
    
    type = fields.Selection([
        ('inpatient', 'Inpatient'),
        ('outpatient', 'Outpatient'),
        ('external', 'External')
    ], string='Type', default='inpatient')
    
    reference = fields.Char(string='Reference')
    ip_no = fields.Char(string='IP Number')
    patient_name = fields.Char(string='Patient Name')
    age = fields.Char(string='Age')
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Sex')
    
    partner_id = fields.Many2one('res.partner', string='Partner')
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Inpatient Admission')
    op_visit_id = fields.Many2one('op.visit', string='Outpatient Visit')
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    prescribing_doctor = fields.Many2one('hospital.physician', string='Prescribing Doctor',
                                       domain="[('team_role','in',('psychiatrist','physician'))]")
    purpose = fields.Text(string='Purpose')
    
    requested_date = fields.Datetime(string='Requested Date')
    required_date = fields.Datetime(string='Required Date')
    approved_date = fields.Datetime(string='Approved Date')
    mrn_no = fields.Char(string='MRN Number')
    treating_doctor = fields.Many2one('hospital.physician', string='Treating Doctor')
    lab_id = fields.Many2one('hospital.lab', string='Lab', required=True, 
                            domain="[('active','=',True)]")
    company_id = fields.Many2one('res.company', string='Company', 
                               default=lambda self: self.env.company)
    
    requisition_line_ids = fields.One2many('hospital.lab.test.requisition.line', 
                                         'requisition_id', string='Requisition Lines')
    
    user_id = fields.Many2one('res.users', string='Created By', 
                            default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    labtest_count = fields.Integer(string='Lab Tests Count', compute='_compute_labtest_count')

    def _compute_labtest_count(self):
        # Implement logic to compute lab test count
        pass

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now()
        })

    def action_sample_received(self):
        self.write({'state': 'sample_received'})

    def action_sent_for_testing(self):
        self.write({'state': 'sent_for_testing'})

    def action_sample_rejected(self):
        self.write({'state': 'sample_rejected'})

    def action_report_generated(self):
        self.write({'state': 'report_generated'})

    def view_labtest(self):
        # Implement action to view lab tests
        pass

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hospital.lab.test.requisition') or 'New'
        return super(HospitalLabTestRequisition, self).create(vals)


class HospitalLabTestRequisitionLine(models.Model):
    _name = 'hospital.lab.test.requisition.line'
    _description = 'Laboratory Test Requisition Line'

    requisition_id = fields.Many2one('hospital.lab.test.requisition', string='Requisition')
    date = fields.Date(string='Date')
    labtest_type_id = fields.Many2one('hospital.lab.test.type', string='Lab Test Type')
    product_id = fields.Many2one('product.product', string='Product',
                               domain="['|',('type','=','service'),('debit_note','=',True)]")
    name = fields.Char(string='Description')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    price_subtotal = fields.Float(string='Subtotal', readonly=True)
    tested = fields.Boolean(string='Tested')



from odoo import models, fields, api

class OeHealthMedicalLabTest(models.Model):
    _name = 'oeh.medical.lab.test'
    _description = 'Medical Lab Test'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Test ID', required=True, copy=False, readonly=True, default='New')
    test_type = fields.Many2one('hospital.lab.test.type', string='Test Type', required=True)
    patient = fields.Many2one('hospital.patient', string='Patient', required=True, 
                            options="{'no_create': True}")
    date_requested = fields.Datetime(string='Date Requested', default=fields.Datetime.now)
    requestor = fields.Many2one('res.partner', string='Requested By', 
                              options="{'no_create': True}")
    pathologist = fields.Many2one('res.partner', string='Pathologist', 
                                options="{'no_create': True}")
    date_analysis = fields.Datetime(string='Date of Analysis')
    
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Test In Progress', 'Test In Progress'),
        ('Completed', 'Completed'),
        ('Invoiced', 'Invoiced')
    ], string='State', default='Draft', tracking=True)
    
    lab_test_criteria = fields.One2many('oeh.medical.lab.test.criteria', 'test_id', 
                                      string='Test Cases')
    results = fields.Text(string='Test Results')
    diagnosis = fields.Text(string='Diagnosis')
    
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('oeh.medical.lab.test') or 'New'
        return super(OeHealthMedicalLabTest, self).create(vals)
    
    def set_to_test_inprogress(self):
        self.write({'state': 'Test In Progress'})
    
    def set_to_test_complete(self):
        self.write({'state': 'Completed'})
    
    def action_lab_invoice_create(self):
        # Implement invoice creation logic here
        self.write({'state': 'Invoiced'})
        return True
    
    def print_patient_labtest(self):
        # Implement print lab test logic here
        return self.env.ref('oehealth_medical.action_report_labtest').report_action(self)


class OeHealthMedicalLabTestCriteria(models.Model):
    _name = 'oeh.medical.lab.test.criteria'
    _description = 'Lab Test Criteria'
    _order = 'sequence'

    test_id = fields.Many2one('oeh.medical.lab.test', string='Lab Test')
    sequence = fields.Integer(string='Sequence', required=True, default=1)
    name = fields.Char(string='Test Name', required=True)
    result = fields.Char(string='Result')
    normal_range = fields.Char(string='Normal Range')
    units = fields.Char(string='Units')