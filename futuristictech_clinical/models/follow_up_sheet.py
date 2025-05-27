# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class FollowUpSheet(models.Model):
    _name = 'hospital.follow.up.sheet'
    _description = 'Follow-Up Sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    title = fields.Char(string='Title', default='Follow-Up Sheet')
    ip_number = fields.Char(string='IP Number', required=True, tracking=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True)
    
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, tracking=True)
    datetime = fields.Date(string='Last Updated Date')
    last_updated_date = fields.Datetime(string='Last Updated Date', default=fields.Datetime.now, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='State', default='draft', tracking=True)
    
     # Hospitalization
    doa = fields.Date(string='Date of Admission', readonly=True)
    dod = fields.Date(string='Date of Discharge')
    admission_reason = fields.Text(string='Admission Reason')
    epileptic_attack = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Epileptic Attack')
    
     # Mental Status Examination
    general_observation = fields.Text(string='General Observation')
    speech = fields.Text(string='Speech')
    mood = fields.Text(string='Mood')
    thought = fields.Text(string='Thought')
    perception = fields.Text(string='Perception')
    cognitive_function = fields.Text(string='Cognitive Function')
    insight = fields.Text(string='Insight')
    
    # Counsellor Observations
    counsellor_observation = fields.Text(string='Counsellor Observation')
     
    hygiene_detail_ids = fields.One2many('hospital.hygiene.detail', 'follow_up_sheet_id', string='Hygiene Details')
    formal_activities_ids = fields.One2many('hospital.activity.record', 'follow_up_sheet_id', string='Formal Activities',
                                        domain=[('activity_type', '=', 'formal')])
    informal_activities_ids = fields.One2many('hospital.activity.record', 'follow_up_sheet_id', string='Informal Activities',
                                          domain=[('activity_type', '=', 'informal')])
    family_session_ids = fields.One2many('hospital.family.session', 'follow_up_sheet_id', string='Family Sessions')
    hygiene_details_ids = fields.One2many('hygiene.detail.line', 'followup_id', string='Hygiene Details')
    incident_details_ids = fields.One2many('incident.detail.line', 'followup_id', string='Incident Details')
    emergency_medicine_ids = fields.One2many('emergency.medicine.line', 'followup_id', string='Emergency Medicines')
    medicine_unconsumed_ids = fields.One2many('medicine.unconsumed.line', 'followup_id', string='Unconsumed Medicines')
    outing_ids = fields.One2many('outing.detail.line', 'followup_id', string='Outings')
    lab_test_ids = fields.One2many('lab.test.line', 'followup_id', string='Lab Tests')
    # outside_consultation_ids = fields.One2many('consultation.line', 'followup_id', string='Outside Consultations')
    outside_consultation_ids = fields.One2many('hospital.outside.consultation', 'follow_up_sheet_id', string='Outside Consultations')
    phone_call_ids = fields.One2many('phone.call.line', 'followup_id', string='Phone Calls')
    counselling_session_ids = fields.One2many('counselling.session.line', 'followup_id', string='Counselling Sessions')
    group_therapy_ids = fields.One2many('group.therapy.line', 'followup_id', string='Group Therapy')

    @api.model_create_multi
    def create(self, vals_list):
        return super(FollowUpSheet, self).create(vals_list)
    
    @api.onchange('ip_number')
    def _onchange_ip_number(self):
        if self.ip_number:
            admission = self.env['hospital.admission'].search([('name', '=', self.ip_number)], limit=1)
            if admission:
                self.patient_id = admission.patient_id
    
    def action_get_details(self):
        self.ensure_one()
        self.last_updated_date = fields.Date.today()
        return True
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
    
    def action_done(self):
        for record in self:
            record.state = 'done'
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
    
    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def get_all_details(self):
        self.ensure_one()
        # This method should populate all the relevant details from other models
        self.datetime = fields.Datetime.now()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Details Updated Successfully!",
                'type': 'rainbow_man',
            }
        }
class HygieneDetail(models.Model):
    _name = 'hospital.hygiene.detail'
    _description = 'Hygiene Detail'
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    parameter = fields.Char(string='Parameter', required=True)
    value = fields.Char(string='Value')
    notes = fields.Text(string='Notes')


class ActivityRecord(models.Model):
    _name = 'hospital.activity.record'
    _description = 'Activity Record'
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    activity = fields.Char(string='Activity')
    comments = fields.Text(string='Comments')
    activity_type = fields.Selection([
        ('formal', 'Formal'),
        ('informal', 'Informal')
    ], string='Activity Type', required=True, default='formal')


class FamilySession(models.Model):
    _name = 'hospital.family.session'
    _description = 'Family Session'
    
    follow_up_sheet_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet', required=True, ondelete='cascade')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    purpose = fields.Char(string='Purpose of the Session')
    discussed = fields.Text(string='Matters Discussed')
    matters_discussed = fields.Text(string='Matters Discussed')
    observation = fields.Text(string='Observation')
    outcome = fields.Text(string='Outcome')
    future_plan = fields.Text(string='Future Plan')
    members_ids = fields.One2many('family.session.member', 'session_id', string='Members')

class FamilySessionMember(models.Model):
    _name = 'family.session.member'
    _description = 'Family Session Member'
    
    session_id = fields.Many2one('family.session.line', string='Session')
    name = fields.Char(string='Name', required=True)
    relationship_id = fields.Many2one('family.relationship', string='Relationship')
    visitor_age = fields.Integer(string='Age')
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    mobile_number = fields.Char(string='Mobile')
    email = fields.Char(string='Email')

class HygieneDetailLine(models.Model):
    _name = 'hygiene.detail.line'
    _description = 'Hygiene Detail Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    parameter_id = fields.Many2one('hygiene.parameter', string='Parameter', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    notes = fields.Text(string='Notes')
    
    def hygiene_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/hygiene_report?parameter_id=%s' % self.parameter_id.id,
            'target': 'new',
        }
    

class FamilyRelationship(models.Model):
    _name = 'family.relationship'
    _description = 'Family Relationship'
    
    name = fields.Char(string='Relationship', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)


class IncidentDetailLine(models.Model):
    _name = 'incident.detail.line'
    _description = 'Incident Detail Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    datetime = fields.Datetime(string='Date & Time', default=fields.Datetime.now)
    incident_type = fields.Selection([
        ('aggression', 'Aggression'),
        ('self_harm', 'Self Harm'),
        ('other', 'Other')
    ], string='Incident Type', required=True)
    location = fields.Char(string='Location')
    description = fields.Text(string='Description')
    action = fields.Text(string='Action Taken')


class EmergencyMedicineLine(models.Model):
    _name = 'emergency.medicine.line'
    _description = 'Emergency Medicine Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    name = fields.Char(string='Reference', required=True)
    requested_date = fields.Datetime(string='Requested Date')
    approved_date = fields.Datetime(string='Approved Date')
    advising_doctor_id = fields.Many2one('res.partner', string='Advising Doctor')
    purpose = fields.Text(string='Purpose')
    notes = fields.Text(string='Notes')
    medicine = fields.Text(string='Medicine Details')
    state = fields.Selection([
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('given', 'Given'),
        ('rejected', 'Rejected')
    ], string='Status', default='requested')


class MedicineUnconsumedLine(models.Model):
    _name = 'medicine.unconsumed.line'
    _description = 'Medicine Unconsumed Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    time = fields.Float(string='Time')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    details = fields.Text(string='Details')
    info = fields.Text(string='Additional Info')
    responsible = fields.Char(string='Responsible Person')


class OutingDetailLine(models.Model):
    _name = 'outing.detail.line'
    _description = 'Outing Detail Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    name = fields.Char(string='Reference')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    nature_of_outing = fields.Char(string='Nature of Outing')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status')

class LabTestLine(models.Model):
    _name = 'lab.test.line'
    _description = 'Lab Test Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    name = fields.Char(string='Reference')
    date_analysis = fields.Date(string='Analysis Date')
    test_type_id = fields.Many2one('lab.test.type', string='Test Type')
    results = fields.Text(string='Results')
    diagnosis = fields.Text(string='Diagnosis')
    pathologist = fields.Char(string='Pathologist')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Status')

class ConsultationLine(models.Model):
    _name = 'consultation.line'
    _description = 'Consultation Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    name = fields.Char(string='Reference')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    doctor_id = fields.Many2one('res.partner', string='Doctor')

class PhoneCallLine(models.Model):
    _name = 'phone.call.line'
    _description = 'Phone Call Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    datetime = fields.Datetime(string='Date & Time', default=fields.Datetime.now)
    caller = fields.Selection([('incoming', 'Incoming'), ('outgoing', 'Outgoing')], string='Call Type')
    caller_name = fields.Char(string='Caller Name')
    phone = fields.Char(string='Phone Number')
    points_discussed = fields.Text(string='Points Discussed')

class CounsellingSessionLine(models.Model):
    _name = 'counselling.session.line'
    _description = 'Counselling Session Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    date = fields.Date(string='Date', default=fields.Date.context_today)
    session_type = fields.Selection([
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('family', 'Family')
    ], string='Session Type', required=True)
    comments = fields.Text(string='Comments')
    state = fields.Selection([
        ('planned', 'Planned'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status')


class GroupTherapyLine(models.Model):
    _name = 'group.therapy.line'
    _description = 'Group Therapy Line'
    
    followup_id = fields.Many2one('hospital.follow.up.sheet', string='Follow-Up Sheet')
    name = fields.Char(string='Session Name')
    start_datetime = fields.Datetime(string='Start Time')
    end_datetime = fields.Datetime(string='End Time')
    program_id = fields.Many2one('therapy.program', string='Program')
    presence = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], string='Presence')
    remarks = fields.Text(string='Remarks')