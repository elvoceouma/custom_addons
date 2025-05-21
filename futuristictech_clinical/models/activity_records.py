from odoo import models, fields, api, _


class ActivityRecord(models.Model):
    _name = 'activity.records'
    _description = "Activity Record"
    _rec_name = "name_seq"
    
    name = fields.Char(string="Name")
    name_seq = fields.Char(string="Reference", readonly=True, copy=False, default=lambda self: _('New'))
    
    # Basic patient information
    ip_number = fields.Char(string="IP Number")
    patient_name = fields.Char(string="Patient Name")
    age = fields.Integer(string="Age")
    mrn_no = fields.Char(string="MRN No")
    # campus_id = fields.Many2one('hospital.hospital', string="Campus")  # Assuming this is a Many2one field
    campus_id = fields.Many2one('hospital.hospital', string='Campus', required=True, tracking=True)

    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    
    # Record information
    date = fields.Date(string="Date")
    doctor = fields.Many2one('res.users', string="Doctor")
 
    # ward = fields.Many2one('oeh.medical.health.center.ward', string='Ward')
    ward = fields.Many2one('hospital.block', string='Ward', required=True, tracking=True)

    room = fields.Many2one('hospital.block', string='Room', required=True, tracking=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string="Status", default='draft')
    
    # One2many relationships for notebook pages
    ward_transfer_line_ids = fields.One2many(
        'ward.transfer.line', 
        'activity_id', 
        string="Ward Transfer Lines"
    )
    
    medical_equipments_line_ids = fields.One2many(
        'medical.equipments.line', 
        'activity_id', 
        string="Medical Equipment Lines"
    )
    
    ect_chart_line_ids = fields.One2many(
        'ect.chart.line', 
        'activity_id', 
        string="ECT Chart Lines"
    )
    
    consultation_line_ids = fields.One2many(
        'consultation.line', 
        'activity_id', 
        string="Consultation Visit Lines"
    )
    
    psychoassessment_line_ids = fields.One2many(
        'psychoassessment.line', 
        'activity_id', 
        string="Psychotherapy Assessment Lines"
    )
    
    alternaive_line_ids = fields.One2many(
        'alternative.line', 
        'activity_id', 
        string="Alternative Supportive Lines"
    )
    
    radiology_line_ids = fields.One2many(
        'radiology.line', 
        'activity_id', 
        string="Radiology Lines"
    )
    
    lab_line_ids = fields.One2many(
        'lab.line', 
        'activity_id', 
        string="Lab Procedure Lines"
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name_seq', _('New')) == _('New'):
                vals['name_seq'] = self.env['ir.sequence'].next_by_code('activity.records') or _('New')
        return super(ActivityRecord, self).create(vals_list)
    
    def action_confirm(self):
        self.state = 'in_progress'
    
    def action_inprogress(self):
        self.state = 'done'

# Models for One2many relationships
class WardTransferLine(models.Model):
    _name = 'ward.transfer.line'
    _description = "Ward Transfer Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    from_ward_id = fields.Many2one('hospital.ward', string="From Ward")
    from_room_id = fields.Many2one('hospital.room', string="From Room")
    to_ward_id = fields.Many2one('hospital.ward', string="To Ward")
    to_room_id = fields.Many2one('hospital.room', string="To Room")
    hand_over_nurse = fields.Many2one('res.users', string="Hand Over Nurse")
    take_over_nurse = fields.Many2one('res.users', string="Take Over Nurse")


class MedicalEquipmentsLine(models.Model):
    _name = 'medical.equipments.line'
    _description = "Medical Equipment Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    equipmet_name = fields.Char(string="Equipment Name")
    connect_time = fields.Float(string="Connect Time")
    disconnect_time = fields.Float(string="Disconnect Time")
    incharge_id = fields.Many2one('res.users', string="Incharge")
    remarks = fields.Text(string="Remarks")


class EctChartLine(models.Model):
    _name = 'ect.chart.line'
    _description = "ECT Chart Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    psychiatrist_id = fields.Many2one('res.users', string="Psychiatrist")
    assistant_id = fields.Many2one('res.users', string="Assistant")
    anaesthetist = fields.Char(string="Anaesthetist")
    equipment_used = fields.Char(string="Equipment Used")
    any_other = fields.Text(string="Any Other")


class ConsultationLine(models.Model):
    _name = 'consultation.line'
    _description = "Consultation Visit Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    consultant_name = fields.Char(string="Consultant Name")
    visit_time = fields.Float(string="Visit Time")


class PsychoassessmentLine(models.Model):
    _name = 'psychoassessment.line' 
    _description = "Psychotherapy Assessment Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    consultant_name = fields.Char(string="Consultant Name")
    procedure = fields.Text(string="Procedure")


class AlternativeLine(models.Model):
    _name = 'alternative.line'
    _description = "Alternative Supportive Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    consultant_name = fields.Char(string="Consultant Name")
    therapy = fields.Text(string="Therapy")


class RadiologyLine(models.Model):
    _name = 'radiology.line'
    _description = "Radiology Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    radiology = fields.Text(string="Radiology")


class LabLine(models.Model):
    _name = 'lab.line'
    _description = "Lab Procedure Line"
    
    activity_id = fields.Many2one('activity.records', string="Activity Record")
    date_time = fields.Datetime(string="Date & Time", default=fields.Datetime.now)
    lab_procedure = fields.Text(string="Lab Procedure")
    no_of_units = fields.Integer(string="No. of Units")