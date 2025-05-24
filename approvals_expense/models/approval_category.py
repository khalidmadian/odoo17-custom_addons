# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[('expense', 'Create Expenses')])

    @api.onchange('approval_type')
    def _onchange_approval_type(self):
        if self.approval_type == 'expense':
            self.has_product = 'required'
            self.has_quantity = 'required'
