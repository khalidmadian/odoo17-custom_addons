from odoo import models, fields, api


class TaskMove(models.Model):
    _name = 'task.move'

    user_id = fields.Many2one('res.users', string='User')
    task_id = fields.Many2one('todo.task', string='Task')
    old_state = fields.Char(string='OLd State')
    new_state = fields.Char(string='New State')
    reason = fields.Char(string='Reason')
    task_line_ids = fields.One2many('task.history.line', 'line_id')

    def action_open_related_task(self):
        action = self.env['ir.actions.actions']._for_xml_id('todo_app.action_todo_task')
        view_id = self.env.ref('todo_app.todo_task_view_form').id
        print(action)
        print(view_id)
        action['views'] = [(view_id, 'form')]
        action['res_id'] = self.task_id.id
        print(action)
        return action


class TaskHistoryLine(models.Model):
    _name = 'task.history.line'

    line_id = fields.Many2one('task.move')
    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    time = fields.Float(string='Time')
