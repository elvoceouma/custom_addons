from odoo import models, fields, api, _

class MedicalClinicalTrail(models.Model):
    _name = 'medical.clinical.trail'
    _description = 'Clinical Trail'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True, default='/')
    date = fields.Date(string='Date', default=fields.Date.today)
    lead_id = fields.Many2one('crm.lead', string='Lead')
    patient_id = fields.Many2one('medical.patient', string='Patient')
    points_of_discussion = fields.Text(string='Points of Discussion')
    remarks = fields.Text(string='Remarks')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    created_on = fields.Datetime(string='Created on', default=fields.Datetime.now)
    
    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.clinical.trail') or '/'
        return super(MedicalClinicalTrail, self).create(vals)