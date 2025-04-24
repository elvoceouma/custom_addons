from odoo import models, fields, api, _

class ConsultationFollowup(models.TransientModel):
    _name = 'consultation.followup'
    _description = 'Consultation Follow-up Wizard'

    consultation_id = fields.Many2one('consultation.consultation', string='Consultation', 
        default=lambda self: self.env.context.get('active_id', False))
    is_sos = fields.Boolean(string='SOS')
    next_followup_date = fields.Date(string='Next Follow-up Date')
    doctor_advice = fields.Text(string='Doctor Advice')
    precautions = fields.Text(string='Precautions')
    todo = fields.Text(string='Todo Before Next Consultation')
    
    @api.onchange('is_sos')
    def _onchange_is_sos(self):
        if self.is_sos:
            self.next_followup_date = False
    
    def save_followup(self):
        self.ensure_one()
        if self.consultation_id:
            vals = {
                'next_followup': True,
                'is_sos': self.is_sos,
                'next_followup_date': self.next_followup_date,
                'doctor_advice': self.doctor_advice,
                'precautions': self.precautions,
                'todo': self.todo,
            }
            self.consultation_id.write(vals)
        return {'type': 'ir.actions.act_window_close'}