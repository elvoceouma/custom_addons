from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HospitalDoctorPayout(models.Model):
    _name = 'hospital.doctor.payout'
    _description = 'Doctor Payout'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', tracking=True, compute='compute_name', store=True)
    doctor_id = fields.Many2one('res.partner', string='Doctor', required=True, tracking=True)
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('paid', 'Paid')
    ], string='State', default='new', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    payout_line_ids = fields.One2many('hospital.doctor.payout.line', 'doctor_payout_id', string='Payout Lines')
    
    def create_vendor_bill(self):
        """Create vendor bill based on the payout lines"""
        if not self.payout_line_ids:
            raise UserError(_('Please add payout lines first.'))
        
        # Prepare invoice lines from payout lines
        invoice_lines = []
        for line in self.payout_line_ids:
            if not line.is_cancelled:  # Skip cancelled lines
                invoice_line_vals = {
                    'product_id': line.product_id.id if line.product_id else False,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit,
                    'name': line.name or (line.product_id.name if line.product_id else 'Doctor Payout'),
                }
                invoice_lines.append((0, 0, invoice_line_vals))
        
        if not invoice_lines:
            raise UserError(_('No valid payout lines found to create vendor bill.'))
        
        # Create vendor bill
        invoice_vals = {
            'partner_id': self.doctor_id.id,  # Fixed: removed .partner_id
            'move_type': 'in_invoice',  # Vendor bill type
            'invoice_date': fields.Date.today(),
            'ref': self.name,  # Reference to payout
            'invoice_line_ids': invoice_lines,
            'company_id': self.company_id.id,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        self.state = 'paid'
        
        return {
            'name': _('Vendor Bill Created'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }
        
    def view_vendor_bill(self):
        """View the created vendor bill"""
        if not self.invoice_id:
            raise UserError(_('No vendor bill found.'))
            
        return {
            'name': _('Vendor Bill'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'type': 'ir.actions.act_window',
        }
    
    @api.depends('doctor_id', 'start_date', 'end_date')
    def compute_name(self):
        for record in self:
            if record.doctor_id and record.start_date and record.end_date:
                record.name = _('Payout for Doctor %s, Start Date: %s, End Date: %s') % (
                    record.doctor_id.name, record.start_date, record.end_date)
            else:
                record.name = _('Doctor Payout')
    
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """Update the name field when doctor_id is changed"""
        if self.doctor_id:
            if self.start_date and self.end_date:
                self.name = _('Payout for Doctor: %s, Start Date: %s, End Date: %s') % (
                    self.doctor_id.name, self.start_date, self.end_date)
            else:
                self.name = _('Payout for Doctor: %s') % (self.doctor_id.name)
    
    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        """Update the name field when start_date or end_date is changed"""
        if self.doctor_id and self.start_date and self.end_date:
            self.name = _('Payout for Doctor: %s, Start Date: %s, End Date: %s') % (
                self.doctor_id.name, self.start_date, self.end_date)
    @api.depends('doctor_id', 'start_date', 'end_date')
    def compute_name(self):
        # Wrute teh  name to compute teh  name  be {Payout for Doctor} + {Doctor Name} + {Start Date} + {End Date}
        for record in self:
            record.name = _('Payout for Doctor %s, Start Date: %s, End Date: %s') % (
                record.doctor_id.name, record.start_date, record.end_date)
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """Update the name field when doctor_id is changed"""
        if self.doctor_id:
            self.name = _('Payout for Doctor: %s') % (self.doctor_id.name)
    @api.onchange('start_date', 'end_date')
    def _onchange_dates(self):
        """Update the name field when start_date or end_date is changed"""
        if self.start_date and self.end_date:
            self.name = _('Payout for Doctor: %s, Start Date: %s, End Date: %s') % (
                self.doctor_id.name, self.start_date, self.end_date)

    
        
    

class HospitalDoctorPayoutLine(models.Model):
    _name = 'hospital.doctor.payout.line'
    _description = 'Doctor Payout Line'
    
    doctor_payout_id = fields.Many2one('hospital.doctor.payout', string='Doctor Payout')
    partner_id = fields.Many2one('res.partner', string='Partner')
    date = fields.Date(string='Date', required=True)
    type = fields.Selection([('credit', 'Credit (IP)')], string='Type', default='credit')
    reference = fields.Char(string='IP/OP Reference')
    internal_reference = fields.Char(string='Internal Reference')
    patient_id = fields.Many2one('res.partner', string='Patient')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description')
    internal_category_id = fields.Many2one('product.category', string='Internal Category')
    quantity = fields.Float(string='Quantity', default=1.0, readonly=False)
    price_unit = fields.Float(string='Unit Price', related='product_id.lst_price', readonly=False)
    price_subtotal = fields.Float(string='Amount', compute='_compute_price_subtotal', store=True)
    is_cancelled = fields.Boolean(string='Is Cancelled', default=False)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit

class HospitalBillEstimation(models.Model):
    _name = 'hospital.bill.estimation'
    _description = 'Hospital Bill Estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, 
                      default='New', tracking=True)
    estimate_date = fields.Date(string='Estimate Date', default=fields.Date.today, tracking=True)
    estimate_no = fields.Char(string='Estimate No', tracking=True)
    
    # Patient information
    related_patient = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    patient_category = fields.Selection([
        ('inpatient', 'Inpatient'),
        ('outpatient', 'Outpatient'),
        ('emergency', 'Emergency')
    ], string='Patient Category', tracking=True)
    
    # Insurance information
    plan_name = fields.Char(string='Plan Name', tracking=True)
    plan_type = fields.Char(string='Plan Type', tracking=True)
    insurance_company = fields.Many2one('res.partner', string='Insurance Company', tracking=True)
    
    # Hospitalization details
    visit_type = fields.Selection([
        ('op', 'OP'),
        ('ip', 'IP'),
        ('emergency', 'Emergency')
    ], string='Visit Type', tracking=True)
    bed_type = fields.Selection([
        ('general', 'General'),
        ('private', 'Private'),
        ('semi_private', 'Semi-Private'),
        ('icu', 'ICU')
    ], string='Bed Type', tracking=True)
    rate_plan = fields.Selection([
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ], string='Rate Plan', tracking=True)
    
    # Lines and totals
    bill_estimation_line_id = fields.One2many('hospital.bill.estimation.line', 'bill_estimation_id', 
                                             string='Estimation Lines')
    amount_estimated = fields.Monetary(string='Estimated Total', compute='_compute_amount', store=True)
    amount_net = fields.Monetary(string='Net Amount', compute='_compute_amount', store=True)
    amount_discount = fields.Monetary(string='Discount', compute='_compute_amount', store=True)
    amount_sponser = fields.Monetary(string='Sponsor Amount', compute='_compute_amount', store=True)
    amount_patient_total = fields.Monetary(string='Patient Amount', compute='_compute_amount', store=True)
    
    # Notes
    note = fields.Text(string='Remarks')
    free_text = fields.Text(string='Free Text')
    
    # Administrative fields
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                 related='company_id.currency_id', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done')
    ], string='Status', default='draft', tracking=True)
    
    @api.depends('bill_estimation_line_id.estimated_total_amount', 
                'bill_estimation_line_id.amount',
                'bill_estimation_line_id.discount_amount',
                'bill_estimation_line_id.sponsor_amount', 
                'bill_estimation_line_id.patient_amount')
    def _compute_amount(self):
        for record in self:
            amount_estimated = sum(line.estimated_total_amount for line in record.bill_estimation_line_id)
            amount_net = sum(line.amount for line in record.bill_estimation_line_id)
            amount_discount = sum(line.discount_amount for line in record.bill_estimation_line_id)
            amount_sponser = sum(line.sponsor_amount for line in record.bill_estimation_line_id)
            amount_patient_total = sum(line.patient_amount for line in record.bill_estimation_line_id)
            
            record.amount_estimated = amount_estimated
            record.amount_net = amount_net
            record.amount_discount = amount_discount
            record.amount_sponser = amount_sponser
            record.amount_patient_total = amount_patient_total
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.bill.estimation') or 'New'
        return super(HospitalBillEstimation, self).create(vals_list)


class HospitalBillEstimationLine(models.Model):
    _name = 'hospital.bill.estimation.line'
    _description = 'Hospital Bill Estimation Line'
    
    bill_estimation_id = fields.Many2one('hospital.bill.estimation', string='Bill Estimation')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description', required=True)
    remarks = fields.Char(string='Remarks')
    quantity = fields.Float(string='Quantity', default=1.0)
    unit_price = fields.Float(string='Unit Price')
    estimated_total_amount = fields.Float(string='Estimated Total', compute='_compute_estimated_total', store=True)
    discount_amount = fields.Float(string='Discount')
    amount = fields.Float(string='Amount', compute='_compute_amount', store=True)
    sponsor_amount = fields.Float(string='Sponsor Amount')
    patient_amount = fields.Float(string='Patient Amount', compute='_compute_patient_amount', store=True)
    
    @api.depends('quantity', 'unit_price')
    def _compute_estimated_total(self):
        for line in self:
            line.estimated_total_amount = line.quantity * line.unit_price
    
    @api.depends('estimated_total_amount', 'discount_amount')
    def _compute_amount(self):
        for line in self:
            line.amount = line.estimated_total_amount - line.discount_amount
    
    @api.depends('amount', 'sponsor_amount')
    def _compute_patient_amount(self):
        for line in self:
            line.patient_amount = line.amount - line.sponsor_amount