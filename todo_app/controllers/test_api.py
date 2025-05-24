from odoo import http,_


class TestAPI(http.Controller):
    @http.route("/test/api", methods=["GET"], type='http', auth='none', csrf=False)
    def test_endpoint(self):
        print("test_api")
