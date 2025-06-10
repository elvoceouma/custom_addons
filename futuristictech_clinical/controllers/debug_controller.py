# -*- coding: utf-8 -*-

import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class DebugAPIController(http.Controller):
    
    def _make_json_response(self, data, status=200):
        """Helper method to create JSON responses"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            ],
            status=status
        )

    @http.route('/api/test/simple', type='http', auth='none', methods=['GET'], csrf=False)
    def simple_test(self, **kwargs):
        """Simple test endpoint to verify API is working"""
        return self._make_json_response({
            'status': 'success',
            'message': 'API is working!',
            'timestamp': '2025-06-09 14:45:00',
            'data': {
                'endpoint': '/api/test/simple',
                'method': 'GET',
                'working': True
            }
        })

    @http.route('/api/auth/login/simple', type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def simple_login_test(self, **kwargs):
        """Simple login test"""
        try:
            method = request.httprequest.method
            
            if method == 'GET':
                return self._make_json_response({
                    'status': 'info',
                    'message': 'Login endpoint is accessible. Use POST to login.',
                    'method': method
                })
            
            # Handle POST request
            login = kwargs.get('login')
            password = kwargs.get('password')
            
            _logger.info(f"Login attempt - Email: {login}, Password: {'*' * len(password) if password else None}")
            
            if not login or not password:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Both login and password are required',
                    'received_params': list(kwargs.keys())
                }, 400)
            
            # Try to authenticate
            try:
                # Get database name
                db = request.session.db or request.db
                _logger.info(f"Using database: {db}")
                
                # Attempt authentication
                uid = request.session.authenticate(db, login, password)
                
                if uid:
                    user = request.env['res.users'].sudo().browse(uid)
                    return self._make_json_response({
                        'status': 'success',
                        'message': 'Authentication successful',
                        'data': {
                            'user_id': uid,
                            'user_name': user.name,
                            'user_email': user.email,
                            'session_id': request.session.sid,
                            'database': db
                        }
                    })
                else:
                    return self._make_json_response({
                        'status': 'error',
                        'message': 'Invalid credentials',
                        'login_attempted': login
                    }, 401)
                    
            except Exception as auth_error:
                _logger.error(f"Authentication error: {str(auth_error)}")
                return self._make_json_response({
                    'status': 'error',
                    'message': f'Authentication failed: {str(auth_error)}',
                    'login_attempted': login
                }, 500)
                
        except Exception as e:
            _logger.error(f"Login endpoint error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }, 500)

    @http.route('/api/debug/info', type='http', auth='none', methods=['GET'], csrf=False)
    def debug_info(self, **kwargs):
        """Debug information endpoint"""
        try:
            return self._make_json_response({
                'status': 'success',
                'message': 'Debug info',
                'data': {
                    'odoo_version': '17.0',
                    'database': request.session.db or request.db,
                    'session_uid': request.session.uid,
                    'is_authenticated': bool(request.session.uid),
                    'available_endpoints': [
                        '/api/test/simple',
                        '/api/auth/login/simple',
                        '/api/debug/info'
                    ],
                    'request_info': {
                        'method': request.httprequest.method,
                        'path': request.httprequest.path,
                        'remote_addr': request.httprequest.remote_addr,
                        'user_agent': request.httprequest.headers.get('User-Agent', '')[:100]
                    }
                }
            })
        except Exception as e:
            _logger.error(f"Debug info error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)