from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class MedicalAppointment(models.Model):
    _name = 'medical.appointment'
    _description = 'Medical Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'appointment_date desc, id desc'

    name = fields.Char(string='Appointment Reference', required=True, readonly=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'medical.patient', string='Patient', required=True, tracking=True)
    doctor_id = fields.Many2one(
        'medical.doctor', string='Doctor', required=True, tracking=True)
    department_id = fields.Many2one(
        'medical.department', string='Department',
        related='doctor_id.department_id', store=True)
    hospital_id = fields.Many2one(
        'medical.hospital', string='Hospital',
        related='department_id.hospital_id', store=True)
    appointment_date = fields.Datetime(
        string='Appointment Date', required=True, tracking=True)
    end_time = fields.Datetime(string='End Time', compute='_compute_end_time', store=True)
    duration = fields.Float(string='Duration (minutes)', default=30.0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')],
        string='Status', default='draft', tracking=True)
    purpose = fields.Text(string='Appointment Purpose')
    case_id = fields.Many2one('medical.case', string='Medical Case')
    symptoms = fields.Text(string='Symptoms', related='case_id.symptoms', readonly=True)
    diagnosis = fields.Text(string='Diagnosis', related='case_id.diagnosis', readonly=True)
    notes = fields.Text(string='Notes')
    campus_id = fields.Many2one('medical.campus', string='Campus')
    lead_id = fields.Many2one('crm.lead', string='Lead/Opportunity')
    patient_history = fields.Html(string='Patient History', compute='_compute_patient_history')
    sale_count = fields.Integer(string='Sale Count', compute='_compute_sale_count')
    invoice_count = fields.Integer(string='Invoice Count', compute='_compute_invoice_count')
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.appointment') or _('New')
        return super(MedicalAppointment, self).create(vals)

    @api.depends('appointment_date', 'duration')
    def _compute_end_time(self):
        for appointment in self:
            if appointment.appointment_date:
                duration_timedelta = timedelta(minutes=appointment.duration)
                appointment.end_time = appointment.appointment_date + duration_timedelta
            else:
                appointment.end_time = False

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})
        # Create a case if this is a new patient encounter
        if not self.case_id:
            case_vals = {
                'patient_id': self.patient_id.id,
                'doctor_id': self.doctor_id.id,
                'symptoms': self.purpose,
            }
            case = self.env['medical.case'].create(case_vals)
            self.write({'case_id': case.id})
        return True

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_case(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Medical Case',
            'view_mode': 'form',
            'res_model': 'medical.case',
            'res_id': self.case_id.id,
            'target': 'current',
        }

    def action_create_sale_order(self):
        self.ensure_one()
        # Implement sale order creation logic here
        return True

    def action_view_sale_orders(self):
        self.ensure_one()
        # Implement logic to view related sale orders
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Orders',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('appointment_id', '=', self.id)],
            'target': 'current',
        }

    def action_view_invoices(self):
        self.ensure_one()
        # Implement logic to view related invoices
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('appointment_id', '=', self.id)],
            'target': 'current',
        }

    def _compute_sale_count(self):
        for appointment in self:
            appointment.sale_count = self.env['sale.order'].search_count([('appointment_id', '=', appointment.id)])

    def _compute_invoice_count(self):
        for appointment in self:
            appointment.invoice_count = self.env['account.move'].search_count([('appointment_id', '=', appointment.id)])

    @api.depends('patient_id')
    def _compute_patient_history(self):
        for record in self:
            if record.patient_id:
                history = "<h3>Patient History</h3><ul>"
                
                # Get past medical cases
                cases = self.env['medical.case'].search([
                    ('patient_id', '=', record.patient_id.id),
                    ('id', '!=', record.case_id.id if record.case_id else False)
                ], limit=5, order='date_start desc')
                
                if cases:
                    history += "<li><strong>Past Medical Cases:</strong><ul>"
                    for case in cases:
                        history += "<li>{} - {} ({})</li>".format(
                            case.name, case.diagnosis or 'No diagnosis', case.date_start)
                    history += "</ul></li>"
                
                # Get past appointments
                appointments = self.env['medical.appointment'].search([
                    ('patient_id', '=', record.patient_id.id),
                    ('id', '!=', record.id),
                    ('state', 'in', ['done', 'cancelled'])
                ], limit=5, order='appointment_date desc')
                
                if appointments:
                    history += "<li><strong>Past Appointments:</strong><ul>"
                    for appointment in appointments:
                        history += "<li>{} - {} ({}) - {}</li>".format(
                            appointment.name, appointment.doctor_id.name, 
                            appointment.appointment_date, appointment.state)
                    history += "</ul></li>"
                
                # Get prescriptions
                prescriptions = self.env['medical.prescription'].search([
                    ('patient_id', '=', record.patient_id.id)
                ], limit=5, order='date desc')
                
                if prescriptions:
                    history += "<li><strong>Recent Prescriptions:</strong><ul>"
                    for prescription in prescriptions:
                        history += "<li>{} - {} ({})</li>".format(
                            prescription.name, prescription.doctor_id.name, prescription.date)
                    history += "</ul></li>"
                
                history += "</ul>"
                record.patient_history = history
            else:
                record.patient_history = False

    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):
        if self.doctor_id:
            self.department_id = self.doctor_id.department_id.id

    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        for appointment in self:
            if appointment.appointment_date and appointment.appointment_date < fields.Datetime.now():
                raise ValidationError(_('Cannot schedule appointments in the past!'))

    def check_availability(self):
        """Check if the doctor is available at the selected time"""
        self.ensure_one()
        if not (self.doctor_id and self.appointment_date):
            return False
            
        # Convert appointment date to day of week (0-6, Monday is 0)
        day_of_week = str(self.appointment_date.weekday())
        
        # Find doctor schedule for this day
        schedule = self.env['doctor.schedule'].search([
            ('doctor_id', '=', self.doctor_id.id),
            ('day_of_week', '=', day_of_week),
            ('is_working_day', '=', True)
        ], limit=1)
        
        if not schedule:
            return False
            
        # Check if time is within doctor's working hours
        app_time = self.appointment_date.hour + self.appointment_date.minute / 60.0
        if app_time < schedule.start_time or app_time > schedule.end_time:
            return False
            
        # Check for overlapping appointments
        end_time = self.end_time or (self.appointment_date + timedelta(minutes=self.duration))
        overlapping = self.search([
            ('doctor_id', '=', self.doctor_id.id),
            ('state', 'in', ['confirmed', 'done']),
            ('id', '!=', self.id),
            '|',
            '&', ('appointment_date', '<=', self.appointment_date), ('end_time', '>', self.appointment_date),
            '&', ('appointment_date', '<', end_time), ('appointment_date', '>=', self.appointment_date)
        ])
        
        return not overlapping
        
    def action_check_availability_ui(self):
        """UI action for checking availability"""
        self.ensure_one()
        result = self.check_availability()
        if result:
            message = _("The selected time slot is available.")
            notification_type = 'success'
        else:
            message = _("The selected time slot is not available. Please choose another time.")
            notification_type = 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Availability Check'),   
                'message': message,
                'sticky': False,
                'type': notification_type,
            }
        }