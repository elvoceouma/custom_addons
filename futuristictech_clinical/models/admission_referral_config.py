from odoo import models, fields, api

class AdmissionReferralConfig(models.Model):
    _name = 'admission.referral.config'
    _description = 'Admission Referral Configuration'

    name = fields.Char(string='Package Name', required=True)
    bed_type_id = fields.Many2one('hospital.bed.type', string='Bed Type')
    
    # One2many fields
    referral_item_ids = fields.One2many(
        'admission.referral.config.item', 
        'referral_config_id', 
        string='Referral Items'
    )
    
    scale_ids = fields.One2many(
        'admission.referral.config.scale', 
        'referral_config_id', 
        string='Scales'
    )

class AdmissionReferralConfigItem(models.Model):
    _name = 'admission.referral.config.item'
    _description = 'Referral Configuration Items'

    referral_config_id = fields.Many2one(
        'admission.referral.config', 
        string='Referral Configuration'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Product', 
        required=True
    )
    quantity = fields.Float(
        string='Quantity', 
        default=1.0, 
        required=True
    )
    unit_price = fields.Float(
        string='Unit Price', 
        related='product_id.list_price', 
        readonly=True
    )

class AdmissionReferralConfigScale(models.Model):
    _name = 'admission.referral.config.scale'
    _description = 'Referral Configuration Scales'

    referral_config_id = fields.Many2one(
        'admission.referral.config', 
        string='Referral Configuration'
    )
    scale_type = fields.Selection([
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
        ('other', 'Other')
    ], string='Scale Type', required=True)