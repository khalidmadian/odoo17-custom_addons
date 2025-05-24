from odoo import models, fields, api
from datetime import date


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _order = 'publication_date desc, name'

    name = fields.Char(string='Title', required=True)
    isbn = fields.Char(string='ISBN')
    author_id = fields.Many2one('library.author', string='Author')
    publication_date = fields.Date(string='Publication Date')
    pages = fields.Integer(string='Number of Pages')
    available = fields.Boolean(string='Available', default=True)
    reader_id = fields.Many2one('res.partner', string='Borrowed By')
    due_date = fields.Date(string='Due Date')

    @api.model
    def create(self, vals):
        # استخدام self.env للوصول إلى التسجيلات الأخرى قبل الإنشاء
        if 'isbn' in vals:
            existing = self.env['library.book'].search([('isbn', '=', vals['isbn'])])
            if existing:
                raise ValueError("Book with this ISBN already exists!")

        # استخدام self.env للوصول إلى المستخدم الحالي
        if 'reader_id' not in vals:
            default_reader = self.env['res.partner'].search([
                ('is_library_member', '=', True)
            ], limit=1)
            if default_reader:
                vals['reader_id'] = default_reader.id

        return super(LibraryBook, self).create(vals)

    def write(self, vals):
        # استخدام self.env للوصول إلى التسجيلات الأخرى قبل التعديل
        if 'reader_id' in vals and not vals.get('due_date'):
            vals['due_date'] = date.today()
        return super(LibraryBook, self).write(vals)

    def action_borrow_book(self):
        # استخدام self.env لإنشاء سجلات في نموذج آخر
        self.ensure_one()
        if not self.reader_id:
            default_reader = self.env['res.partner'].search([
                ('is_library_member', '=', True)
            ], limit=1)
            if default_reader:
                self.write({
                    'reader_id': default_reader.id,
                    'due_date': date.today(),
                    'available': False
                })
                # إنشاء سجل إعارة جديد
                self.env['library.loan'].create({
                    'book_id': self.id,
                    'reader_id': default_reader.id,
                    'loan_date': date.today(),
                    'due_date': date.today(),
                })

    def action_return_book(self):
        self.write({
            'reader_id': False,
            'due_date': False,
            'available': True
        })

    @api.model
    def check_overdue_books(self):
        # استخدام self.env للبحث في التسجيلات
        overdue_books = self.env['library.book'].search([
            ('due_date', '<', date.today()),
            ('available', '=', False)
        ])

        # استخدام self.env لإرسال بريد إلكتروني
        template = self.env.ref('library_book.email_template_overdue')
        for book in overdue_books:
            template.send_mail(book.id, force_send=True)