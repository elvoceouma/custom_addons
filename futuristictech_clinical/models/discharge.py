# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class DischargeRecord(models.Model):
    _name = 'hospital.discharge'
    _description = 'Patient Discharge'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Inpatient Admission', required=True, tracking=True)
    discharge_date = fields.Datetime(string='Discharge Date', default=fields.Datetime.now, tracking=True)
    
    # Fields from the form view
    requested_by = fields.Many2one('res.users', string='Requested By', tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By', tracking=True)
    approved_date = fields.Datetime(string='Approved Date', tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    prescription_id = fields.Many2one('hospital.prescription', string='Prescription', tracking=True)
    
    # Clearance related fields
    counsellor = fields.Many2one('res.users', string='Counsellor', tracking=True)
    nurse = fields.Many2one('res.users', string='Nurse', tracking=True)
    store_incharge = fields.Many2one('res.users', string='Store Incharge', tracking=True)
    
    # Additional fields
    description = fields.Text(string='Description', tracking=True)
    
    # State field for status tracking
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approve', 'Approved'),
        ('close', 'Closed'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge') or _('New')
        return super(DischargeRecord, self).create(vals_list)

    def action_confirm(self):
        for record in self:
            record.state = 'waiting_for_approval'
    
    def action_approve(self):
        for record in self:
            record.state = 'approve'
            record.approved_by = self.env.user.id
            record.approved_date = fields.Datetime.now()
    
    def action_close(self):
        for record in self:
            record.state = 'close'
            if record.inpatient_admission_id:
                record.inpatient_admission_id.state = 'Discharged'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_medicine_packing(self):
            self.ensure_one()
            return {
                'name': _('Medicine Packing'),
                'type': 'ir.actions.act_window',
                'res_model': 'hospital.medicine.packing',
                'view_mode': 'tree,form',
                'domain': [('discharge_id', '=', self.id)],
                'context': {
                    'default_discharge_id': self.id,
                    'default_patient_id': self.patient_id.id,
                    'default_inpatient_admission_id': self.inpatient_admission_id.id,
                },
                'target': 'current',
            }
        
    def action_requisition_clearance(self):
        self.ensure_one()
        return {
            'name': _('Requisition Clearance'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.requisition.clearance',
            'view_mode': 'tree,form',
            'domain': [('discharge_id', '=', self.id)],
            'context': {
                'default_discharge_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
            },
            'target': 'current',
        }
    
    def action_store_clearance(self):
        self.ensure_one()
        return {
            'name': _('Store Clearance'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.store.clearance',
            'view_mode': 'tree,form',
            'domain': [('discharge_id', '=', self.id)],
            'context': {
                'default_discharge_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
            },
            'target': 'current',
        }
    
    def action_discharge_summary(self):
        self.ensure_one()
        return {
            'name': _('Discharge Summary'),
            'type': 'ir.actions.act_window',
            'res_model': 'hospital.discharge.summary',
            'view_mode': 'tree,form',
            'domain': [('inpatient_admission_id', '=', self.inpatient_admission_id.id)],
            'context': {
                'default_inpatient_admission_id': self.inpatient_admission_id.id,
                'default_patient_id': self.patient_id.id,
                'default_campus': self.campus,
                'default_discharge_id': self.id,
            },
            'target': 'current',
        }


class DischargeSummary(models.Model):
    _name = 'hospital.discharge.summary'
    _description = 'Discharge Summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Admission', required=True, tracking=True)
    discharge_id = fields.Many2one('hospital.discharge', string='Discharge Record', tracking=True)
    discharge_date = fields.Date(string='Discharge Date', tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    
    # Requisition lines
    pa_requisition_lines = fields.One2many('hospital.patient.requisition.line', 'discharge_summary_id', 
                                        string='Patient Requisition Lines')
    sr_requisition_lines = fields.One2many('hospital.service.requisition.line', 'discharge_summary_id', 
                                        string='Service Requisition Lines')
    ct_requisition_lines = fields.One2many('hospital.caretaker.requisition.line', 'discharge_summary_id', 
                                        string='Caretaker Requisition Lines')
    sp_requisition_lines = fields.One2many('hospital.special.privilege.line', 'discharge_summary_id', 
                                        string='Special Privilege Lines')
    
    # Other details
    processed_by = fields.Many2one('res.users', string='Processed By', tracking=True)
    processed_date = fields.Date(string='Processed Date', tracking=True)
    
    # Approvals related fields
    clinical_psychologist = fields.Many2one('res.users', string='Clinical Psychologist', tracking=True)
    psychiatrist = fields.Many2one('res.users', string='Psychiatrist', tracking=True)
    registrar = fields.Many2one('res.users', string='Registrar', tracking=True)
    clinical_psychologist_bool = fields.Boolean(string='Clinical Psychologist Approved', tracking=True)
    psychiatrist_bool = fields.Boolean(string='Psychiatrist Approved', tracking=True)
    registrar_bool = fields.Boolean(string='Registrar Approved', tracking=True)
    description = fields.Text(string='Description', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('close', 'Close'),
        ('approve', 'Approved')
    ], string='Status', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.discharge.summary') or _('New')
        return super(DischargeSummary, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'inprogress'
    
    def action_close(self):
        for record in self:
            record.state = 'close'
    
    def action_approve_clinical_psychologist(self):
        for record in self:
            record.clinical_psychologist_bool = True
            record.clinical_psychologist = self.env.user.id
            self._check_all_approvals()
    
    def action_approve_psychiatrist(self):
        for record in self:
            record.psychiatrist_bool = True
            record.psychiatrist = self.env.user.id
            self._check_all_approvals()
    
    def action_approve_registrar(self):
        for record in self:
            record.registrar_bool = True
            record.registrar = self.env.user.id
            self._check_all_approvals()
    
    def _check_all_approvals(self):
        for record in self:
            if record.clinical_psychologist_bool and record.psychiatrist_bool and record.registrar_bool:
                record.state = 'approve'



class HospitalRequisitionClearance(models.Model):
    _name = 'hospital.requisition.clearance'
    _description = 'Requisition Clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Inpatient Admission', 
                                            domain="[('state', '!=', 'Discharged')]", tracking=True)
    discharge_id = fields.Many2one('hospital.discharge', string='Discharge', tracking=True)
    discharge_date = fields.Datetime(related='discharge_id.discharge_date', string='Discharge Date', tracking=True)
    
    
    # Other fields
    processed_by = fields.Many2one('res.users', string='Processed By', tracking=True)
    processed_date = fields.Datetime(string='Processed Date', tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    requisition_id = fields.Many2one('hospital.patient.requisition', string='Requisition')
    product_id = fields.Many2one('product.product', string='Product', 
                                domain="[('debit_note','=',True),('type','!=','service')]", required=True)
    date = fields.Date(string='Date')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    is_issued = fields.Boolean(string='Is Issued', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('close', 'Closed')
    ], string='Status', default='draft', tracking=True)

    pa_requisition_lines = fields.One2many('hospital.patient.requisition.line', 'id', 
                                         string='Patient Requisition Lines')
    
    sr_requisition_lines = fields.One2many('hospital.service.requisition.line', 'id',
                                         string='Service Requisition Lines')
    ct_requisition_lines = fields.One2many('hospital.caretaker.requisition.line', 'id',
                                         string='Caretaker Requisition Lines')
    
    sp_requisition_lines = fields.One2many('hospital.special.privilege.line', 'id', 
                                         string='Special Privilege Lines')
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.requisition.clearance') or _('New')
        return super(HospitalRequisitionClearance, self).create(vals_list)
    
    def action_confirm(self):
        for record in self:
            record.state = 'inprogress'
    
    def action_close(self):
        for record in self:
            record.state = 'close'
            record.processed_by = self.env.user.id
            record.processed_date = fields.Datetime.now()

class PatientRequisitionLine(models.Model):
    _name = 'hospital.patient.requisition.line'
    _description = 'Patient Requisition Line'
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    discharge_summary_id = fields.Many2one('hospital.discharge.summary', string='Discharge Summary')
    requisition_clearance_id = fields.Many2one('hospital.requisition.clearance', string='Requisition Clearance')
    product_id = fields.Many2one('product.product', string='Product', 
                                domain="[('debit_note','=',True),('type','!=','service')]")
    pr_id = fields.Many2one('hospital.patient.requisition', string='Patient Requisition')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', default='draft')
    requisition_id = fields.Many2one('hospital.patient.requisition', string='Requisition')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    is_issued = fields.Boolean(string='Is Issued', default=False)
    
    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.internal_category_id = self.product_id.categ_id
            self.price_unit = self.product_id.list_price
            
    def action_cancel(self):
        for record in self:
            record.state = 'rejected'


class ServiceRequisitionLine(models.Model):
    _name = 'hospital.service.requisition.line'
    _description = 'Service Requisition Line'
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    discharge_summary_id = fields.Many2one('hospital.discharge.summary', string='Discharge Summary')
    requisition_clearance_id = fields.Many2one('hospital.requisition.clearance', string='Requisition Clearance')
    sr_id = fields.Many2one('hospital.service.requisition', string='Service Requisition')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', default='draft')
    requisition_id = fields.Many2one('hospital.service.requisition', string='Requisition')
    
    def action_cancel(self):
        for record in self:
            record.state = 'rejected'


class HospitalCaretakerRequisition(models.Model):
    _name = 'hospital.caretaker.requisition'
    _description = 'Hospital Caretaker Requisition'

    name = fields.Char(string='Reference', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    patient_id = fields.Many2one('hospital.patient', string='Patient')
    caretaker_id = fields.Many2one('res.partner', string='Caretaker')
    line_ids = fields.One2many('hospital.caretaker.requisition.line', 'cr_id', string='Lines')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft')

class CaretakerRequisitionLine(models.Model):
    _name = 'hospital.caretaker.requisition.line'
    _description = 'Caretaker Requisition Line'
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    discharge_summary_id = fields.Many2one('hospital.discharge.summary', string='Discharge Summary')
    requisition_clearance_id = fields.Many2one('hospital.requisition.clearance', string='Requisition Clearance')
    cr_id = fields.Many2one('hospital.caretaker.requisition', string='Caretaker Requisition')
    type = fields.Char(string='Type')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'


class SpecialPrivilegeLine(models.Model):
    _name = 'hospital.special.privilege.line'
    _description = 'Special Privilege Line'
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    discharge_summary_id = fields.Many2one('hospital.discharge.summary', string='Discharge Summary')
    requisition_clearance_id = fields.Many2one('hospital.requisition.clearance', string='Requisition Clearance')
    ref = fields.Char(string='Reference')
    sp_id = fields.Many2one('hospital.special.privilege', string='Special Privilege')
    privilege_type = fields.Char(string='Privilege Type')
    date = fields.Date(string='Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft')
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'



class HospitalStoreClearanceProductList(models.Model):
    _name = 'hospital.store.clearance.product.list'
    _description = 'Store Clearance Product List'
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    store_clearance_id = fields.Many2one('hospital.store.clearance', string='Store Clearance')
    product_id = fields.Many2one('product.product', string='Product')
    qty = fields.Float(string='Quantity')



class HospitalStoreClearance(models.Model):
    _name = 'hospital.store.clearance'
    _description = 'Store Clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Inpatient Admission', tracking=True)
    discharge_id = fields.Many2one('hospital.discharge', string='Discharge', tracking=True)
    discharge_date = fields.Datetime(related='discharge_id.discharge_date', string='Discharge Date', tracking=True)
    
    # # Stock picking related fields
    stock_picking_count = fields.Integer(string='Stock Picking Count', compute='_compute_stock_picking_count')
    picking_type = fields.Many2one('stock.picking.type', string='Picking Type', tracking=True)
    source_location = fields.Many2one('stock.location', string='Source Location', tracking=True)
    destination_location = fields.Many2one('stock.location', string='Destination Location', tracking=True)
    
    # # Product lines
    product_list = fields.One2many('hospital.store.clearance.product.list', 'store_clearance_id', 
                                  string='Product List')
    product_lines = fields.One2many('hospital.store.clearance.product.line', 'store_clearance_id', 
                                   string='Product Lines')
    
    # # Other fields
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    items_returned = fields.Boolean(string='All Items Returned', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('close', 'Closed')
    ], string='Status', default='draft', tracking=True)

    discharge_summary_id = fields.Many2one('hospital.discharge.summary', string='Discharge Summary')
    ref = fields.Char(string='Reference')
    sp_id = fields.Many2one('hospital.special.privilege', string='Special Privilege')
    privilege_type = fields.Char(string='Privilege Type')
    date = fields.Date(string='Date')

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.store.clearance') or _('New')
        return super(HospitalStoreClearance, self).create(vals_list)
    
    def _compute_stock_picking_count(self):
        for record in self:
            record.stock_picking_count = self.env['stock.picking'].search_count([
                ('store_clearance_id', '=', record.id)
            ])
    
    def action_confirm(self):
        for record in self:
            record.state = 'inprogress'
    
    def action_close(self):
        for record in self:
            record.state = 'close'
    
    def view_stock_picking(self):
        self.ensure_one()
        return {
            'name': _('Stock Pickings'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('store_clearance_id', '=', self.id)],
            'context': {'default_store_clearance_id': self.id},
            'target': 'current',
        }

class HospitalStoreClearanceProductLine(models.Model):
    _name = 'hospital.store.clearance.product.line'
    _description = 'Store Clearance Product Line'
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    store_clearance_id = fields.Many2one('hospital.store.clearance', string='Store Clearance')
    product_id = fields.Many2one('product.product', string='Product', domain=[('returnable_product', '=', True)])
    qty = fields.Float(string='Quantity')


class HospitalCounsellorClearance(models.Model):
    _name = 'hospital.counsellor.clearance'
    _description = 'Counsellor Clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    counsellor_id = fields.Many2one('hospital.physician', string='Counsellor', tracking=True)
    clearance_date = fields.Date(string='Clearance Date', default=fields.Date.today, tracking=True)
    is_cleared = fields.Boolean(string='Is Cleared', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inprogress', 'In Progress'),
        ('close', 'Close')
    ], string='Status', default='draft', tracking=True)
    inpatient_admission_id = fields.Many2one('hospital.admission', string='Inpatient Admission', tracking=True)
    discharge_id = fields.Many2one('hospital.discharge', string='Discharge', tracking=True)
    discharge_date = fields.Datetime(related='discharge_id.discharge_date', string='Discharge Date', tracking=True)
    campus = fields.Char(string='Campus', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    processed_by = fields.Many2one('res.users', string='Processed By', tracking=True)
    processed_date = fields.Datetime(string='Processed Date', tracking=True)
    requisition_id = fields.Many2one('hospital.patient.requisition', string='Requisition')
    product_id = fields.Many2one('product.product', string='Product', 
                                domain="[('debit_note','=',True),('type','!=','service')]", required=True)
    date = fields.Date(string='Date')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    is_issued = fields.Boolean(string='Is Issued', default=False)
    pa_requisition_lines = fields.One2many('hospital.patient.requisition.line', 'id', 
                                         string='Patient Requisition Lines')
    sr_requisition_lines = fields.One2many('hospital.service.requisition.line', 'id',
                                         string='Service Requisition Lines')
    ct_requisition_lines = fields.One2many('hospital.caretaker.requisition.line', 'id',
                                         string='Caretaker Requisition Lines')
    sp_requisition_lines = fields.One2many('hospital.special.privilege.line', 'id',
                                         string='Special Privilege Lines')
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.counsellor.clearance') or _('New')
        return super(HospitalCounsellorClearance, self).create(vals_list)
    
    def action_close(self):
        for record in self:
            record.is_cleared = True
            record.state = 'close'

    def action_confirm(self):
        for record in self:
            record.state = 'inprogress'            