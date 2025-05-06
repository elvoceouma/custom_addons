# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class OPVisit(models.Model):
    _name = 'hospital.op.visit'
    _description = 'Outpatient Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    
    name = fields.Char(string='Reference', readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    related_partner = fields.Many2one('res.partner', string='Related Partner')
    date = fields.Datetime(string='Visit Date', default=fields.Datetime.now, tracking=True)
    physician_id = fields.Many2one('res.partner', string='Treating Doctor', 
                                  domain=[('is_physician', '=', True)], tracking=True)
    
    visit_type = fields.Selection([
        ('initial', 'Initial Visit'),
        ('follow_up', 'Follow-Up'),
        ('emergency', 'Emergency'),
        ('referral', 'Referral')
    ], string='Type', default='initial', tracking=True)
    
    consultation_type = fields.Selection([
        ('general', 'General'),
        ('specialist', 'Specialist'),
        ('emergency', 'Emergency')
    ], string='Consultation Type', default='general', tracking=True)
    
    title = fields.Char(string='Title', default='New')
    free_screening = fields.Boolean(string='Free Screening', default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', tracking=True)
    
    reason = fields.Text(string='Reason for Visit')
    diagnosis = fields.Text(string='Diagnosis')
    treatment = fields.Text(string='Treatment')
    notes = fields.Text(string='Notes')
    
    prescription_ids = fields.One2many('hospital.prescription', 'op_visit_id', string='Prescriptions')
    prescription_count = fields.Integer(string='Prescription Count', compute='_compute_prescription_count')
    
    bill_ids = fields.One2many('hospital.op.bill', 'op_visit_id', string='OP Bills')
    bill_count = fields.Integer(string='Bill Count', compute='_compute_bill_count')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hospital.op.visit') or _('New')
        return super(OPVisit, self).create(vals_list)
    
    @api.depends('prescription_ids')
    def _compute_prescription_count(self):
        for record in self:
            record.prescription_count = len(record.prescription_ids)
    
    @api.depends('bill_ids')
    def _compute_bill_count(self):
        for record in self:
            record.bill_count = len(record.bill_ids)
    
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        if self.patient_id:
            self.related_partner = self.patient_id.partner_id
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_complete(self):
        for record in self:
            record.state = 'completed'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'
    
    def action_save(self):
        return True
    
    def action_discard(self):
        return {'type': 'ir.actions.act_window_close'}
    
    def action_view_prescriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Prescriptions'),
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('op_visit_id', '=', self.id)],
            'context': {'default_op_visit_id': self.id, 'default_patient_id': self.patient_id.id},
        }
    
    def action_view_bills(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('OP Bills'),
            'res_model': 'hospital.op.bill',
            'view_mode': 'tree,form',
            'domain': [('op_visit_id', '=', self.id)],
            'context': {'default_op_visit_id': self.id, 'default_patient_id': self.patient_id.id},
        }


class OPBill(models.Model):
    _name = 'hospital.op.bill'
    _description = 'OP Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Bill Number', readonly=True, default=lambda self: _('New'))
    op_visit_id = fields.Many2one('hospital.op.visit', string='OP Visit', required=True)
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