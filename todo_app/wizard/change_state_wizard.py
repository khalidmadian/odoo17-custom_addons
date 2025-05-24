from odoo import models, fields, api


class ChangeState(models.TransientModel):
    _name = 'change.state'

    task_id = fields.Many2one('todo.task')
    state = fields.Selection([
        ('completed', 'Completed'),
        ('in_progress', 'In Progress')
    ], default='in_progress')

    reason = fields.Char()

    def action_confirm(self):
        if self.task_id.status == 'closed':
            self.task_id.status = self.state
            self.task_id.create_task_move_record('closed', self.state, self.reason)
