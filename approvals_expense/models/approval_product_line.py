from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    expense_line_id = fields.Many2one('hr.expense', string="Expense Line")

    def _check_products_account(self):
        """ Raise an error if at least one product does not have an expense account. """
        product_lines_without_account = self.filtered(lambda line: not line.product_id.property_account_expense_id)
        if product_lines_without_account:
            product_names = product_lines_without_account.product_id.mapped('display_name')
            raise UserError(
                _('Please set an expense account on product(s) %s.', ', '.join(product_names))
            )
