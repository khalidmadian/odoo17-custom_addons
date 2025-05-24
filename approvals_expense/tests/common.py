# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestApprovalsExpenseCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Define an approval category for expenses.
        approval_category_form = Form(cls.env['approval.category'])
        approval_category_form.name = 'Expense Request'
        approval_category_form.approval_type = 'expense'
        cls.expense_category = approval_category_form.save()

        # Create a user to use as an approver.
        cls.user_approver = cls.env['res.users'].create({
            'login': 'yesman',
            'name': 'Carl Allen',
        })

        # Create employees to use in expense requests.
        cls.employee_1 = cls.env['hr.employee'].create({
            'name': 'John Doe',
            'user_id': cls.user_approver.id,
        })
        cls.employee_2 = cls.env['hr.employee'].create({
            'name': 'Jane Smith',
        })

        # Create some products for expenses.
        cls.product_travel = cls.env['product.product'].create({
            'name': 'Travel Expenses',
            'can_be_expensed': True,
        })
        cls.product_meal = cls.env['product.product'].create({
            'name': 'Meal Expenses',
            'can_be_expensed': True,
        })
        cls.product_earphone = cls.env['product.product'].create({
            'name': 'Earphone',
            'can_be_expensed': True,
        })

        # Find UoM unit and create the 'fortnight' unit.
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.uom_fortnight = cls.env['uom.uom'].create({
            'category_id': cls.uom_unit.category_id.id,
            'name': 'Fortnights',
            'uom_type': 'bigger',
            'factor_inv': 15.0,
        })

    def create_request_form(self, approver=False, category=False):
        """Return a new instance of Form for an expense request.

        :param approver: optional record to set an approver directly on the new
            approval request.
        :param category: optional record to choose the category of the new
            approval request. Takes the "Expense Request" by default.
        """
        if not category:
            category = self.expense_category
        create_request_form = Form(self.env['approval.request'].with_user(approver).with_context(
            default_name=self.expense_category.name,
            default_category_id=category.id,
        ))
        if approver:
            # Set an approver.
            with create_request_form.approver_ids.new() as req_approver:
                req_approver.user_id = approver
        return create_request_form

    def create_expense_sheet(self, employee=False, origin=False, lines=False):
        """Create and return a new expense sheet.

        :param record employee: employee used for the expense sheet ('employee_1' by default).
        :param string origin: optional string to define the expense sheet's origin.
        :param list lines: optional list containing dicts to create expense lines.
               Takes the following keys:
                - product: record of the product
                - amount: amount for the expense
                - quantity: 1 by default
                - uom: uom id for the line (product's uom by default)
        """
        vals = {
            'employee_id': (employee and employee.id) or self.employee_1.id,
            'name': origin or 'Expense Sheet',
        }
        # Create expense lines if defined.
        if lines:
            vals['expense_line_ids'] = []
            for line in lines:
                product = line['product']
                expense_line_vals = (0, 0, {
                    'date': fields.Date.today(),
                    'name': product.display_name,
                    'product_id': product.id,
                    'unit_amount': line.get('amount', 0),
                    'quantity': line.get('quantity', 1),
                    'product_uom_id': line.get('uom', product.uom_id.id),
                })
                vals['expense_line_ids'].append(expense_line_vals)

        new_expense_sheet = self.env['hr.expense.sheet'].create(vals)
        return new_expense_sheet

    def get_expense_sheet(self, request, index=0):
        """Retrieve the expense sheet linked to the approval request."""
        expense_sheets = request.expense_line_ids.sheet_id
        return expense_sheets[index]
