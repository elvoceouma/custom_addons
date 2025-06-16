from odoo import models, fields, api, _

class CrmVisits(models.Model):
    _name = 'crm.visits'
    _description = 'CRM Visits'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', readonly=True, default='/')
    lead_id = fields.Many2one('crm.lead', string='Lead', domain="[('type','=','lead')]", required=True)
    date = fields.Date(string='Date', tracking=True, required=True)
    campus_id = fields.Many2one('hospital.hospital', string='Campus', tracking=True)
    visitor = fields.Selection([
        ('Caller', 'Caller'),
        ('Patient', 'Patient'),
        ('Other', 'Other')
    ], string='Visitor', tracking=True)
    
    # Visitor information fields
    visitor_name = fields.Char(string='Visitor Name', tracking=True)
    visitor_age = fields.Char(string='Age')
    visitor_sex = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Transgender', 'Transgender')
    ], string='Sex')
    visitor_relation_patient = fields.Many2one('relationship.master', string='Relationship with Patient', tracking=True)
    visitor_phone = fields.Char(string='Phone')
    visitor_email = fields.Char(string='Email')
    
    state = fields.Selection([
        ('New', 'New'),
        ('no_show', 'No Show'),
        ('Attender Assigned', 'Attender Assigned'),
        ('Counsellor Assigned', 'Counsellor Assigned'),
        ('Closed', 'Closed')
    ], string='State', tracking=True, default='New')
    
    other_visitor_ids = fields.One2many('crm.visits.line', 'visit_id', string='Other Visitors')
    attender = fields.Many2one('hr.employee', string='Attender', domain="[('attender','=',True)]", tracking=True)
    counsellor = fields.Many2one('hr.employee', string='Counsellor', domain="[('counsellor','=',True)]", tracking=True)
    notes = fields.Text(string='Attender Notes', tracking=True)
    counsellor_notes = fields.Text(string='Counsellor Notes', tracking=True)
    feedback = fields.Text(string='Feedback or Specific Issues Raised')
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.visits') or '/'
        return super(CrmVisits, self).create(vals)

class CrmVisitsLine(models.Model):
    _name = 'crm.visits.line'
    _description = 'CRM Visits Line'

    visit_id = fields.Many2one('crm.visits', string='Visit')
    name = fields.Char(string='Name')
    age = fields.Char(string='Age')
    sex = fields.Selection([
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Transgender', 'Transgender')
    ], string='Sex')
    relation = fields.Many2one('relationship.master', string='Relationship')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')