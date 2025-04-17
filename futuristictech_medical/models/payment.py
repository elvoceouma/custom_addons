from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MedicalPayment(models.Model):
    _name = 'medical.payment'
    _description = 'Medical Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Payment Reference', required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'medical.patient', string='Patient', required=True, tracking=True)
    treatment_id = fields.Many2one(
        'medical.treatment', string='Treatment')
    prescription_id = fields.Many2one(
        'medical.prescription', string='Prescription')
    amount = fields.Float(string='Amount', required=True, tracking=True)
    payment_date = fields.Datetime(
        string='Payment Date', default=fields.Datetime.now)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('insurance', 'Insurance'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other')],
        string='Payment Method', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    invoice_id = fields.Many2one(
        'account.move', string='Invoice')
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.payment') or _('New')
        return super(MedicalPayment, self).create(vals)

    def action_confirm(self):
        for payment in self:
            if payment.state != 'draft':
                continue
            
            # Create invoice if needed
            if not payment.invoice_id:
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'partner_id': payment.patient_id.partner_id.id,
                    'invoice_date': fields.Date.today(),
                    'invoice_line_ids': [(0, 0, {
                        'name': f"Medical Payment - {payment.name}",
                        'quantity': 1,
                        'price_unit': payment.amount,
                    })]
                })
                payment.invoice_id = invoice.id
            
            payment.write({'state': 'confirmed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
        }