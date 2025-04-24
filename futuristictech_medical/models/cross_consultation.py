from odoo import models, fields, api

class CrossConsultationConsultation(models.Model):
    _name = 'cross.consultation.consultation'
    _description = 'Cross Consultation'
    
    cross_consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    doctor_id = fields.Many2one('hr.employee', string='Doctor', required=True)
    followup_type_id = fields.Many2one('followup.type', string='Type', required=True)

    @api.onchange('cross_consultation_id')
    def _onchange_cross_consultation_id(self):
        domain = {}
        if self.cross_consultation_id:
            domain['followup_type_id'] = [('type', '=', self.cross_consultation_id.type)]
        return {'domain': domain}
    
    @api.onchange('followup_type_id')
    def _onchange_followup_type_id(self):
        domain = {}
        if self.followup_type_id.team_role:
            employee_ids = self.env['hr.employee'].search([('team_role', '=', self.followup_type_id.team_role)]).ids
            domain['doctor_id'] = [('id', 'in', employee_ids)]
        return {'domain': domain}