from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CreateHospitalSaleWizard(models.TransientModel):
    _name = 'create.hospital.sale.wizard'
    _description = 'Create Hospital Sale'
    
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    patient_id = fields.Many2one('medical.patient', string='Patient')
    doctor_id = fields.Many2one('medical.doctor', string='Doctor')
    campus_id = fields.Many2one('campus.master', string='Campus')
    service_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('treatment', 'Treatment'),
        ('medication', 'Medication'),
        ('lab_test', 'Lab Test'),
        ('procedure', 'Procedure'),
        ('package', 'Package'),
        ('other', 'Other')
    ], string='Service Type', required=True, default='consultation')
    appointment_id = fields.Many2one('medical.appointment', string='Appointment')
    case_id = fields.Many2one('medical.case', string='Medical Case')
    prescription_id = fields.Many2one('medical.prescription', string='Prescription')
    
    # Fields for filtering records
    patient_domain = fields.Char(compute='_compute_patient_domain')
    doctor_domain = fields.Char(compute='_compute_doctor_domain')
    appointment_domain = fields.Char(compute='_compute_appointment_domain')
    case_domain = fields.Char(compute='_compute_case_domain')
    prescription_domain = fields.Char(compute='_compute_prescription_domain')
    
    @api.depends('partner_id')
    def _compute_patient_domain(self):
        for wizard in self:
            if wizard.partner_id:
                wizard.patient_domain = f"[('partner_id', '=', {wizard.partner_id.id})]"
            else:
                wizard.patient_domain = "[]"
    
    @api.depends('campus_id')
    def _compute_doctor_domain(self):
        for wizard in self:
            if wizard.campus_id:
                wizard.doctor_domain = f"[('hospital_id', '=', {wizard.campus_id.id})]"
            else:
                wizard.doctor_domain = "[]"
    
    @api.depends('patient_id', 'doctor_id')
    def _compute_appointment_domain(self):
        for wizard in self:
            domain = []
            if wizard.patient_id:
                domain.append(('patient_id', '=', wizard.patient_id.id))
            if wizard.doctor_id:
                domain.append(('doctor_id', '=', wizard.doctor_id.id))
            wizard.appointment_domain = str(domain)
    
    @api.depends('patient_id', 'doctor_id')
    def _compute_case_domain(self):
        for wizard in self:
            domain = []
            if wizard.patient_id:
                domain.append(('patient_id', '=', wizard.patient_id.id))
            if wizard.doctor_id:
                domain.append(('doctor_id', '=', wizard.doctor_id.id))
            wizard.case_domain = str(domain)
    
    @api.depends('patient_id', 'doctor_id')
    def _compute_prescription_domain(self):
        for wizard in self:
            domain = []
            if wizard.patient_id:
                domain.append(('patient_id', '=', wizard.patient_id.id))
            if wizard.doctor_id:
                domain.append(('doctor_id', '=', wizard.doctor_id.id))
            wizard.prescription_domain = str(domain)
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """When customer changes, try to find related patient"""
        if self.partner_id:
            patient = self.env['medical.patient'].search([
                ('partner_id', '=', self.partner_id.id)
            ], limit=1)
            if patient:
                self.patient_id = patient.id
            else:
                self.patient_id = False
                return {
                    'warning': {
                        'title': _('No Patient Found'),
                        'message': _('No patient record found for this customer. You will need to create one.')
                    }
                }
    
    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        """When patient changes, update related fields"""
        if self.patient_id and not self.partner_id:
            self.partner_id = self.patient_id.partner_id
        
        if self.patient_id and self.patient_id.department_id:
            return {
                'domain': {
                    'doctor_id': [('department_id', '=', self.patient_id.department_id.id)]
                }
            }
    
    @api.onchange('service_type')
    def _onchange_service_type(self):
        """Reset related fields when service type changes"""
        if self.service_type == 'consultation':
            self.case_id = False
            self.prescription_id = False
        elif self.service_type == 'treatment':
            self.appointment_id = False
            self.prescription_id = False
        elif self.service_type == 'medication':
            self.appointment_id = False
            self.case_id = False
            
    @api.onchange('appointment_id')
    def _onchange_appointment_id(self):
        """When appointment is selected, update related fields"""
        if self.appointment_id:
            self.patient_id = self.appointment_id.patient_id
            self.doctor_id = self.appointment_id.doctor_id
            self.case_id = self.appointment_id.case_id
    
    @api.onchange('case_id')
    def _onchange_case_id(self):
        """When case is selected, update related fields"""
        if self.case_id:
            self.patient_id = self.case_id.patient_id
            self.doctor_id = self.case_id.doctor_id
    
    @api.onchange('prescription_id')
    def _onchange_prescription_id(self):
        """When prescription is selected, update related fields"""
        if self.prescription_id:
            self.patient_id = self.prescription_id.patient_id
            self.doctor_id = self.prescription_id.doctor_id
    
    def action_create_patient(self):
        """Create a new patient from the current customer"""
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
                    'message': _('Patient already exists for this customer and has been linked to the wizard.')
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
            'target': 'new',
        }
    
    def action_create_hospital_sale(self):
        """Create hospital sale order based on selected options"""
        self.ensure_one()
        
        if not self.patient_id:
            raise ValidationError(_("Patient is required for hospital sales"))
        
        if not self.doctor_id:
            raise ValidationError(_("Doctor is required for hospital sales"))
        
        # Create the sale order
        order_vals = {
            'partner_id': self.partner_id.id,
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'campus_id': self.campus_id.id,
            'is_hospital_sale': True,
            'service_type': self.service_type,
        }
        
        # Add specific fields based on service type
        if self.service_type == 'consultation' and self.appointment_id:
            order_vals['appointment_id'] = self.appointment_id.id
        
        if self.service_type == 'treatment' and self.case_id:
            order_vals['case_id'] = self.case_id.id
        
        if self.service_type == 'medication' and self.prescription_id:
            order_vals['prescription_id'] = self.prescription_id.id
        
        # Create the order
        sale_order = self.env['sale.order'].create(order_vals)
        
        # Add order lines based on service type
        if self.service_type == 'consultation':
            # Add consultation product
            if self.doctor_id and self.doctor_id.doctor_product_ids:
                consultation_product = self.doctor_id.doctor_product_ids.filtered(
                    lambda p: p.detailed_type == 'service' and 'consult' in p.name.lower()
                )
                if consultation_product:
                    self.env['sale.order.line'].create({
                        'order_id': sale_order.id,
                        'product_id': consultation_product[0].id,
                        'name': consultation_product[0].name,
                        'product_uom_qty': 1,
                        'price_unit': consultation_product[0].list_price,
                        'doctor_id': self.doctor_id.id,
                    })
        
        elif self.service_type == 'medication' and self.prescription_id:
            # Add medication lines from prescription
            for med_line in self.prescription_id.medication_lines:
                self.env['sale.order.line'].create({
                    'order_id': sale_order.id,
                    'product_id': med_line.medication_id.product_id.id,
                    'name': med_line.medication_id.name,
                    'product_uom_qty': med_line.quantity,
                    'price_unit': med_line.medication_id.product_id.list_price,
                    'prescription_line_id': med_line.id,
                })
        
        # Open the created sale order
        return {
            'name': _('Hospital Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'type': 'ir.actions.act_window',
        }