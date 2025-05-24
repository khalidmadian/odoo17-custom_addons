from email.policy import default

from odoo import models, fields, api


class TaskHistory(models.Model):
    _name = 'task.history'

    task_line_history = fields.Many2one('todo.task', string='Task History')
    name = fields.Char(string='Name')
    # groups = "todo_app.todo_app_manager_group" ==> only in this group see this you can use with pyhon code and xml code
    description = fields.Text(string='Description', groups="todo_app.todo_app_manager_group")
    time = fields.Float(string='Time')
