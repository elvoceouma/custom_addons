# -*- coding: utf-8 -*-

import json
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from odoo import http, fields, api
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
import werkzeug.utils

_logger = logging.getLogger(__name__)

class APIAuthController(http.Controller):
    
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
    
    def _generate_api_token(self, user_id):
        """Generate a secure API token for the user"""
        # Generate a random token
        token = secrets.token_urlsafe(32)
        
        # Create token record (you might want to create a dedicated model for this)
        # For now, we'll use a simple approach with user's private data
        token_data = {
            'token': token,
            'user_id': user_id,
            'created_at': fields.Datetime.now(),
            'expires_at': fields.Datetime.now() + timedelta(days=30),  # 30 day expiry
            'is_active': True
        }
        
        # Store token in user's private context or create a separate model
        # For demo purposes, we'll return the token directly
        # In production, store this securely in database
        
        return token
    
    def _validate_api_token(self, token):
        """Validate API token and return user"""
        if not token:
            return None
            
        try:
            # In production, validate against stored tokens in database
            # For demo, we'll use a simple approach
            # You should implement proper token validation with expiry checks
            
            # Try to authenticate with session
            if token.startswith('session_'):
                session_id = token.replace('session_', '')
                # Validate session exists and get user
                return None  # Implement session validation
            
            # For bearer tokens, implement your validation logic
            return None
            
        except Exception as e:
            _logger.error(f"Token validation error: {str(e)}")
            return None
    
    @http.route('/api/auth/login', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    def api_login(self, **kwargs):
        """API Login endpoint - authenticate and get token"""
        try:
            # Handle OPTIONS request for CORS
            if request.httprequest.method == 'OPTIONS':
                return self._make_json_response({'message': 'OK'})
            
            # Get login credentials
            login = kwargs.get('login') or kwargs.get('email')
            password = kwargs.get('password')
            
            if not login or not password:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Email and password are required',
                    'data': None
                }, 400)
            
            # Authenticate user using Odoo's authentication
            try:
                uid = request.session.authenticate(request.session.db, login, password)
                if not uid:
                    return self._make_json_response({
                        'status': 'error',
                        'message': 'Invalid email or password',
                        'data': None
                    }, 401)
                
                # Get user information
                user = request.env['res.users'].sudo().browse(uid)
                if not user.exists():
                    return self._make_json_response({
                        'status': 'error',
                        'message': 'User not found',
                        'data': None
                    }, 404)
                
                # Generate API token
                api_token = self._generate_api_token(uid)
                
                # Get user context and permissions
                context = self._get_user_context(user)
                
                # Prepare response
                response_data = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'user': {
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'phone': user.phone or '',
                            'avatar': f'/web/image/res.users/{user.id}/image_128'
                        },
                        'authentication': {
                            'api_token': api_token,
                            'session_id': request.session.sid,
                            'expires_at': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S'),
                            'token_type': 'Bearer'
                        },
                        'permissions': context,
                        'session_info': {
                            'is_authenticated': True,
                            'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                }
                
                return self._make_json_response(response_data)
                
            except Exception as auth_error:
                _logger.error(f"Authentication error: {str(auth_error)}")
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Authentication failed',
                    'data': None
                }, 401)
                
        except Exception as e:
            _logger.error(f"API login error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': 'Internal server error',
                'data': None
            }, 500)
    
    @http.route('/api/auth/session-login', type='http', auth='none', methods=['POST'], csrf=False)
    def api_session_login(self, **kwargs):
        """Alternative login that returns session-based token"""
        try:
            login = kwargs.get('login') or kwargs.get('email')
            password = kwargs.get('password')
            
            if not login or not password:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Email and password are required',
                    'data': None
                }, 400)
            
            # Authenticate and create session
            uid = request.session.authenticate(request.session.db, login, password)
            if not uid:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Invalid credentials',
                    'data': None
                }, 401)
            
            user = request.env['res.users'].browse(uid)
            context = self._get_user_context(user)
            
            # Return session ID as token
            return self._make_json_response({
                'status': 'success',
                'message': 'Session login successful',
                'data': {
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email
                    },
                    'session_token': f"session_{request.session.sid}",
                    'session_id': request.session.sid,
                    'permissions': context
                }
            })
            
        except Exception as e:
            _logger.error(f"Session login error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)
    
    @http.route('/api/auth/logout', type='http', auth='user', methods=['POST'], csrf=False)
    def api_logout(self, **kwargs):
        """API Logout endpoint"""
        try:
            # Clear session
            request.session.logout()
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Logout successful',
                'data': {
                    'logged_out_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Exception as e:
            _logger.error(f"API logout error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)
    
    @http.route('/api/auth/verify', type='http', auth='user', methods=['GET'], csrf=False)
    def verify_token(self, **kwargs):
        """Verify if current session/token is valid"""
        try:
            user = request.env.user
            context = self._get_user_context(user)
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Token is valid',
                'data': {
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email
                    },
                    'session_id': request.session.sid,
                    'permissions': context,
                    'verified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Exception as e:
            _logger.error(f"Token verification error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': 'Invalid or expired token',
                'data': None
            }, 401)
    
    def _get_user_context(self, user):
        """Get user context including roles and permissions"""
        context = {
            'user_id': user.id,
            'user_name': user.name,
            'user_email': user.email,
            'is_student': False,
            'is_parent': False,
            'is_teacher': False,
            'is_psychologist': False,
            'is_admin': user.has_group('base.group_system'),
            'organizations': [],
            'schools': [],
            'grades': [],
            'classrooms': []
        }
        
        # Check if user is a psychologist
        psychologist_assignments = request.env['hospital.hospital'].sudo().search([
            ('psychologist_ids', 'in', user.id)
        ])
        if psychologist_assignments:
            context['is_psychologist'] = True
            context['organizations'] = [{'id': org.id, 'name': org.name} for org in psychologist_assignments]
        
        # Check if user is assigned to any grades
        grade_assignments = request.env['hospital.grade'].sudo().search([
            ('psychologist_ids', 'in', user.id)
        ])
        if grade_assignments:
            context['grades'] = [{'id': grade.id, 'name': grade.name, 'school_id': grade.school_id.id} for grade in grade_assignments]
        
        # Check if user is assigned to any classrooms
        classroom_assignments = request.env['hospital.classroom'].sudo().search([
            ('psychologist_ids', 'in', user.id)
        ])
        if classroom_assignments:
            context['classrooms'] = [{'id': cls.id, 'name': cls.name, 'grade_id': cls.grade_id.id} for cls in classroom_assignments]
        
        return context