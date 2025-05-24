# -*- coding: utf-8 -*-
{
    'name': "To-Do App",
    'summary': """""",
    "license": "",
    'description': """""",
    'author': "",
    'website': "",
    'category': '',
    'version': '0.1',

    'depends': ['base', 'mail', 'web'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_view.xml',
        'views/base_menu.xml',
        'views/todo_task_view.xml',
        'views/task_move_view.xml',
        'views/task_history_view.xml',
        'wizard/change_state_wizard_view.xml',
        'reports/todo_task_report.xml',
    ],

    'installable': True,
    'application': True,
}
