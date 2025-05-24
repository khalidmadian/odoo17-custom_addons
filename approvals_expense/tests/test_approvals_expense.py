# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from odoo.addons.approvals_expense.tests.common import TestApprovalsCommon
from odoo.exceptions import UserError
from odoo.tests.common import Form


class TestApprovalsExpense(TestApprovalsCommon):

    def get_expense_sheet_for_employee(self, employee):
        """Helper method to get expense sheets for a specific employee."""
        return self.env['expense.sheet'].search([
            ('employee_id', '=', employee.id)
        ])

    def test_01_create_expense_request(self):
        """Creates a new expense request and verifies all fields are correctly set."""
        request_form = self.create_request_form()
        request_expense = request_form.save()

        self.assertEqual(request_expense.has_product, 'required')
        self.assertEqual(request_expense.has_quantity, 'required',
                         "An expense request must have `has_quantity` forced on 'required'.")
        self.assertEqual(request_expense.has_product, 'required',
                         "An expense request must have `has_product` forced on 'required'.")

    def test_02_check_constrains(self):
        """Checks all constraints are respected and all errors are raised."""
        # Create a new expense request and save it.
        request_form = self.create_request_form(approver=self.user_approver)
        request_expense = request_form.save()

        # Try to submit it without any expense lines -> must raise a UserError.
        with self.assertRaises(UserError):
            request_expense.action_confirm()

        # Add new expense lines, they require a description but an onchange will fill the
        # description automatically if we set the product id.
        request_form = Form(request_expense)
        with request_form.expense_line_ids.new() as line:
            line.product_id = self.product_travel
            line.quantity = 1
            line.amount = 500
        with request_form.expense_line_ids.new() as line:
            line.description = "Team lunch meeting"
            line.quantity = 1
            line.amount = 200
        # Try to validate, should be OK now.
        request_expense = request_form.save()
        request_expense.action_confirm()
        self.assertEqual(request_expense.request_status, 'pending')

        # Try to approve it...
        with self.assertRaises(UserError):
            # ... but raise an error because all expense lines need a product_id.
            request_expense.action_approve()

        # Edit the line without product id then try to approve it again.
        request_expense.action_draft()
        request_form = Form(request_expense)
        with request_form.expense_line_ids.edit(1) as line:
            line.product_id = self.product_meal
        request_expense = request_form.save()
        request_expense.with_user(self.user_approver).action_approve()
        # ... should be approved now.
        self.assertEqual(request_expense.request_status, 'approved')

        # Try to generate an expense sheet from the request...
        with self.assertRaises(UserError):
            # ... but must fail because the expense lines are not properly configured.
            request_expense.action_create_expense_sheets()
        self.assertEqual(request_expense.expense_sheet_count, 0)

        # Edit the expense lines to ensure they are valid, then try again.
        request_expense.action_draft()
        request_form = Form(request_expense)
        with request_form.expense_line_ids.edit(0) as line:
            line.amount = 500
        with request_form.expense_line_ids.edit(1) as line:
            line.amount = 200
        request_expense = request_form.save()
        request_expense.action_confirm()
        request_expense.with_user(self.user_approver).action_approve()
        request_expense.action_create_expense_sheets()
        self.assertEqual(request_expense.expense_sheet_count, 1)

    def test_expense_01_check_create_expense(self):
        """Checks an approval expense request will create a new expense sheet
        and verifies the expense sheet is correctly set."""
        # Checks we have no expense sheets for the employees.
        expense_for_employee_1 = self.get_expense_sheet_for_employee(self.employee_1)
        expense_for_employee_2 = self.get_expense_sheet_for_employee(self.employee_2)
        self.assertEqual(len(expense_for_employee_1), 0)
        self.assertEqual(len(expense_for_employee_2), 0)

        # Create a new expense request for travel expenses.
        request_form = self.create_request_form(approver=self.user_approver)
        with request_form.expense_line_ids.new() as line:
            line.product_id = self.product_travel
            line.quantity = 1
            line.amount = 500
        request_expense = request_form.save()
        request_expense.action_confirm()
        request_expense.with_user(self.user_approver).action_approve()
        request_expense.action_create_expense_sheets()

        # Check we have an expense sheet and if it is correctly set.
        self.assertEqual(request_expense.expense_sheet_count, 1)
        expense_sheet = self.get_expense_sheet(request_expense, 0)
        self.assertEqual(expense_sheet.employee_id.id, self.employee_1.id)
        self.assertEqual(len(expense_sheet.expense_line_ids), 1)
        self.assertEqual(expense_sheet.origin, request_expense.name)
        # Check the expense line fields.
        expense_line = expense_sheet.expense_line_ids[0]
        self.assertEqual(expense_line.product_qty, 1)
        self.assertEqual(expense_line.amount, 500)

    def test_expense_02_add_expense_line(self):
        """Checks we don't create a new expense sheet but modify the existing one,
        adding a new expense line if needed."""
        # Create an expense sheet for employee_1 without expense lines.
        expense_sheet = self.create_expense_sheet(employee=self.employee_1)

        # Create a new expense request that will update the expense sheet and
        # add a new expense line.
        request_form = self.create_request_form(approver=self.user_approver)
        with request_form.expense_line_ids.new() as line:
            line.product_id = self.product_travel
            line.quantity = 1
            line.amount = 500
        request_expense = request_form.save()
        request_expense.action_confirm()
        request_expense.with_user(self.user_approver).action_approve()
        request_expense.action_create_expense_sheets()

        # Check we have an expense sheet and if it is correctly set.
        self.assertEqual(request_expense.expense_sheet_count, 1)
        request_expense_sheet = self.get_expense_sheet(request_expense, 0)
        self.assertEqual(
            request_expense_sheet.id, expense_sheet.id,
            "The expense sheet linked to the request must be the existing one."
        )
        self.assertEqual(len(expense_sheet.expense_line_ids), 1)
        # Check the expense line fields.
        expense_line = expense_sheet.expense_line_ids[0]
        self.assertEqual(expense_line.product_qty, 1)
        self.assertEqual(expense_line.amount, 500)

    def test_expense_03_edit_expense_line(self):
        """Checks we don't create a new expense sheet but modify the existing one,
        updating the amount of the existing expense line."""
        # Create an expense sheet for employee_1 with an expense line.
        expense_sheet = self.create_expense_sheet(
            employee=self.employee_1,
            lines=[{
                'product': self.product_travel,
                'amount': 500,
                'quantity': 1,
            }]
        )

        # Create a new expense request that will update the expense sheet and
        # modify the amount of its expense line.
        request_form = self.create_request_form(approver=self.user_approver)
        with request_form.expense_line_ids.new() as line:
            line.product_id = self.product_travel
            line.quantity = 1
            line.amount = 600
        request_expense = request_form.save()
        request_expense.action_confirm()
        request_expense.with_user(self.user_approver).action_approve()
        request_expense.action_create_expense_sheets()

        # Check we have an expense sheet and if it is correctly set.
        self.assertEqual(request_expense.expense_sheet_count, 1)
        request_expense_sheet = self.get_expense_sheet(request_expense, 0)
        self.assertEqual(
            request_expense_sheet.id, expense_sheet.id,
            "The expense sheet linked to the request must be the existing one."
        )
        self.assertEqual(len(expense_sheet.expense_line_ids), 1)
        # Check the expense line fields.
        expense_line = expense_sheet.expense_line_ids[0]
        self.assertEqual(expense_line.product_qty, 1)
        self.assertEqual(expense_line.amount, 600)

    def test_expense_04_create_multiple_expense_sheets(self):
        """Checks expense approval requests with multiple expense lines will,
        depending on how they are set, create expense sheets or add expense lines."""
        # Create an expense sheet for employee_1 with an expense line.
        expense_sheet_1 = self.create_expense_sheet(
            employee=self.employee_1,
            lines=[{
                'product': self.product_travel,
                'amount': 500,
                'quantity': 1,
            }]
        )

        # Create and edit an approval request.
        request_form = self.create_request_form(approver=self.user_approver)
        with request_form.expense_line_ids.new() as line:
            line.product_id = self.product_travel
            line.quantity = 1
            line.amount = 600
        with request_form.expense_line_ids.new() as line:
            line.product_id = self.product_meal
            line.quantity = 1
            line.amount = 200
        # Confirm, approve, and ask to create expense sheets.
        request_expense = request_form.save()
        request_expense.action_confirm()
        request_expense.with_user(self.user_approver).action_approve()
        request_expense.action_create_expense_sheets()

        self.assertEqual(
            request_expense.expense_sheet_count, 2,
            "Must have two expense sheets linked to the approval request."
        )
        request_expense_sheet_1 = self.get_expense_sheet(request_expense, 0)
        self.assertEqual(
            request_expense_sheet_1.id, expense_sheet_1.id,
            "The first expense sheet must be the already existing one."
        )
        self.assertEqual(len(expense_sheet_1.expense_line_ids), 2)
        self.assertEqual(
            expense_sheet_1.expense_line_ids[0].product_id.id, self.product_travel.id
        )
        self.assertEqual(expense_sheet_1.expense_line_ids[0].amount, 500)
        self.assertEqual(
            expense_sheet_1.expense_line_ids[1].product_id.id, self.product_meal.id
        )
        self.assertEqual(expense_sheet_1.expense_line_ids[1].amount, 200)

        request_expense_sheet_2 = self.get_expense_sheet(request_expense, 1)
        self.assertEqual(
            request_expense_sheet_2.employee_id.id, self.employee_2.id,
            "The second expense sheet must be created for the correct employee."
        )
        self.assertEqual(len(request_expense_sheet_2.expense_line_ids), 1)
        self.assertEqual(
            request_expense_sheet_2.expense_line_ids[0].product_id.id, self.product_meal.id
        )
        self.assertEqual(request_expense_sheet_2.expense_line_ids[0].amount, 200)
