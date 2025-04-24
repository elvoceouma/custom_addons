from odoo import models, fields, api

class ConsultationPrescriptionLine(models.Model):
    _name = 'consultation.prescription.line'
    _description = 'Consultation Prescription Line'

    @api.model
    def default_get(self, fields):
        rec = super(ConsultationPrescriptionLine, self).default_get(fields)
        context = self.env.context
        if context.get('psychiatrist_id'):
            employee_id = self.env['hr.employee'].browse(context.get('psychiatrist_id'))
            if employee_id and employee_id.related_doctor_id:
                rec.update({
                    'doctor': employee_id.related_doctor_id.id,
                    'speciality': employee_id.related_doctor_id.speciality and employee_id.related_doctor_id.speciality.id or False,
                })
        return rec
        
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    doctor = fields.Many2one('res.partner', string='Physician', required=True)
    speciality = fields.Many2one('medical.speciality', string='Speciality')
    name = fields.Many2one('product.product', string='Medicines', required=True)
    prescription_type = fields.Selection([
        ('SOS', 'SOS'), 
        ('Definite', 'Definite'), 
        ('Repetitive', 'Repetitive')
    ], string='Type', required=True)
    start_treatment = fields.Datetime(string='From')
    end_treatment = fields.Datetime(string='To')
    mrgn = fields.Float(string='M')
    noon = fields.Float(string='AN')
    evng = fields.Float(string='E')
    night = fields.Float(string='N')
    dose_form = fields.Many2one('product.form', string='Form')
    product_uom = fields.Many2one('uom.uom', string='UOM')
    indication = fields.Many2one('oeh.medical.pathology', string='Indication')
    common_dosage = fields.Many2one('oeh.medical.dosage', string='Frequency')
    take = fields.Selection([
        ('After Food', 'After Food'), 
        ('Before Food', 'Before Food')
    ], string='Take')
    
    @api.model
    def create(self, vals):
        consultation_id = self.env['consultation.consultation'].browse(vals.get('consultation_id', False))
        if consultation_id:
            consultation_id.prescription_status = 'changed'
        return super(ConsultationPrescriptionLine, self).create(vals)
        
    def write(self, vals):
        for rec in self:
            if rec.consultation_id:
                rec.consultation_id.prescription_status = 'changed'
        return super(ConsultationPrescriptionLine, self).write(vals)
        
    def unlink(self):
        for rec in self:
            if rec.consultation_id:
                rec.consultation_id.prescription_status = 'changed'
        return super(ConsultationPrescriptionLine, self).unlink()