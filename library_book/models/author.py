from odoo import models, fields, api

class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Library Author'

    name = fields.Char(string='Name', required=True)
    birth_date = fields.Date(string='Birth Date')
    book_ids = fields.One2many('library.book', 'author_id', string='Books')
    books_count = fields.Integer(string='Number of Books', compute='_compute_books_count')

    @api.depends('book_ids')
    def _compute_books_count(self):
        # استخدام self.env للوصول إلى بيانات أخرى
        for author in self:
            author.books_count = self.env['library.book'].search_count([
                ('author_id', '=', author.id)
            ])

    def action_view_books(self):
        # استخدام self.env للوصول إلى views
        action = self.env['ir.actions.act_window']._for_xml_id('library_book.library_book_action')
        action['domain'] = [('author_id', '=', self.id)]
        return action