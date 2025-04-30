# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Controller, route
import json

class TestAPI(http.Controller):
    @http.route('/api/test', type='http', auth='none', methods=['GET'], csrf=False)
    def test_endpoint(self, **kwargs):
        response = {
            'status': 'success',
            'message': 'Hello World'
        }
        print(response)
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')]
        )