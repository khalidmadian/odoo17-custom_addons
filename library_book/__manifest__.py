{
    'name': 'Library Management',
    'version': '1.0',
    'summary': 'Manage library books and authors',
    'description': """
        This module allows you to manage books, authors and book loans
        using self.env extensively
    """,
    'author': 'Your Name',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/book_views.xml',
        'views/author_views.xml',
    ],
    'installable': True,
    'application': True,
}