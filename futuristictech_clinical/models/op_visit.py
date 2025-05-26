# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OpVisit(models.Model):
    _name = 'op.visits'
    _description = 'OP Visits'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'visit_date desc, id desc'

    name = fields.Char(
        string='Reference', 
        readonly=True, 
        default='New',
        copy=False
    )

    patient_id = fields.Many2one(
        'hospital.patient', 
        string='Patient', 
        required=True, 
        tracking=True,
        ondelete='restrict'
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Partner', 
        tracking=True
    )

    visit_date = fields.Datetime(
        string='Visit Date', 
        default=fields.Datetime.now, 
        tracking=True,
        required=True
    )
    treating_doctor = fields.Many2one(
        'hr.employee', 
        string='Treating Doctor', 
        tracking=True,
        domain=[('department_id.name', 'ilike', 'doctor')]
    )
    free_screening = fields.Boolean(
        string='Free Screening', 
        default=False, 
        tracking=True
    )
    followup_type_id = fields.Many2one(
        'followup.type', 
        string='Follow-up Type', 
        tracking=True
    )
    tot_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled')
    ], string='Status', default='draft', tracking=True)
    
    prescription_count = fields.Integer(
        string='Prescriptions Count', 
        compute='_compute_prescription_count'
    )
    invoice_count = fields.Integer(
        string='Invoice Count', 
        compute='_compute_invoice_count'
    )
    
    consultation_type = fields.Selection([
        ('in_person', 'In Person'),
        ('virtual', 'Virtual'),
        ('home_based_consultation', 'Home Based Consultation')
    ], string='Consultation Type', default='in_person', tracking=True)
    
    # Additional useful fields
    notes = fields.Text(string='Notes')
    diagnosis = fields.Text(string='Diagnosis')
    symptoms = fields.Text(string='Symptoms')
    vital_signs = fields.Text(string='Vital Signs')
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency', 
        related='company_id.currency_id', 
        store=True, 
        readonly=True
    )

    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """Auto-populate partner when patient is selected"""
        if self.patient_id:
            # Try to get partner from patient if it has one
            if hasattr(self.patient_id, 'partner_id') and self.patient_id.partner_id:
                self.partner_id = self.patient_id.partner_id
            else:
                # Clear partner if patient doesn't have one
                self.partner_id = False

    @api.model
    def create(self, vals):
        """Generate sequence number for new visits"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('op.visits') or 'New'
        return super(OpVisit, self).create(vals)

    @api.depends('patient_id')
    def _compute_prescription_count(self):
        """Compute prescription count for each visit"""
        for visit in self:
            prescriptions = self.env['hospital.prescription'].search_count([
                ('op_visit_id', '=', visit.id)
            ])
            visit.prescription_count = prescriptions

    @api.depends('patient_id')
    def _compute_invoice_count(self):
        """Compute invoice count for each visit"""
        for visit in self:
            invoices = self.env['account.move'].search_count([
                ('op_visit_id', '=', visit.id),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ])
            visit.invoice_count = invoices

    @api.depends('free_screening')
    def _compute_total_amount(self):
        """Compute total amount based on prescriptions and services"""
        for visit in self:
            if visit.free_screening:
                visit.tot_amount = 0.0
            else:
                # Add logic to compute from related invoices or service lines
                total = 0.0
                invoices = self.env['account.move'].search([
                    ('op_visit_id', '=', visit.id),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted')
                ])
                total = sum(invoices.mapped('amount_total'))
                visit.tot_amount = total

    @api.constrains('visit_date')
    def _check_visit_date(self):
        """Validate visit date is not in future beyond reasonable limit"""
        for visit in self:
            if visit.visit_date and visit.visit_date > fields.Datetime.now():
                # Allow scheduling up to 30 days in advance
                max_future_date = fields.Datetime.now() + fields.timedelta(days=30)
                if visit.visit_date > max_future_date:
                    raise ValidationError(_("Visit date cannot be more than 30 days in the future."))

    def action_draft(self):
        """Reset visit to draft state"""
        self.ensure_one()
        if self.state == 'completed':
            raise ValidationError(_("Completed visits cannot be reset to draft."))
        self.write({'state': 'confirmed'})
        return True
    
    def action_confirmed(self):
        """Complete the visit"""
        self.ensure_one()
        if self.state != 'confirmed':
            raise ValidationError(_("Only confirmed visits can be completed."))
        self.write({'state': 'completed'})
        return True

    def action_cancel(self):
        """Cancel the visit"""
        self.ensure_one()
        if self.state == 'completed':
            raise ValidationError(_("Completed visits cannot be canceled."))
        self.write({'state': 'canceled'})
        return True

    def action_reset_to_draft(self):
        """Reset visit to draft state"""
        self.ensure_one()
        if self.state == 'completed':
            raise ValidationError(_("Completed visits cannot be reset to draft."))
        self.write({'state': 'draft'})
        return True

    def action_view_prescriptions(self):
        """View related prescriptions"""
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Prescriptions'),
            'res_model': 'hospital.prescription',
            'view_mode': 'tree,form',
            'domain': [('op_visit_id', '=', self.id)],
            'context': {
                'default_op_visit_id': self.id,
                'default_patient_id': self.patient_id.id,
            }
        }
        
        if self.prescription_count == 1:
            prescription = self.env['hospital.prescription'].search([('op_visit_id', '=', self.id)], limit=1)
            action.update({
                'view_mode': 'form',
                'res_id': prescription.id,
            })
        
        return action

    def action_view_invoices(self):
        """View related invoices"""
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [
                ('op_visit_id', '=', self.id),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ],
            'context': {
                'default_op_visit_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_move_type': 'out_invoice',
            }
        }
        
        if self.invoice_count == 1:
            invoice = self.env['account.move'].search([
                ('op_visit_id', '=', self.id),
                ('move_type', 'in', ['out_invoice', 'out_refund'])
            ], limit=1)
            action.update({
                'view_mode': 'form',
                'res_id': invoice.id,
            })
        
        return action

    def action_create_prescription(self):
        """Create a new prescription for this visit"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Prescription'),
            'res_model': 'hospital.prescription',
            'view_mode': 'form',
            'context': {
                'default_op_visit_id': self.id,
                'default_patient_id': self.patient_id.id,
                'default_doctor_id': self.treating_doctor.id,
            },
            'target': 'new',
        }

    def action_create_invoice(self):
        """Create a new invoice for this visit"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Invoice'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'context': {
                'default_op_visit_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_move_type': 'out_invoice',
            },
            'target': 'new',
        }

    def name_get(self):
        """Custom display name"""
        result = []
        for visit in self:
            name = f"{visit.name} - {visit.patient_id.name}"
            if visit.visit_date:
                name += f" ({visit.visit_date.strftime('%Y-%m-%d')})"
            result.append((visit.id, name))
        return result

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
    # team_role = fields.Many2one('hr.department', string='Team Role')
    

# Extend hospital.prescription to include op_visit_id if it doesn't exist
class HospitalPrescription(models.Model):
    _inherit = 'hospital.prescription'
    
    op_visit_id = fields.Many2one('op.visits', string='OP Visit')


# Extend account.move to include op_visit_id if it doesn't exist
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    op_visit_id = fields.Many2one('op.visits', string='OP Visit')


class OPBill(models.Model):
    _name = 'hospital.op.bill'
    _description = 'OP Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Bill Number', readonly=True, default=lambda self: _('New'))
    op_visit_id = fields.Many2one('op.visits', string='OP Visit', required=True)
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