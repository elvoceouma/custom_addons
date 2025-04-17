# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cancel_expenses = fields.Selection(related='company_id.cancel_expenses', string='Cancel Expense', readonly=False)
