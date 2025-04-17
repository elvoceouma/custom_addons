# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    cancel_expenses = fields.Selection([
        ('cancel', 'Cancel Only'),
        ('cancel_reset', "Cancel and Reset to Draft"),
        ('cancel_delete', "Cancel and Delete")
    ], string='Cancel Expense', default="cancel")
