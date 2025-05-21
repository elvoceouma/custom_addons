from odoo import models, fields, api, _
from datetime import datetime


class NurseAssessment(models.Model):
    _name = "nurse.assessment"
    _description = "Nurse Assessment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name_seq'

    name = fields.Char(string='Assessment', readonly=True)
    name_seq = fields.Char(string='Assessment Reference', required=True, copy=False, readonly=True,
                        default=lambda self: _('New'))
    
    # Patient Information
    ip_number = fields.Char(string='IP Number')
    patient_name = fields.Char(string='Patient Name')
    age = fields.Integer(string='Age')
    mrn_no = fields.Char(string='MRN No')
    date = fields.Date(string='Date', default=fields.Date.today)
    patient_gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender')
    campus_id = fields.Many2one('hospital.hospital', string='Campus')
    
    # Vitals
    nurse_bp = fields.Char(string='BP in mm/hg')
    temperature = fields.Float(string='Temperature')
    weight = fields.Float(string='weight in Kg')
    saturation = fields.Float(string='Saturation(If Required)%')
    nurse_pulse = fields.Integer(string='Pulse in bpm ')
    respiratory_rate = fields.Integer(string='Respiratory Rate')
    grbs = fields.Float(string='GRBS')
    
    # Examination
    level_consciousness = fields.Selection([
        ('consciousness', 'Consciousness'),
        ('unconsciousness', 'Unconsciousness'),
       
    ], string='Level of Consciousness')
    respiratory_status = fields.Selection([
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal')
    ], string='Respiratory Status')
    skin_integrity = fields.Selection([
        ('intact', 'Intact'),
        ('not_intact', 'Not Intact')
    ], string='Skin Integrity')
    any_other_finding = fields.Boolean(string='Any Other Finding')
    finding_notes = fields.Text(string='Finding Notes')
    
    # Other Information
    current_medications = fields.Text(string='Current Medications')
    diet = fields.Selection([
        ('normal', 'Normal'),
        ('specific_diet', 'Speific Diet'),

    ], string='Diet')
    investigation_ordered = fields.Text(string='Investigation Ordered')
    diet_note = fields.Text(string='Diet Notes')
    
    # Special Conditions
    vulnerable = fields.Boolean(string='Vulnerable')
    pain_score = fields.Selection([
        ('0', '0 - No Pain'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10 - Severe Pain')
    ], string='Pain Score')
    special_care = fields.Text(string='Special Care Instructions')
    
    # Risk Factors
    pressure_sores = fields.Boolean(string='Pressure Sores')
    restraints = fields.Boolean(string='Restraints')
    fall = fields.Boolean(string='Fall Risk')
    pressure_note = fields.Text(string='Pressure Notes')
    restraints_used = fields.Text(string='Restraints Used')
    dvt = fields.Boolean(string='DVT Risk')
    
    # State management
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string='Status', default='draft', tracking=True)
    
    @api.model
    def create(self, vals):
        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('nurse.assessment') or _('New')
        result = super(NurseAssessment, self).create(vals)
        return result
    
    def action_inprogress(self):
        """Set assessment to in progress state"""
        self.write({'state': 'in_progress'})
    
    def action_confirm(self):
        """Complete the assessment"""
        self.write({'state': 'completed'})