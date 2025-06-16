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
    
    def _get_user_partner_record(self, user):
        """Get the partner record associated with the user"""
        try:
            # First try to find partner record by user relationship
            partner = user.partner_id
            if partner:
                return partner
            
            # If no direct partner relationship, try to find by email
            if user.email:
                partner = request.env['res.partner'].sudo().search([
                    ('email', '=', user.email),
                    ('is_company', '=', False)
                ], limit=1)
                if partner:
                    return partner
            
            # If still no partner found, try by login/name
            partner = request.env['res.partner'].sudo().search([
                '|',
                ('login', '=', user.login),
                ('name', '=', user.name),
                ('is_company', '=', False)
            ], limit=1)
            
            return partner
            
        except Exception as e:
            _logger.error(f"Error getting partner record: {str(e)}")
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
                
                # Get the partner record associated with this user
                partner = self._get_user_partner_record(user)
                
                # Generate API token
                api_token = self._generate_api_token(uid)
                
                # Get user context and permissions
                context = self._get_user_context(user, partner)
                
                # Prepare user data - use partner data if available, fallback to user data
                user_data = {
                    'id': user.id,
                    'name': partner.name if partner else user.name,
                    'email': partner.email if partner and partner.email else user.email,
                    'phone': partner.phone if partner and partner.phone else (user.phone if hasattr(user, 'phone') else ''),
                    'avatar': f'/web/image/res.users/{user.id}/image_128'
                }
                
                # Add partner-specific fields if partner exists
                if partner:
                    user_data.update({
                        'partner_id': partner.id,
                        'contact_role': partner.contact_role,
                        'student_id': partner.student_id if partner.contact_role == 'student' else None,
                        'employee_id': partner.employee_id if partner.contact_role in ['employee', 'manager'] else None,
                        'license_number': partner.license_number if partner.contact_role == 'psychologist' else None,
                    })
                
                # Prepare response
                response_data = {
                    'status': 'success',
                    'message': 'Login successful',
                    'data': {
                        'user': user_data,
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
            partner = self._get_user_partner_record(user)
            context = self._get_user_context(user, partner)
            
            # Prepare user data
            user_data = {
                'id': user.id,
                'name': partner.name if partner else user.name,
                'email': partner.email if partner and partner.email else user.email
            }
            
            if partner:
                user_data.update({
                    'partner_id': partner.id,
                    'contact_role': partner.contact_role
                })
            
            # Return session ID as token
            return self._make_json_response({
                'status': 'success',
                'message': 'Session login successful',
                'data': {
                    'user': user_data,
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
            partner = self._get_user_partner_record(user)
            context = self._get_user_context(user, partner)
            
            user_data = {
                'id': user.id,
                'name': partner.name if partner else user.name,
                'email': partner.email if partner and partner.email else user.email
            }
            
            if partner:
                user_data.update({
                    'partner_id': partner.id,
                    'contact_role': partner.contact_role
                })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Token is valid',
                'data': {
                    'user': user_data,
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
    
    def _get_user_context(self, user, partner=None):
        """Get user context including roles and permissions based on contact_role"""
        context = {
            'user_id': user.id,
            'user_name': partner.name if partner else user.name,
            'user_email': partner.email if partner and partner.email else user.email,
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
        
        # If no partner record found, return basic context
        if not partner:
            _logger.warning(f"No partner record found for user {user.login}")
            return context
        
        # Set role flags based on contact_role
        contact_role = partner.contact_role
        if contact_role == 'student':
            context['is_student'] = True
            # Get student's classrooms
            if partner.classroom_ids:
                context['classrooms'] = [{
                    'id': cls.id, 
                    'name': cls.name, 
                    'grade_id': cls.grade_id.id,
                    'grade_name': cls.grade_id.name,
                    'school_id': cls.grade_id.school_id.id,
                    'school_name': cls.grade_id.school_id.name
                } for cls in partner.classroom_ids]
                
                # Get unique grades and schools
                grades = partner.classroom_ids.mapped('grade_id')
                schools = grades.mapped('school_id')
                context['grades'] = [{'id': grade.id, 'name': grade.name} for grade in grades]
                context['schools'] = [{'id': school.id, 'name': school.name} for school in schools]
        
        elif contact_role == 'parent':
            context['is_parent'] = True
            # Get children and their schools/classrooms
            if partner.child_ids:
                children_data = []
                for child in partner.child_ids:
                    child_data = {
                        'id': child.id,
                        'name': child.name,
                        'classrooms': []
                    }
                    if child.classroom_ids:
                        child_data['classrooms'] = [{
                            'id': cls.id,
                            'name': cls.name,
                            'grade_name': cls.grade_id.name,
                            'school_name': cls.grade_id.school_id.name
                        } for cls in child.classroom_ids]
                    children_data.append(child_data)
                context['children'] = children_data
        
        elif contact_role == 'teacher':
            context['is_teacher'] = True
            # Get teacher's assigned classrooms
            assigned_classrooms = request.env['hospital.classroom'].sudo().search([
                ('teacher_id', '=', partner.id)
            ])
            if assigned_classrooms:
                context['classrooms'] = [{
                    'id': cls.id, 
                    'name': cls.name, 
                    'grade_id': cls.grade_id.id,
                    'grade_name': cls.grade_id.name,
                    'school_id': cls.grade_id.school_id.id,
                    'school_name': cls.grade_id.school_id.name,
                    'student_count': cls.student_count
                } for cls in assigned_classrooms]
                
                # Get unique grades and schools
                grades = assigned_classrooms.mapped('grade_id')
                schools = grades.mapped('school_id')
                context['grades'] = [{'id': grade.id, 'name': grade.name} for grade in grades]
                context['schools'] = [{'id': school.id, 'name': school.name} for school in schools]
        
        elif contact_role == 'psychologist':
            context['is_psychologist'] = True
            
            # Get organizations where psychologist is assigned
            organization_assignments = request.env['hospital.hospital'].sudo().search([
                ('psychologist_ids', 'in', partner.id)
            ])
            if organization_assignments:
                context['organizations'] = [{
                    'id': org.id, 
                    'name': org.name,
                    'type': org.type
                } for org in organization_assignments]
            
            # Get grade assignments
            grade_assignments = request.env['hospital.grade'].sudo().search([
                ('psychologist_ids', 'in', partner.id)
            ])
            if grade_assignments:
                context['grades'] = [{
                    'id': grade.id, 
                    'name': grade.name, 
                    'school_id': grade.school_id.id,
                    'school_name': grade.school_id.name
                } for grade in grade_assignments]
            
            # Get classroom assignments
            classroom_assignments = request.env['hospital.classroom'].sudo().search([
                ('psychologist_ids', 'in', partner.id)
            ])
            if classroom_assignments:
                context['classrooms'] = [{
                    'id': cls.id, 
                    'name': cls.name, 
                    'grade_id': cls.grade_id.id,
                    'grade_name': cls.grade_id.name,
                    'school_id': cls.grade_id.school_id.id,
                    'school_name': cls.grade_id.school_id.name,
                    'student_count': cls.student_count
                } for cls in classroom_assignments]
        
        # Get institution associations for any role
        if partner.institution_ids:
            institutions = [{
                'id': inst.id,
                'name': inst.name,
                'type': inst.type
            } for inst in partner.institution_ids]
            if 'organizations' not in context or not context['organizations']:
                context['organizations'] = institutions
            else:
                # Merge with existing organizations, avoiding duplicates
                existing_ids = [org['id'] for org in context['organizations']]
                for inst in institutions:
                    if inst['id'] not in existing_ids:
                        context['organizations'].append(inst)
        
        return context