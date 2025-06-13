from odoo import models, fields, api, _

class AdviceCounsellor(models.Model):
    _name = 'advice.counsellor'
    _description = 'Advice to Counsellors'
    _rec_name = 'counsellor_id'
    
    @api.depends('type', 'inpatient_admission_id', 'op_visit_id')
    def _compute_patient(self):
        for record in self:
            if record.type == 'ip' and record.inpatient_admission_id:
                record.patient_id = record.inpatient_admission_id.patient.id
                record.op_visit_id = False
            elif record.type == 'op' and record.op_visit_id:
                record.patient_id = record.op_visit_id.patient_id.id
                record.inpatient_admission_id = False
            else:
                record.patient_id = False
                record.inpatient_admission_id = False
                record.op_visit_id = False
    
    type = fields.Selection([('ip', 'IP'), ('op', 'OP')], string='Type', required=True, default='ip', tracking=True)
    counsellor_id = fields.Many2one('hr.employee', string='Counsellor')
    inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
    op_visit_id = fields.Many2one('op.visits', string='OP Reference')
    patient_id = fields.Many2one('oeh.medical.patient', string='Patient', compute='_compute_patient', store=True)
    followup_type_id = fields.Many2one('followup.type', string='Type', required=True)
    date = fields.Date(string='Date')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    note = fields.Text(string='Advice')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    
# class AdviceClinicalPsychologist(models.Model):
#     _name = 'advice.clinical.psychologist'
#     _description = 'Advice to Clinical Psychologist'
#     _rec_name = 'clinical_psychologist_id'
    
#     @api.depends('type', 'inpatient_admission_id', 'op_visit_id')
#     def _compute_patient(self):
#         for record in self:
#             if record.type == 'ip' and record.inpatient_admission_id:
#                 record.patient_id = record.inpatient_admission_id.patient.id
#                 record.op_visit_id = False
#             elif record.type == 'op' and record.op_visit_id:
#                 record.patient_id = record.op_visit_id.patient_id.id
#                 record.inpatient_admission_id = False
#             else:
#                 record.patient_id = False
#                 record.inpatient_admission_id = False
#                 record.op_visit_id = False
    
#     type = fields.Selection([('ip', 'IP'), ('op', 'OP')], string='Type', required=True, default='ip', tracking=True)
#     clinical_psychologist_id = fields.Many2one('hr.employee', string='Clinical Psychologist')
#     inpatient_admission_id = fields.Many2one('oeh.medical.inpatient', string='IP Number')
#     op_visit_id = fields.Many2one('op.visits', string='OP Reference')
#     patient_id = fields.Many2one('oeh.medical.patient', string='Patient', compute='_compute_patient', store=True)
#     followup_type_id = fields.Many2one('followup.type', string='Type', required=True)
#     date = fields.Date(string='Date')
#     start_date = fields.Datetime(string='Start Date')
#     end_date = fields.Datetime(string='End Date')
#     note = fields.Text(string='Advice')
#     user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)