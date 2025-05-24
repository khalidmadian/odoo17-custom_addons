from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    expense_count = fields.Integer(compute='_compute_expense_count')

    @api.depends('product_line_ids.expense_line_id')
    def _compute_expense_count(self):
        for request in self:
            request.expense_count = len(request.product_line_ids.mapped('expense_line_id'))

    def action_approve(self, approver=None):
        if self.approval_type == 'expense' and any(not line.product_id for line in self.product_line_ids):
            raise UserError(_("You must select a product for each line of requested expenses."))
        return super().action_approve(approver)

    def action_confirm(self):
        for request in self:
            if request.approval_type == 'expense' and not request.product_line_ids:
                raise UserError(_("You cannot create an empty expense request."))
        return super().action_confirm()

    def action_create_expense_sheets(self):
        """ Create and/or modify Expenses. """
        self.ensure_one()
        self.product_line_ids._check_products_account()

        for line in self.product_line_ids:
            expense_vals = {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'price_unit': line.product_id.standard_price,
                'quantity': line.quantity,
                'employee_id': self.env.user.employee_id.id,
                'company_id': self.company_id.id,
            }
            expense = self.env['hr.expense'].create(expense_vals)
            line.expense_line_id = expense.id

    def action_open_expenses(self):
        """ Return the list of expenses the approval request created. """
        self.ensure_one()
        expense_ids = self.product_line_ids.mapped('expense_line_id').ids
        domain = [('id', 'in', expense_ids)]
        action = {
            'name': _('Expenses'),
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'type': 'ir.actions.act_window',
            'domain': domain,
        }
        return action
