from email.policy import default
from datetime import date, datetime, timedelta
from os import close

from reportlab.graphics.transform import translate

from odoo import models, fields, api
from odoo.odoo.exceptions import ValidationError
from odoo.odoo.tools.populate import compute


class TodoTask(models.Model):
    _name = 'todo.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(default='New', readonly=1)
    name = fields.Char(string='Name', translate=True)
    due_date = fields.Datetime(string="Due Date", tracking=1)
    is_late = fields.Boolean(string='Is Late')  # , compute='_compute_check_late_tasks', store=True)
    description = fields.Text(string='Description', tracking=1)
    # (tracking=1) to make this fiels display on the chatter
    assign_to = fields.Many2one('res.partner', string='Assign To', tracking=1)
    estimated_time = fields.Float(string='Estimated Time')
    task_line = fields.One2many('task.history', 'task_line_history', string='Task History')
    total_time = fields.Float(string='Total Time', compute='_compute_total_time', store=True)
    active = fields.Boolean(default=True, string='Active')
    current_time = fields.Datetime(default=fields.Datetime.now())
    end_of_limited_assign = fields.Datetime(compute='_compute_end_of_limited_assign')

    status = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed')
    ], default='new', string='Status', tracking=1)

    @api.depends('current_time')
    def _compute_end_of_limited_assign(self):
        for rec in self:
            if rec.current_time:
                rec.end_of_limited_assign = rec.current_time + timedelta(hours=2)
            else:
                rec.end_of_limited_assign = False

    @api.depends('task_line.time')
    def _compute_total_time(self):
        """Calculate the total time from related TaskHistory records."""
        for task in self:
            task.total_time = sum(line.time for line in task.task_line)

    @api.onchange('total_time', 'estimated_time')
    def _check_time_estimation(self):
        """Validate that total_time doesn't exceed estimated_time."""
        for task in self:
            if 0 < task.estimated_time < task.total_time:
                raise ValueError('Total time of tasks more than Estimated time')

    def action_archive(self):
        for record in self:
            record.active = False

    def action_unarchive(self):
        for record in self:
            record.active = True

    def action_closed(self):
        for record in self:
            record.create_task_move_record(record.status, 'closed')
            record.status = 'closed'

    def action_open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('todo_app.change_state_wizard_action')
        action['context'] = {'default_task_id': self.id}
        return action

    def action_state_new(self):
        for record in self:
            record.create_task_move_record(record.status, 'new')
            record.status = 'new'

    def action_state_in_progress(self):
        for record in self:
            record.create_task_move_record(record.status, 'in_progress')
            record.status = 'in_progress'

    def action_state_completed(self):
        for record in self:
            record.create_task_move_record(record.status, 'completed')
            record.status = 'completed'

    def action_create_new_task(self):
        print(self.env['todo.task'].create({
            'name': 'khalid Madian',
            'description': 'JJJJJJJJJJJJJJJJ'
        }))
        print(self.env['todo.task'].search([('name', '=', 'play')]))
        print(self.env.context)
        print(self.env.user.lang)
        print(self.env.user)
        print(self.env.uid)

    # @api.depends('due_date')
    # def _compute_check_late_tasks(self):
    #     for rec in self:
    #         if fields.Datetime.to_datetime(rec.due_date) < fields.Datetime.now():
    #             rec.is_late = True

    @api.model_create_multi
    def create(self, vals):
        res = super(TodoTask, self).create(vals)
        print('In Create Method')
        return res

    print(due_date)

    @api.model
    def create(self, vals):
        res = super(TodoTask, self).create(vals)
        if res.ref == 'New':
            res.ref = res.env['ir.sequence'].next_by_code('task_seq')
        return res

    def create_task_move_record(self, old_state, new_state, reason=''):
        for rec in self:
            rec.env['task.move'].create({
                'user_id': rec.env.uid,
                'task_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or '',
                # 'task_line_ids': [(0, 0, {'description': line.description, 'name': line.name, 'time': line.time}) for
                #                   line in rec.env['task.move'].task_line_ids],
            })
