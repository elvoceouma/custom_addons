from odoo import models, fields, api
from datetime import datetime, timedelta


class ClinicalPsychologistSession(models.Model):
    _name = 'clinical.psychologist.session'
    _description = 'Clinical Psychologist Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(string='Session Number', default='New', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('started', 'Check In'),
        ('Check_Out', 'Check Out'),
        ('completed', 'Completed')
    ], string='State', default='draft', tracking=True)
    
    type = fields.Selection([
        ('ip', 'Inpatient'),
        ('op', 'Outpatient')
    ], string='Type', required=True, default='op', tracking=True)
    
    inpatient_admission_id = fields.Many2one(
        'hospital.inpatient.admission',
        string='IP Number',
        tracking=True
    )
    op_visit_id = fields.Many2one(
        'op.visit',
        string='OP Visit',
        tracking=True
    )
    patient_id = fields.Many2one(
        'res.partner',
        string='Patient',
        required=True,
        readonly=True,
        tracking=True
    )
    patient_age = fields.Integer(
        string='Age',
        readonly=True,
        # related='patient_id.age'
    )
    sex = fields.Selection(
        [('male', 'Male'),
         ('female', 'Female')],
        string='Sex',
        readonly=True
    )
    
    followup_type_id = fields.Many2one(
        'followup.type',
        string='Type',
        tracking=True
    )
    team_role = fields.Char(string='Team Role', invisible=True)
    consultation_type = fields.Selection([
        ('clinic', 'Clinic Consultation'),
        ('virtual', 'Virtual Consultation'),
        ('home', 'Home-Based Consultation')
    ], string='Consultation Type', readonly=True)
    
    date = fields.Date(
        string='Date',
        default=fields.Date.context_today,
        required=True,
        tracking=True
    )
    clinical_psychologist_id = fields.Many2one(
        'res.users',
        string='Psychologist/Family Therapist',
        # domain="[('team_role', 'in', ['clinical_psychologist','family_therapist'])]",
        tracking=True
    )
    session_type_id = fields.Many2one(
        'session.type',
        string='Session Type',
        required=True,
        tracking=True
    )
    session_subtype_id = fields.Many2one(
        'session.subtype',
        string='Session Sub Type',
        tracking=True
    )
    
    check_in_datetime = fields.Datetime(string='Check-In', readonly=True)
    check_out_datetime = fields.Datetime(string='Check-Out', readonly=True)
    virtual_consultation_url = fields.Char(string='Virtual Consultation URL', readonly=True)
    geo_location = fields.Char(string='Geo Location', readonly=True)
    
    # Session Content
    session_target_ids = fields.Many2many(
        'session.target',
        string='Session Targets'
    )
    objective = fields.Html(string='Objective')
    note = fields.Html(string='Session Description')
    outcome = fields.Html(string='Outcome of Session')
    plan = fields.Html(string='Plan')
    consultant_comments = fields.Html(string='Consultant Comments')
    
    # Assignments
    assignment_ids = fields.One2many(
        'session.assignment',
        'session_id',
        string='Home/Work Assignments'
    )
    
    # Follow-up
    next_followup = fields.Boolean(string='Next Follow-up', invisible=True)
    is_sos = fields.Boolean(string='SOS', readonly=True)
    next_followup_date = fields.Date(string='Next Follow-up Date', readonly=True)
    doctor_advice = fields.Text(string='Doctor Advice', readonly=True)
    precautions = fields.Text(string='Precautions', readonly=True)
    todo = fields.Text(string='To Do', readonly=True)
    
    user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        readonly=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('clinical.psychologist.session') or 'New'
        return super().create(vals)

    def action_start(self):
        """Check In action"""
        self.write({
            'state': 'started',
            'check_in_datetime': fields.Datetime.now()
        })

    def action_end(self):
        """Check Out action"""
        self.write({
            'state': 'Check_Out',
            'check_out_datetime': fields.Datetime.now()
        })

    def action_complete(self):
        """Complete action"""
        self.write({
            'state': 'completed'
        })

    def view_doctor_consultation(self):
        """View doctor consultation"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Doctor Consultation',
            'res_model': 'doctor.consultation',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id}
        }

    def view_cp_consultation(self):
        """View CP consultation"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'CP Consultation',
            'res_model': 'cp.consultation',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id}
        }

    def action_screening(self):
        """Action to view screening records"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Screening',
            'res_model': 'clinical.psychologist.screening',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {
                'search_default_patient_id': [self.patient_id.id],
                'default_patient_id': self.patient_id.id
            }
        }

    def action_counsellor_session(self):
        """Action to create/view counsellor session"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Counsellor Session',
            'res_model': 'counsellor.session',
            'view_mode': 'tree,form',
            'domain': [('resident_id', '=', self.patient_id.id)],
            'context': {
                'search_default_resident_id': [self.patient_id.id],
                'default_resident_id': self.patient_id.id
            }
        }

    def action_lab_tests(self):
        """Action to view lab tests"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lab Tests',
            'res_model': 'lab.test',
            'view_mode': 'tree,form',
            'domain': [('patient', '=', self.patient_id.id)],
            'context': {
                'search_default_patient': [self.patient_id.id],
                'default_patient': self.patient_id.id
            }
        }

    def action_cross_consultation(self):
        """Action to view cross consultation"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cross Consultation',
            'res_model': 'cross.consultation',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {
                'search_default_patient_id': [self.patient_id.id],
                'default_patient_id': self.patient_id.id
            }
        }

    def action_crm_notes(self):
        """Action to view CRM notes"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'CRM Notes',
            'res_model': 'crm.notes',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {
                'search_default_patient_id': [self.patient_id.id],
                'default_patient_id': self.patient_id.id
            }
        }

    def view_psychiatrist_evaluation_form(self):
        """View psychiatrist evaluation form"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Psychiatrist Evaluation',
            'res_model': 'psychiatrist.evaluation',
            'view_mode': 'form',
            'context': {
                'default_type': self.type,
                'default_inpatient_admission_id': self.inpatient_admission_id.id if self.inpatient_admission_id else False,
                'default_op_visit_id': self.op_visit_id.id if self.op_visit_id else False,
                'default_patient_id': self.patient_id.id
            }
        }

    def view_patient_documents(self):
        """View patient documents"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Patient Documents',
            'res_model': 'patient.documents',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id}
        }

    def view_feedback_form(self):
        """View feedback form"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Feedback Form',
            'res_model': 'feedback.form',
            'view_mode': 'tree,form',
            'domain': [('session_id', '=', self.id)],
            'context': {'default_session_id': self.id}
        }

    def send_feedback_form_psychologist(self):
        """Send feedback form to psychologist"""
        # Implementation for sending feedback form
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Feedback Form',
                'message': 'Feedback form sent successfully',
                'type': 'success'
            }
        }
    
    def action_next_followup(self):
        """Action to set next follow-up date"""
        next_followup_date = datetime.now().date() + timedelta(days=30)
        self.write({
            'date': next_followup_date
        })

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'ip':
            self.op_visit_id = False
        else:
            self.inpatient_admission_id = False

    @api.onchange('inpatient_admission_id')
    def _onchange_inpatient_admission_id(self):
        if self.inpatient_admission_id:
            self.patient_id = self.inpatient_admission_id.patient_id

    @api.onchange('op_visit_id')
    def _onchange_op_visit_id(self):
        if self.op_visit_id:
            self.patient_id = self.op_visit_id.patient_id

    @api.onchange('session_type_id')
    def _onchange_session_type_id(self):
        if self.session_type_id:
            self.session_subtype_id = False

    def action_clinical_psychologist_screening(self):
        """Action to view clinical psychologist screening"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clinical Psychologist Screening',
            'res_model': 'clinical.psychologist.screening',
            'view_mode': 'tree,form',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'context': {'default_patient_id': self.patient_id.id}
        }
class SessionAssignment(models.Model):
    _name = 'session.assignment'
    _description = 'Session Assignment'

    name = fields.Char(string='Assignment', required=True)
    session_id = fields.Many2one('clinical.psychologist.session', string='Session')

    # Session Types and Subtypes
class SessionType(models.Model):
    _name = 'session.type'
    _description = 'Session Type'

    name = fields.Char(string='Session Type', required=True)
    description = fields.Text(string='Description')
    
class SessionSubtype(models.Model):
    _name = 'session.subtype'
    _description = 'Session Subtype'

    name = fields.Char(string='Session Subtype', required=True)
    session_type_id = fields.Many2one('session.type', string='Session Type', required=True)
    description = fields.Text(string='Description')