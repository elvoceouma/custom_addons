# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    is_cancel = fields.Boolean('Is Cancel', compute='_compute_is_reset')
    is_reset = fields.Boolean('Is Reset', compute='_compute_is_reset')
    is_delete = fields.Boolean('Is Delete', compute='_compute_is_reset')

    @api.depends('employee_id')
    def _compute_is_reset(self):
        for sheet in self:
            is_expense_user = self.user_has_groups('bi_hr_expense_cancel.group_cancel_expense')
            if is_expense_user:
                if self.env.company.cancel_expenses == 'cancel':
                    sheet.is_cancel = True
                    sheet.is_reset = False
                    sheet.is_delete = False
                elif self.env.company.cancel_expenses == 'cancel_reset':
                    sheet.is_cancel = True
                    sheet.is_reset = True
                    sheet.is_delete = False
                elif self.env.company.cancel_expenses == 'cancel_delete':
                    sheet.is_cancel = True
                    sheet.is_reset = True
                    sheet.is_delete = True
            else:
                sheet.is_cancel = False
                sheet.is_reset = False
                sheet.is_delete = False

    def action_cancel(self):
        for expense in self:
            if expense.state == 'done':
                # Handle posted entries
                for move in expense.account_move_ids:
                    if move.state == 'posted':
                        move.button_draft()
                    move.button_cancel()
            expense.write({'state': 'cancel'})

    def action_reset(self):
        self.ensure_one()
        # Add creator check
        if not self.env.user.has_group('bi_hr_expense_cancel.group_cancel_expense'):
            raise UserError(_("You don't have permission to reset this expense."))
        if self.create_uid.id != self.env.user.id:
            raise UserError(_("Only the creator can reset this expense."))
        return self.write({'state': 'draft'})

    def action_unlink(self):
        self.ensure_one()
        # Add creator check
        if not self.env.user.has_group('bi_hr_expense_cancel.group_cancel_expense'):
            raise UserError(_("You don't have permission to delete this expense."))
        if self.create_uid.id != self.env.user.id:
            raise UserError(_("Only the creator can delete this expense."))
        for sheet in self.expense_line_ids:
            sheet.unlink()
        return self.unlink()


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def action_mass_cancel(self):
        for expense in self:
            if not self.env.user.has_group('bi_hr_expense_cancel.group_cancel_expense'):
                raise UserError(_("You don't have permission to cancel expenses."))
            if expense.create_uid.id != self.env.user.id:
                raise UserError(_("You can only cancel expenses that you created."))
            expense.sheet_id.action_cancel()

    def action_mass_reset(self):
        for expense in self:
            if self.env.company.cancel_expenses == 'cancel':
                raise UserError(_("You cannot select Cancel Reset to Draft"))
            if expense.create_uid.id != self.env.user.id:
                raise UserError(_("You can only reset expenses that you created."))
            expense.sheet_id.action_cancel()
            expense.sheet_id.action_reset()

    def action_mass_delete(self):
        for expense in self:
            if self.env.company.cancel_expenses != 'cancel_delete':
                raise UserError(_("Delete operation is not allowed with current settings"))
            if expense.create_uid.id != self.env.user.id:
                raise UserError(_("You can only delete expenses that you created."))
            expense.sheet_id.action_cancel()
            expense.sheet_id.action_reset()
            expense.sheet_id.action_unlink()
