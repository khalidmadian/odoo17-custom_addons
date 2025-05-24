import json
from crypt import methods

from odoo import http, _
from odoo.http import request


class TodoTaskApi(http.Controller):
    # Create operation with https type
    @http.route('/v1/todo_task', methods=['POST'], auth='none', type='http', csrf=False)
    def post_todo_task(self):
        try:
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            if not vals.get('name'):
                return request.make_json_response({
                    'error': 'Name Is Required'
                }, status=400)
            res = request.env['todo.task'].sudo().create(vals)
            if res:
                return request.make_json_response({
                    'message': 'Task created successfully',
                    'id': res.id,
                    'name': res.name,
                }, status=200)
            else:
                return None
        except Exception as error:
            return request.make_json_response({
                'message': error,
            }, status=400)

    # create operation with JSON type
    @http.route('/v1/todo_task/json', methods=['POST'], type='json', auth='none', csrf=False)
    def post_todo_task_json(self):
        args = request.httprequest.data.decode()
        vals = json.loads(args)
        res = request.env['todo.task'].sudo().create(vals)
        if res:
            return {
                'message': 'Task created successfully'
            }

    # Update operation
    @http.route('/v1/todo_task/<int:task_id>', methods=['PUT'], auth='none', type='http', csrf=False)
    def update_todo_task(self, task_id):
        try:
            task = request.env['todo.task'].sudo().search([('id', '=', task_id)])
            if not task:
                return request.make_json_response({
                    'error': 'ID not found',
                }, status=404)
            args = request.httprequest.data.decode()
            vals = json.loads(args)
            task.write(vals)
            return request.make_json_response({
                'message': 'Task has been updated successfully',
                'id': task.id,
                'name': task.name,
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                'message': error,
            }, status=400)

    # get operation(single task)
    @http.route('/v1/todo_task/<int:task_id>', methods=['GET'], type='http', auth='none', csrf='False')
    def get_todo_task(self, task_id):
        try:
            task = request.env['todo.task'].sudo().search([('id', '=', task_id)])
            if task:
                return request.make_json_response({
                    'message': 'Task found successfully',
                    'id': task.id,
                    'name': task.name,
                    'description': task.description,
                    'status': task.status,

                }, status=200)
            else:
                return request.make_json_response({
                    'error': 'Task not found',
                }, status=404)

        except Exception as error:
            return request.make_json_response({
                'message': error,
            })

    # Delete(Unlink) operation
    @http.route('/v1/todo_task/<int:task_id>', methos=['DELETE'], auth='none', type='http', csrf=False)
    def delete_task(self, task_id):
        try:
            task = request.env['todo.task'].sudo().search([('id', '=', task_id)])
            if not task:
                return request.make_json_response({
                    'error': 'ID not found',
                }, status=404)
            task.unlink()
            return request.make_json_response({
                'message': 'Task has been deleted successfully',
            }, status=200)
        except Exception as error:
            return request.make_json_response({
                'message': error,
            })

    @http.route('/v1/todo_tasks', methods=['GET'], auth='none', type='http', csrf=False)
    def get_todo_tasks(self):
        try:
            tasks = request.env['todo.task'].sudo().search([])
            if not tasks:
                return request.make_json_response({
                    'error': 'No tasks records found',
                }, status=404)
            return request.make_json_response([{
                'name': task.name,
                'description': task.description,
                'is_late': task.is_late,
                'status': task.status,
            } for task in tasks], status=200)
        except Exception as error:
            return request.make_json_response({
                'message': error,
            })
