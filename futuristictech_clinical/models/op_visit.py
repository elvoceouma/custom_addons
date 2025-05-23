# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OpVisit(models.Model):
    _name = 'op.visit'
    _description = 'OP Visits'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', readonly=True, default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner', tracking=True)
    visit_date = fields.Datetime(string='Visit Date', default=fields.Datetime.now, tracking=True)
    treating_doctor = fields.Many2one('hr.employee', string='Treating Doctor', tracking=True)
    treating_doctor_id = fields.Many2one('hr.employee', string='Treating Doctor ID', tracking=True)
    free_screening = fields.Boolean(string='Free Screening', default=False, tracking=True)
    followup_type_id = fields.Many2one('followup.type', string='Follow-up Type', tracking=True)
    tot_amount = fields.Float(string='Total Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', tracking=True)
    prescription_count = fields.Integer(string='Prescriptions Count', compute='_compute_prescription_count')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    team_role = fields.Many2one('hr.department', string='Team Role', tracking=True)
    consultation_type = fields.Selection([
        ('in_person', 'In Person'),
        ('virtual', 'Virtual'),
        ('home_based_consultation', 'Home Based Consultation')
    ], string='Consultation Type', default='in_person', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.visit') or 'New'
        return super(OpVisit, self).create(vals)
    
    def _compute_prescription_count(self):
        # Implement your logic to count prescriptions
        for visit in self:
            prescriptions = self.env['hospital.prescription'].search([('op_visit_id', '=', visit.id)])
            visit.prescription_count = len(prescriptions)
    
    def _compute_invoice_count(self):
        # Implement your logic to count invoices
        for visit in self:
            invoices = self.env['account.move'].search([('op_visit_id', '=', visit.id)])
            visit.invoice_count = len(invoices)
    
    def action_draft(self):
        self.write({'state': 'confirmed'})
    
    def action_confirmed(self):
        self.write({'state': 'completed'})
    
    def action_complete(self):
        self.write({'state': 'completed'})
    
    def action_cancel(self):
        self.write({'state': 'canceled'})

    def action_view_prescriptions(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Prescriptions',
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('op_visit_id', '=', self.id)],
            'context': {'default_op_visit_id': self.id}
        }

    def action_view_invoices(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('op_visit_id', '=', self.id)],
            'context': {'default_op_visit_id': self.id}
        }

class FollowupType(models.Model):
    _name = 'followup.type'
    _description = 'Follow-up Type'
    
    name = fields.Char(string='Name', required=True)
    type = fields.Selection([
        ('ip', 'Inpatient'),
        ('op', 'Outpatient')
    ], string='Type', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    team_role = fields.Many2one('hr.department', string='Team Role')
    

# Extend hospital.prescription to include op_visit_id if it doesn't exist
class HospitalPrescription(models.Model):
    _inherit = 'hospital.prescription'
    
    op_visit_id = fields.Many2one('op.visit', string='OP Visit')


# Extend account.move to include op_visit_id if it doesn't exist
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    op_visit_id = fields.Many2one('op.visit', string='OP Visit')


class OPBill(models.Model):
    _name = 'hospital.op.bill'
    _description = 'OP Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Bill Number', readonly=True, default=lambda self: _('New'))
    op_visit_id = fields.Many2one('op.visit', string='OP Visit', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', related='op_visit_id.patient_id', store=True)
    date = fields.Date(string='Bill Date', default=fields.Date.context_today)
    
    line_ids = fields.One2many('hospital.op.bill.line', 'bill_id', string='Bill Lines')
    
    amount_untaxed = fields.Float(string='Untaxed Amount', compute='_compute_amounts', store=True)
    amount_tax = fields.Float(string='Tax', compute='_compute_amounts', store=True)
    amount_total = fields.Float(string='Total', compute='_compute_amounts', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.op.bill') or _('New')
        return super(OPBill, self).create(vals_list)
    
    @api.depends('line_ids.price_subtotal')
    def _compute_amounts(self):
        for bill in self:
            amount_untaxed = sum(line.price_subtotal for line in bill.line_ids)
            amount_tax = sum(line.price_tax for line in bill.line_ids)
            bill.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })


class OPBillLine(models.Model):
    _name = 'hospital.op.bill.line'
    _description = 'OP Bill Line'
    
    bill_id = fields.Many2one('hospital.op.bill', string='Bill', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    name = fields.Text(string='Description', required=True)
    
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    
    price_unit = fields.Float(string='Unit Price', required=True)
    discount = fields.Float(string='Discount (%)', default=0.0)
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount', store=True)
    price_tax = fields.Float(string='Tax', compute='_compute_amount', store=True)
    price_total = fields.Float(string='Total', compute='_compute_amount', store=True)
    
    @api.depends('quantity', 'price_unit', 'discount', 'tax_ids')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(price, currency=None, quantity=line.quantity)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })