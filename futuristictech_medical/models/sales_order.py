from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Fields related to hospital management
    patient_id = fields.Many2one('medical.patient', string='Patient')
    doctor_id = fields.Many2one('medical.doctor', string='Doctor')
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    is_hospital_sale = fields.Boolean(string='Is Hospital Sale', default=False)
    appointment_id = fields.Many2one('medical.appointment', string='Appointment')
    case_id = fields.Many2one('medical.case', string='Medical Case')
    prescription_id = fields.Many2one('medical.prescription', string='Prescription')
    inpatient_id = fields.Many2one('medical.inpatient', string='Inpatient')
    service_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('treatment', 'Treatment'),
        ('medication', 'Medication'),
        ('lab_test', 'Lab Test'),
        ('procedure', 'Procedure'),
        ('package', 'Package'),
        ('other', 'Other')
    ], string='Service Type')
    lead_id = fields.Many2one('crm.lead', string='Lead')
    
    # Computed fields
    patient_registration = fields.Char(related='patient_id.registration_number', string='Patient ID', store=True)
    patient_history = fields.Html(string='Patient History', compute='_compute_patient_history')
    
    @api.depends('patient_id')
    def _compute_patient_history(self):
        for order in self:
            if order.patient_id:
                history = "<h3>Patient History</h3><ul>"
                
                # Get past medical cases
                cases = self.env['medical.case'].search([
                    ('patient_id', '=', order.patient_id.id),
                    ('id', '!=', order.case_id.id if order.case_id else False)
                ], limit=5, order='date_start desc')
                
                if cases:
                    history += "<li><strong>Past Medical Cases:</strong><ul>"
                    for case in cases:
                        history += f"<li>{case.name} - {case.diagnosis or 'No diagnosis'} ({case.date_start})</li>"
                    history += "</ul></li>"
                
                # Get past prescriptions
                prescriptions = self.env['medical.prescription'].search([
                    ('patient_id', '=', order.patient_id.id),
                    ('id', '!=', order.prescription_id.id if order.prescription_id else False)
                ], limit=5, order='date desc')
                
                if prescriptions:
                    history += "<li><strong>Past Prescriptions:</strong><ul>"
                    for prescription in prescriptions:
                        history += f"<li>{prescription.name} - {prescription.doctor_id.name or 'Unknown doctor'} ({prescription.date})</li>"
                    history += "</ul></li>"
                
                # Get past treatments
                treatments = self.env['medical.treatment'].search([
                    ('patient_id', '=', order.patient_id.id)
                ], limit=5, order='date desc')
                
                if treatments:
                    history += "<li><strong>Past Treatments:</strong><ul>"
                    for treatment in treatments:
                        history += f"<li>{treatment.name} - {treatment.treatment_type_id.name} ({treatment.date})</li>"
                    history += "</ul></li>"
                
                history += "</ul>"
                order.patient_history = history
            else:
                order.patient_history = False
    
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """When patient changes, update partner and other related fields"""
        if self.patient_id:
            self.partner_id = self.patient_id.partner_id
            # Set default values based on patient
            return {
                'domain': {
                    'doctor_id': [('department_id', '=', self.patient_id.department_id.id)] if self.patient_id.department_id else []
                }
            }
    
    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        """When doctor changes, update department and other fields"""
        if self.doctor_id:
            self.campus_id = self.doctor_id.hospital_id.id
    
    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        """When appointment is selected, update related fields"""
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
            self.doctor_id = self.appointment_id.doctor_id
            self.case_id = self.appointment_id.case_id
            self.service_type = 'consultation'
            # Add the consultation product to the order line
            if self.doctor_id and self.doctor_id.doctor_product_ids:
                consultation_product = self.doctor_id.doctor_product_ids.filtered(lambda p: p.detailed_type == 'service' and 'consult' in p.name.lower())
                if consultation_product:
                    self.order_line = [(0, 0, {
                        'product_id': consultation_product[0].id,
                        'name': consultation_product[0].name,
                        'product_uom_qty': 1,
                        'price_unit': consultation_product[0].list_price,
                    })]
    
    @api.onchange('case_id')
    def _onchange_case_id(self):
        """When medical case is selected, update related fields"""
        if self.case_id:
            self.patient_id = self.case_id.patient_id
            self.doctor_id = self.case_id.doctor_id
            
    @api.onchange('prescription_id')
    def _onchange_prescription_id(self):
        """When prescription is selected, add medication to order lines"""
        if self.prescription_id:
            self.patient_id = self.prescription_id.patient_id
            self.doctor_id = self.prescription_id.doctor_id
            self.service_type = 'medication'
            
            # Add prescription lines to order
            order_lines = []
            for med_line in self.prescription_id.medication_lines:
                order_lines.append((0, 0, {
                    'product_id': med_line.medication_id.product_id.id,
                    'name': med_line.medication_id.name,
                    'product_uom_qty': med_line.quantity,
                    'price_unit': med_line.medication_id.product_id.list_price,
                }))
            
            if order_lines:
                self.order_line = order_lines
    
    def action_confirm(self):
        """Override to handle hospital-specific actions on confirm"""
        for order in self:
            if order.is_hospital_sale:
                # If the sale is linked to an appointment, update the appointment state
                if order.appointment_id and order.appointment_id.state == 'draft':
                    order.appointment_id.action_confirm()
                
                # If this is a medication sale from prescription, mark prescription as dispensed
                if order.service_type == 'medication' and order.prescription_id:
                    order.prescription_id.action_dispense()
                    
                # Create a payment record if needed
                if order.service_type in ['consultation', 'treatment', 'procedure']:
                    payment_obj = self.env['medical.payment']
                    payment_vals = {
                        'patient_id': order.patient_id.id,
                        'amount': order.amount_total,
                        'payment_date': fields.Datetime.now(),
                        'payment_method': 'other',  # Default
                        'state': 'draft',
                    }
                    
                    if order.service_type == 'treatment' and order.case_id:
                        # Find the latest treatment for this case
                        treatment = self.env['medical.treatment'].search([
                            ('case_id', '=', order.case_id.id)
                        ], limit=1, order='id desc')
                        
                        if treatment:
                            payment_vals['treatment_id'] = treatment.id
                    
                    elif order.service_type == 'consultation' and order.appointment_id:
                        # Try to find a prescription linked to this appointment
                        prescription = self.env['medical.prescription'].search([
                            ('appointment_id', '=', order.appointment_id.id)
                        ], limit=1)
                        
                        if prescription:
                            payment_vals['prescription_id'] = prescription.id
                    
                    # Create the payment record
                    payment = payment_obj.create(payment_vals)
                    
                    # Link the sale order to this payment for reference
                    # We'll need to add this field to the medical.payment model
                    payment.write({'sale_order_id': order.id})
            
        return super(SaleOrder, self).action_confirm()
    
    def action_create_patient(self):
        """Create a new patient from the current order partner"""
        self.ensure_one()
        if not self.partner_id:
            raise ValidationError(_("Please select a customer first"))
        
        # Check if a patient already exists for this partner
        existing_patient = self.env['medical.patient'].search([
            ('partner_id', '=', self.partner_id.id)
        ], limit=1)
        
        if existing_patient:
            self.patient_id = existing_patient.id
            return {
                'warning': {
                    'title': _('Existing Patient'),
                    'message': _('Patient already exists for this customer and has been linked to the order.')
                }
            }
        
        # Create new patient
        patient_vals = {
            'partner_id': self.partner_id.id,
            'registration_number': self.env['ir.sequence'].next_by_code('medical.patient'),
            'hospital_id': self.campus_id.id if self.campus_id else False,
            # Add other default values here
        }
        
        new_patient = self.env['medical.patient'].create(patient_vals)
        self.patient_id = new_patient.id
        
        return {
            'name': _('Patient'),
            'view_mode': 'form',
            'res_model': 'medical.patient',
            'res_id': new_patient.id,
            'type': 'ir.actions.act_window',
        }
    
    def action_create_appointment(self):
        """Create a new appointment from this order"""
        self.ensure_one()
        if not self.patient_id:
            raise ValidationError(_("Please select a patient first"))
        
        if not self.doctor_id:
            raise ValidationError(_("Please select a doctor first"))
        
        # Create new appointment
        appointment_vals = {
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'department_id': self.doctor_id.department_id.id,
            'appointment_date': fields.Datetime.now() + timedelta(days=1),  # Default to tomorrow
            'purpose': _('Created from sales order %s') % self.name,
            'state': 'draft',
        }
        
        new_appointment = self.env['medical.appointment'].create(appointment_vals)
        self.appointment_id = new_appointment.id
        self.service_type = 'consultation'
        
        return {
            'name': _('Appointment'),
            'view_mode': 'form',
            'res_model': 'medical.appointment',
            'res_id': new_appointment.id,
            'type': 'ir.actions.act_window',
        }
        
    def action_view_appointment(self):
        """View the linked appointment"""
        self.ensure_one()
        if not self.appointment_id:
            raise ValidationError(_("No appointment linked to this order"))
        
        return {
            'name': _('Appointment'),
            'view_mode': 'form',
            'res_model': 'medical.appointment',
            'res_id': self.appointment_id.id,
            'type': 'ir.actions.act_window',
        }
    
    def action_create_case(self):
        """Create a new medical case from this order"""
        self.ensure_one()
        if not self.patient_id:
            raise ValidationError(_("Please select a patient first"))
        
        if not self.doctor_id:
            raise ValidationError(_("Please select a doctor first"))
        
        # Create new case
        case_vals = {
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'date_start': fields.Datetime.now(),
            'state': 'draft',
        }
        
        new_case = self.env['medical.case'].create(case_vals)
        self.case_id = new_case.id
        
        return {
            'name': _('Medical Case'),
            'view_mode': 'form',
            'res_model': 'medical.case',
            'res_id': new_case.id,
            'type': 'ir.actions.act_window',
        }
        
    def action_view_case(self):
        """View the linked medical case"""
        self.ensure_one()
        if not self.case_id:
            raise ValidationError(_("No medical case linked to this order"))
        
        return {
            'name': _('Medical Case'),
            'view_mode': 'form',
            'res_model': 'medical.case',
            'res_id': self.case_id.id,
            'type': 'ir.actions.act_window',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # Fields related to hospital management
    doctor_id = fields.Many2one('medical.doctor', string='Assigned Doctor')
    is_medication = fields.Boolean(string='Is Medication', compute='_compute_is_medication', store=True)
    is_treatment = fields.Boolean(string='Is Treatment', compute='_compute_is_treatment', store=True)
    is_consultation = fields.Boolean(string='Is Consultation', compute='_compute_is_consultation', store=True)
    is_lab_test = fields.Boolean(string='Is Lab Test', compute='_compute_is_lab_test', store=True)
    prescription_line_id = fields.Many2one('medical.prescription.line', string='Prescription Line')
    treatment_id = fields.Many2one('medical.treatment', string='Treatment')
    lab_test_id = fields.Many2one('medical.labtest', string='Lab Test')
    
    @api.depends('product_id')
    def _compute_is_medication(self):
        """Check if product is linked to a medication"""
        for line in self:
            line.is_medication = bool(self.env['medical.medication'].search_count([
                ('product_id', '=', line.product_id.id)
            ]))
    
    @api.depends('product_id')
    def _compute_is_treatment(self):
        """Check if product is linked to a treatment type"""
        for line in self:
            line.is_treatment = bool(self.env['medical.treatment.type'].search_count([
                ('name', 'ilike', line.product_id.name)
            ]))
    
    @api.depends('product_id')
    def _compute_is_consultation(self):
        """Check if product is a consultation service"""
        for line in self:
            line.is_consultation = line.product_id.detailed_type == 'service' and 'consult' in line.product_id.name.lower()
    
    @api.depends('product_id')
    def _compute_is_lab_test(self):
        """Check if product is linked to a lab test"""
        for line in self:
            line.is_lab_test = bool(self.env['medical.labtest.types'].search_count([
                ('product_id', '=', line.product_id.id)
            ]))
    
    @api.onchange('product_id')
    def _onchange_product_id_medical(self):
        """Handle medical-specific logic when product changes"""
        if self.order_id.is_hospital_sale and self.product_id:
            # If it's a consultation, suggest a doctor if not already set
            if self.is_consultation and not self.doctor_id:
                doctors = self.env['medical.doctor'].search([
                    ('active', '=', True),
                    ('doctor_product_ids', 'in', [self.product_id.id])
                ], limit=1)
                
                if doctors:
                    self.doctor_id = doctors[0].id
                    
            # If it's a medication, check available stock
            if self.is_medication:
                medication = self.env['medical.medication'].search([
                    ('product_id', '=', self.product_id.id)
                ], limit=1)
                
                if medication and medication.stock_quantity < self.product_uom_qty:
                    return {
                        'warning': {
                            'title': _('Stock Warning'),
                            'message': _('There are only %s units available for this medication.') % medication.stock_quantity
                        }
                    }


class MedicalPayment(models.Model):
    _inherit = 'medical.payment'
    
    # Add reference to sale order
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    
    def action_view_invoice(self):
        """Also allow to view invoice from sales order if available"""
        self.ensure_one()
        
        if self.invoice_id:
            return super(MedicalPayment, self).action_view_invoice()
        elif self.sale_order_id and self.sale_order_id.invoice_ids:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoice',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': self.sale_order_id.invoice_ids[0].id,
            }
        else:
            raise ValidationError(_("No invoice found for this payment."))


class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'
    
    # Add related fields to sales
    sale_order_ids = fields.One2many('sale.order', 'appointment_id', string='Sales Orders')
    sale_count = fields.Integer(string='Sale Count', compute='_compute_sale_count')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    
    @api.depends('sale_order_ids')
    def _compute_sale_count(self):
        for appointment in self:
            appointment.sale_count = len(appointment.sale_order_ids)
    
    @api.depends('sale_order_ids.invoice_ids')
    def _compute_invoice_count(self):
        for appointment in self:
            appointment.invoice_count = len(appointment.mapped('sale_order_ids.invoice_ids'))
    
    def action_create_sale_order(self):
        """Create a new sale order from this appointment"""
        self.ensure_one()
        
        # Find consultation product from doctor
        product_id = False
        if self.doctor_id and self.doctor_id.doctor_product_ids:
            consultation_products = self.doctor_id.doctor_product_ids.filtered(
                lambda p: p.detailed_type == 'service' and 'consult' in p.name.lower()
            )
            if consultation_products:
                product_id = consultation_products[0].id
        
        # If no product found from doctor, search for generic consultation product
        if not product_id:
            consultation_products = self.env['product.product'].search([
                ('detailed_type', '=', 'service'),
                ('name', 'ilike', 'consult')
            ], limit=1)
            if consultation_products:
                product_id = consultation_products[0].id
        
        # Create the sale order
        order_vals = {
            'partner_id': self.patient_id.partner_id.id,
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'appointment_id': self.id,
            'is_hospital_sale': True,
            'service_type': 'consultation',
        }
        
        # Add order line if product found
        if product_id:
            product = self.env['product.product'].browse(product_id)
            order_vals['order_line'] = [(0, 0, {
                'product_id': product_id,
                'name': product.name,
                'product_uom_qty': 1,
                'price_unit': product.list_price,
            })]
        
        sale_order = self.env['sale.order'].create(order_vals)
        
        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
        }
    
    def action_view_sale_orders(self):
        """View sale orders related to this appointment"""
        self.ensure_one()
        
        if not self.sale_order_ids:
            # If no sale orders exist, create one
            return self.action_create_sale_order()
        
        action = {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
        }
        
        if len(self.sale_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_order_ids.id,
            })
            
        return action
    
    def action_view_invoices(self):
        """View invoices related to this appointment's sale orders"""
        self.ensure_one()
        
        invoices = self.mapped('sale_order_ids.invoice_ids')
        
        if not invoices:
            raise ValidationError(_("No invoices found for this appointment."))
        
        action = {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
        }
        
        if len(invoices) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': invoices.id,
            })
            
        return action


class MedicalCase(models.Model):
    _inherit = 'medical.case'
    
    # Add related fields to sales
    sale_order_ids = fields.One2many('sale.order', 'case_id', string='Sales Orders')
    sale_count = fields.Integer(string='Sale Count', compute='_compute_sale_count')
    
    @api.depends('sale_order_ids')
    def _compute_sale_count(self):
        for case in self:
            case.sale_count = len(case.sale_order_ids)
    
    def action_view_sale_orders(self):
        """View sale orders related to this case"""
        self.ensure_one()
        
        action = {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
        }
        
        if len(self.sale_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_order_ids.id,
            })
            
        return action
    
    def action_create_sale_order(self):
        """Create a new sale order from this case"""
        self.ensure_one()
        
        order_vals = {
            'partner_id': self.patient_id.partner_id.id,
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'case_id': self.id,
            'is_hospital_sale': True,
            'service_type': 'treatment',
        }
        
        sale_order = self.env['sale.order'].create(order_vals)
        
        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
        }


class MedicalPrescription(models.Model):
    _inherit = 'medical.prescription'
    
    # Add related fields to sales
    sale_order_ids = fields.One2many('sale.order', 'prescription_id', string='Sales Orders')
    sale_count = fields.Integer(string='Sale Count', compute='_compute_sale_count')
    
    @api.depends('sale_order_ids')
    def _compute_sale_count(self):
        for prescription in self:
            prescription.sale_count = len(prescription.sale_order_ids)
    
    def action_view_sale_orders(self):
        """View sale orders related to this prescription"""
        self.ensure_one()
        
        action = {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.sale_order_ids.ids)],
        }
        
        if len(self.sale_order_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.sale_order_ids.id,
            })
            
        return action
    
    def action_create_sale_order(self):
        """Create a new sale order from this prescription"""
        self.ensure_one()
        
        order_vals = {
            'partner_id': self.patient_id.partner_id.id,
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'prescription_id': self.id,
            'is_hospital_sale': True,
            'service_type': 'medication',
        }
        
        # Add order lines for medications
        order_lines = []
        for med_line in self.medication_lines:
            order_lines.append((0, 0, {
                'product_id': med_line.medication_id.product_id.id,
                'name': med_line.medication_id.name,
                'product_uom_qty': med_line.quantity,
                'price_unit': med_line.medication_id.product_id.list_price,
                'prescription_line_id': med_line.id,
            }))
        
        if order_lines:
            order_vals['order_line'] = order_lines
        
        sale_order = self.env['sale.order'].create(order_vals)
        
        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
        }
    
