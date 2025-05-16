# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class InpatientAdmission(models.Model):
    _name = 'hospital.inpatient.admission'
    _description = 'Inpatient Admission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_name'
    
    # Identification fields
    name = fields.Char(string='Inpatient #', readonly=True, default=lambda self: (self.env['ir.sequence'].next_by_code('hospital.inpatient.admission') or ''))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    patient_name = fields.Char(related='patient_id.name', string='Patient Name', store=True)
    patient_mrn = fields.Char(related='patient_id.mrn', string='MRN', store=True)
    
    # Basic information
    patient_title = fields.Selection([
        ('mr', 'MR'),
        ('mrs', 'MRS'),
        ('miss', 'MISS'),
        ('ms', 'MS')
    ], string='Patient Title', tracking=True)
    admitting_person = fields.Char(string='Admitting Person')
    next_barcode_number = fields.Integer(string='Next Bar-code Number', default=1)
    
    # Location information
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)
    block_id = fields.Many2one('hospital.block', string='Block', required=True, tracking=True)
    room_id = fields.Many2one('hospital.room', string='Room', required=True, tracking=True)
    bed_id = fields.Many2one('hospital.bed', string='Bed', required=True, tracking=True)
    
    # Type information
    admission_type = fields.Selection([
        ('emergency', 'Emergency'),
        ('planned', 'Planned'),
        ('transfer', 'Transfer'),
        ('other', 'Other')
    ], string='Admission Type', default='planned', tracking=True)
    
    # Date information
    admission_date = fields.Datetime(string='Admission Date', default=fields.Datetime.now, tracking=True)
    discharge_date = fields.Datetime(string='Discharge Date', tracking=True)
    advised_discharge_date = fields.Datetime(string='Advised Discharge Date', tracking=True)
    next_bill_date = fields.Datetime(string='Next Bill Date', tracking=True)
    
    # Medical information
    condition_before_admission = fields.Text(string='Condition Before Admission')
    nursing_plan = fields.Text(string='Nursing Plan')
    discharge_plan = fields.Text(string='Discharge Plan')
    advice_for_discharge = fields.Text(string='Advice for Discharge')
    
    # Team information
    psychiatrist_id = fields.Many2one('res.partner', string='Psychiatrist', domain=[('is_psychiatrist', '=', True)])
    clinical_psychologist_id = fields.Many2one('res.partner', string='Clinical Psychologist', domain=[('is_clinical_psychologist', '=', True)])
    physician_id = fields.Many2one('res.partner', string='Physician', domain=[('is_physician', '=', True)])
    counsellor_id = fields.Many2one('res.partner', string='Counsellor', domain=[('is_counsellor', '=', True)])
    acting_counsellor_id = fields.Many2one('res.partner', string='Acting Counsellor', domain=[('is_counsellor', '=', True)])
    caretaker_id = fields.Many2one('res.partner', string='Caretaker', domain=[('is_caretaker', '=', True)])
    family_therapist_id = fields.Many2one('res.partner', string='Family Therapist', domain=[('is_family_therapist', '=', True)])
    
    # Administrative information
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    clinical_closure_by = fields.Many2one('res.users', string='Clinical Closure By')
    administrative_closure_by = fields.Many2one('res.users', string='Administrative Closure By')
    
    # Attachments
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    consent_form = fields.Binary(string='Consent Form')
    consent_form_name = fields.Char(string='Consent Form Filename')
    agreement = fields.Binary(string='Agreement')
    agreement_name = fields.Char(string='Agreement Filename')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admission_confirmed', 'Admission Confirmed'),
        ('invoiced', 'Invoiced'),
        ('completed', 'Completed'),
        ('discharge_initiated', 'Discharge Initiated'),
        ('discharged', 'Discharged')
    ], string='State', default='draft', tracking=True)
    
    # Related document links
    document_ids = fields.One2many('hospital.inpatient.document', 'inpatient_id', string='Documents')
    form_ids = fields.One2many('hospital.inpatient.form', 'inpatient_id', string='Forms & Scales')
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] =self.env['ir.sequence'].next_by_code('hospital.inpatient.admission')
        result = super(InpatientAdmission, self).create(vals)
        return result
    
    def action_confirm_admission(self):
        for record in self:
            record.state = 'admission_confirmed'
            if record.bed_id:
                record.bed_id.write({
                    'status': 'occupied',
                    'current_patient_id': record.patient_id.id
                })
    
    def action_initiate_discharge(self):
        for record in self:
            record.state = 'discharge_initiated'
    
    def action_complete_discharge(self):
        for record in self:
            record.state = 'discharged'
            if record.bed_id:
                record.bed_id.write({
                    'status': 'free',
                    'current_patient_id': False
                })
    
    def action_invoiced(self):
        for record in self:
            record.state = 'invoiced'
    
    def action_completed(self):
        for record in self:
            record.state = 'completed'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'
    
    def generate_medicine_box(self):
        # Action to generate medicine box report
        return True
    
    def generate_discharge_summary(self):
        # Action to generate discharge summary
        return True
    
    def generate_final_bill(self):
        # Action to generate final bill
        return True
    
    def generate_food_bill(self):
        # Action to generate food bill
        return True
    
    def view_prescriptions(self):
        # Action to view prescriptions
        return {
            'name': _('Prescriptions'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.prescription',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.patient_id.id)],
        }
    
    def view_medication_forms(self):
        # Action to view medication forms
        return True
    
    def view_admission_forms(self):
        # Action to view admission forms
        return True
    
    def view_assessment_forms(self):
        # Action to view assessment forms
        return True
    
    def view_outing_forms(self):
        # Action to view outing forms
        return True
    
    def view_investigation_forms(self):
        # Action to view investigation forms
        return True
    
    def view_vital_charts(self):
        # Action to view vital charts
        return True
    
    def view_high_support(self):
        return {
            'name': _('High Support Records'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.high.support',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.patient_id.id)],
        }

    def view_mo_sr_admission(self):
        return {
            'name': _('MO/SR Admission Records'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.mo.sr.admission',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.patient_id.id)],
        }

    def view_provisional_bills(self):
        return {
            'name': _('Provisional Bills'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.provisional.bill',
            'type': 'ir.actions.act_window',
            'domain': [('inpatient_id', '=', self.id)],
        }

    def view_ect_consent(self):
        return {
            'name': _('ECT Consent Forms'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.ect.consent',
            'type': 'ir.actions.act_window',
            'domain': [('inpatient_id', '=', self.id)],
        }

    def view_minor_admission(self):
        return {
            'name': _('Minor Admission Records'),
            'view_mode': 'tree,form',
            'res_model': 'hospital.minor.admission',
            'type': 'ir.actions.act_window',
            'domain': [('patient_id', '=', self.patient_id.id)],
        }


    def action_save_form(self):
            """Save the current form"""
            return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel_form(self):
        """Cancel form editing"""
        return {'type': 'ir.actions.act_window_close'}
    
    def action_open_socrates(self):
        """Open SOCRATES form"""
        return self._open_specific_form('socrates', 'SOCRATES Assessment')
    
    def action_open_dtcq_consultation_d(self):
        """Open DTCQ Consultation(D) form"""
        return self._open_specific_form('dtcq_d', 'DTCQ Consultation(D)')
    
    def action_open_dtcq_consultation_a(self):
        """Open DTCQ Consultation(A) form"""
        return self._open_specific_form('dtcq_a', 'DTCQ Consultation(A)')
    
    def action_open_assist(self):
        """Open ASSIST form"""
        return self._open_specific_form('assist', 'ASSIST Assessment')
    
    def action_open_pss_consultation(self):
        """Open PSS Consultation form"""
        return self._open_specific_form('pss', 'PSS Consultation')
    
    def action_open_basis(self):
        """Open BASIS form"""
        return self._open_specific_form('basis', 'BASIS Assessment')
    
    def _open_specific_form(self, form_type, form_name):
        """Helper method to open a specific form type
        
        If a form of this type already exists for the current patient,
        open that form. Otherwise, create a new one with the specified type.
        """
        # Get the current patient_id from context or related record
        patient_id = self.env.context.get('patient_id', False)
        
        # Look for existing form of this type for this patient
        domain = [('form_type', '=', form_type)]
        if patient_id:
            domain.append(('patient_id', '=', patient_id))
            
        existing_form = self.search(domain, limit=1)
        
        if existing_form:
            # Open existing form
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'patient.forms',
                'res_id': existing_form.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # Create new form
            default_values = {
                'name': form_name,
                'form_type': form_type,
            }
            if patient_id:
                default_values['patient_id'] = patient_id
                
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'patient.forms',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_name': form_name, 'default_form_type': form_type}
            }
class InpatientDocument(models.Model):
    _name = 'hospital.inpatient.document'
    _description = 'Inpatient Document'
    
    name = fields.Char(string='Document Name', required=True)
    inpatient_id = fields.Many2one('hospital.inpatient.admission', string='Inpatient', required=True, ondelete='cascade')
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='File Name')
    upload_date = fields.Date(string='Upload Date', default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='Uploaded By', default=lambda self: self.env.user)
    notes = fields.Text(string='Notes')


class InpatientForm(models.Model):
    _name = 'hospital.inpatient.form'
    _description = 'Inpatient Form'
    
    name = fields.Char(string='Form Name', required=True)
    inpatient_id = fields.Many2one('hospital.inpatient.admission', string='Inpatient', required=True, ondelete='cascade')
    form_type = fields.Selection([
        ('socrates', 'SOCRATES'),
        ('dtco_doctor', 'DTCO Consultation (Doctor)'),
        ('dtco_allied', 'DTCO Consultation (Allied)'),
        ('assist', 'ASSIST'),
        ('pss', 'PSS Consultation'),
        ('basis', 'BASIS')
    ], string='Form Type', required=True)
    completion_date = fields.Date(string='Completion Date', default=fields.Date.context_today)
    completed_by = fields.Many2one('res.users', string='Completed By', default=lambda self: self.env.user)
    form_result = fields.Text(string='Form Result')
    form_score = fields.Float(string='Form Score')
    notes = fields.Text(string='Notes') 