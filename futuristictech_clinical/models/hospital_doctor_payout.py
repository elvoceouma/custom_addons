from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HospitalDoctorPayout(models.Model):
    _name = 'hospital.doctor.payout'
    _description = 'Doctor Payout'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Name', required=True, tracking=True)
    doctor_id = fields.Many2one('hospital.physician', string='Doctor', required=True, tracking=True)
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
        
        # Create vendor bill logic here
        
        self.state = 'paid'
        return True
        
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

    def create_vendor_bill(self):
        """Create vendor bill based on the payout lines"""
        if not self.payout_line_ids:
            raise UserError(_('Please add payout lines first.'))
        
        # Create vendor bill logic here
        invoice_vals = {
            'partner_id': self.doctor_id.partner_id.id,
            'date_invoice': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'name': line.name,
            }) for line in self.payout_line_ids],
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        self.invoice_id = invoice.id
        self.state = 'paid'
        
        return True

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
    quantity = fields.Float(string='Quantity', default=1.0)
    price_unit = fields.Float(string='Unit Price')
    price_subtotal = fields.Float(string='Amount', compute='_compute_price_subtotal', store=True)
    is_cancelled = fields.Boolean(string='Is Cancelled', default=False)
    
    @api.depends('quantity', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit