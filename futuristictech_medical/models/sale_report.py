from odoo import models, fields, api


class SaleReport(models.Model):
    _inherit = 'sale.report'
    
    # Add hospital-specific fields to the sales report
    patient_id = fields.Many2one('medical.patient', string='Patient', readonly=True)
    doctor_id = fields.Many2one('medical.doctor', string='Doctor', readonly=True)
    campus_id = fields.Many2one('campus.master', string='Campus', readonly=True)
    service_type = fields.Selection([
        ('consultation', 'Consultation'),
        ('treatment', 'Treatment'),
        ('medication', 'Medication'),
        ('lab_test', 'Lab Test'),
        ('procedure', 'Procedure'),
        ('package', 'Package'),
        ('other', 'Other')
    ], string='Service Type', readonly=True)
    is_hospital_sale = fields.Boolean(string='Is Hospital Sale', readonly=True)
    
    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['patient_id'] = "s.patient_id"
        res['doctor_id'] = "s.doctor_id"
        res['campus_id'] = "s.campus_id"
        res['service_type'] = "s.service_type"
        res['is_hospital_sale'] = "s.is_hospital_sale"
        return res
        
    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.patient_id,
            s.doctor_id,
            s.campus_id,
            s.service_type,
            s.is_hospital_sale"""
        return res