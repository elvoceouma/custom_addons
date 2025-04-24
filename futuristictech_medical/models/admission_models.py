from odoo import models, fields, api

class AdmissionConsultation(models.Model):
    _name = 'admission.consultation'
    _description = 'Admission Consultation'
    
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    followup_type_id = fields.Many2one('followup.type', string='Type', required=True)
    quantity = fields.Float(string='Qty', required=True)
    unit_price = fields.Float(string='Price')

    
class AdmissionRoomType(models.Model):
    _name = 'admission.room.type'
    _description = 'Admission Room Type'
    
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    product_id = fields.Many2one('product.product', string='Room Type', required=True)
    quantity = fields.Float(string='No. of Days', required=True)
    unit_price = fields.Float(string='Price')


class AdmissionScaleType(models.Model):
    _name = 'admission.scale.type'
    _description = 'Admission Scale Types'
    
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    scale_type = fields.Selection([
        ('assist_who', 'ASSIST - WHO'),
        ('basis_32', 'BASIS - 32'),
        ('dtcq_8_alcohol', 'DTCQ 8 - ALCOHOL'),
        ('dtcq_8_drugs', 'DTCQ 8 - DRUGS'),
        ('socrates', 'SOCRATES'),
        ('pss', 'PSS'),
        ('treatment_entry', 'Treatment Entry'),
        ('cross_cutting_symptom_measure', 'Cross - Cutting Symptom Measure'),
        ('disability_assessment_who_proxy', 'Disability Assessment WHO Proxy'),
        ('disability_assessment_who_self', 'Disability Assessment WHO Self'),
        ('mania_adult_dsm', 'Mania Adult - DSM'),
        ('personality_inventory_brief_self', 'Personality Inventory Brief Self'),
        ('repetitive_thoughts_behaviours', 'Repetitive Thoughts and Behaviours'),
        ('depression_adult_dsm', 'Depression - Adult DSM'),
        ('psychosis_symptom_severity', 'Psychosis Symptom Severity'),
        ('casig_therapist', 'CASIG Therapist')
    ], string='Scale Type', required=True)

    
class AdmissionMiscItem(models.Model):
    _name = 'admission.misc.item'
    _description = 'Admission Miscellaneous Item'
    
    consultation_id = fields.Many2one('consultation.consultation', string='Consultation')
    product_id = fields.Many2one('product.product', string='Room Type', required=True)
    quantity = fields.Float(string='Qty', required=True)
    unit_price = fields.Float(string='Price')