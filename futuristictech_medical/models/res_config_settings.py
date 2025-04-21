from odoo import _, api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    enable_ocn = fields.Boolean(string='Enable OCN', default=False)
    disable_redirect_firebase_dynamic_link = fields.Boolean(string='Disable Redirect Firebase Dynamic Link', default=False)
    enable_avalara = fields.Boolean(string='Enable Avalara', default=False)
    map_box_token = fields.Char(string='Map Box Token')
    setting_account_avatax = fields.Char(string='Account Avatax')   
    