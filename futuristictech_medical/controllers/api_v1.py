# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import json
import random
import logging
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
import secrets
import hashlib
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, AccessDenied, UserError


class SimplifiedAuthenticationAPI(http.Controller):
    
    def _make_json_response(self, data, status=200):
        """Helper method to create standardized JSON responses"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Token'),
                ('Access-Control-Allow-Credentials', 'true')
            ],
            status=status
        )

    def _generate_api_token(self, user_id):
        """Generate a secure API token for the user"""
        # Create a unique token using user ID, timestamp, and random data
        timestamp = str(int(datetime.now().timestamp()))
        random_data = secrets.token_hex(16)
        token_data = f"{user_id}:{timestamp}:{random_data}"
        
        # Hash the token data
        api_token = hashlib.sha256(token_data.encode()).hexdigest()
        
        # Store token in user's context or a separate model (optional)
        # For now, we'll return the token directly
        return api_token

    def _get_user_context(self, user):
        """Get user permissions and context information"""
        try:
            # Get user groups and permissions
            groups = user.groups_id.mapped('name')
            
            # Check if user has specific roles
            is_admin = user.has_group('base.group_system')
            is_manager = user.has_group('base.group_user')
            
            # Get company information
            company_info = {
                'id': user.company_id.id if user.company_id else None,
                'name': user.company_id.name if user.company_id else '',
                'currency': user.company_id.currency_id.name if user.company_id and user.company_id.currency_id else 'USD'
            }
            
            return {
                'groups': groups,
                'is_admin': is_admin,
                'is_manager': is_manager,
                'company': company_info,
                'timezone': user.tz or 'UTC',
                'language': user.lang or 'en_US'
            }
        except Exception as e:
            _logger.error(f"Error getting user context: {str(e)}")
            return {}

    def _validate_api_token(self, token):
        """Validate API token and return user ID if valid"""
        try:
            # In a production environment, you might want to store tokens
            # in a database table with expiration times
            # For now, we'll do basic validation
            if not token or len(token) != 64:  # SHA256 hex is 64 characters
                return False
            return True
        except Exception as e:
            _logger.error(f"Token validation error: {str(e)}")
            return False

    @http.route('/api/test', type='http', auth='none', methods=['GET'], csrf=False)
    def test_connection(self, **kwargs):
        """Test API connectivity"""
        return self._make_json_response({
            'status': 'success',
            'message': 'API connection successful',
            'data': {
                'server': 'Mental Health API v2.0',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'endpoints': [
                    '/api/auth/login',
                    '/api/auth/register', 
                    '/api/auth/logout',
                    '/api/auth/profile'
                ]
            }
        })

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
                            'avatar': f'/web/image/res.users/{user.id}/image_128',
                            'active': user.active,
                            'last_login': user.login_date.strftime('%Y-%m-%d %H:%M:%S') if user.login_date else None
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
                            'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'ip_address': request.httprequest.remote_addr
                        }
                    }
                }
                
                # Log successful login
                _logger.info(f"Successful login for user: {user.email} (ID: {user.id})")
                
                return self._make_json_response(response_data)
                
            except AccessDenied:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Invalid email or password',
                    'data': None
                }, 401)
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

    @http.route('/api/auth/register', type='http', auth='none', methods=['POST', 'OPTIONS'], csrf=False)
    def api_register(self, **kwargs):
        """API Registration endpoint - create new user account"""
        try:
            # Handle OPTIONS request for CORS
            if request.httprequest.method == 'OPTIONS':
                return self._make_json_response({'message': 'OK'})
            
            # Get registration data
            name = kwargs.get('name', '').strip()
            email = kwargs.get('email', '').strip()
            password = kwargs.get('password', '').strip()
            phone = kwargs.get('phone', '').strip()
            
            # Validate required fields
            if not name or not email or not password:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Name, email, and password are required',
                    'data': None
                }, 400)
            
            # Validate email format
            if '@' not in email or '.' not in email:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Invalid email format',
                    'data': None
                }, 400)
            
            # Validate password strength
            if len(password) < 6:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Password must be at least 6 characters long',
                    'data': None
                }, 400)
            
            # Check if user already exists
            existing_user = request.env['res.users'].sudo().search([
                ('email', '=', email)
            ], limit=1)
            
            if existing_user:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'User with this email already exists',
                    'data': None
                }, 409)
            
            # Create new user
            try:
                user_vals = {
                    'name': name,
                    'login': email,
                    'email': email,
                    'password': password,
                    'phone': phone,
                    'active': True,
                    'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])]  # Portal user by default
                }
                
                new_user = request.env['res.users'].sudo().create(user_vals)
                
                # Generate API token for the new user
                api_token = self._generate_api_token(new_user.id)
                
                # Authenticate the new user
                uid = request.session.authenticate(request.session.db, email, password)
                
                if uid:
                    context = self._get_user_context(new_user)
                    
                    response_data = {
                        'status': 'success',
                        'message': 'Registration successful',
                        'data': {
                            'user': {
                                'id': new_user.id,
                                'name': new_user.name,
                                'email': new_user.email,
                                'phone': new_user.phone or '',
                                'avatar': f'/web/image/res.users/{new_user.id}/image_128',
                                'active': new_user.active
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
                                'registration_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                        }
                    }
                    
                    # Log successful registration
                    _logger.info(f"New user registered: {email} (ID: {new_user.id})")
                    
                    return self._make_json_response(response_data, 201)
                else:
                    return self._make_json_response({
                        'status': 'error',
                        'message': 'Registration successful but authentication failed',
                        'data': None
                    }, 500)
                    
            except ValidationError as ve:
                return self._make_json_response({
                    'status': 'error',
                    'message': f'Validation error: {str(ve)}',
                    'data': None
                }, 400)
            except Exception as create_error:
                _logger.error(f"User creation error: {str(create_error)}")
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Failed to create user account',
                    'data': None
                }, 500)
                
        except Exception as e:
            _logger.error(f"API registration error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': 'Internal server error',
                'data': None
            }, 500)

    @http.route('/api/auth/profile', type='http', auth='user', methods=['GET', 'PUT', 'OPTIONS'], csrf=False)
    def api_profile(self, **kwargs):
        """Get or update user profile"""
        try:
            # Handle OPTIONS request for CORS
            if request.httprequest.method == 'OPTIONS':
                return self._make_json_response({'message': 'OK'})
            
            user = request.env.user
            
            if request.httprequest.method == 'GET':
                # Get user profile
                context = self._get_user_context(user)
                
                profile_data = {
                    'status': 'success',
                    'message': 'Profile retrieved successfully',
                    'data': {
                        'user': {
                            'id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'phone': user.phone or '',
                            'avatar': f'/web/image/res.users/{user.id}/image_128',
                            'active': user.active,
                            'last_login': user.login_date.strftime('%Y-%m-%d %H:%M:%S') if user.login_date else None,
                            'created_on': user.create_date.strftime('%Y-%m-%d %H:%M:%S') if user.create_date else None
                        },
                        'permissions': context,
                        'preferences': {
                            'timezone': user.tz or 'UTC',
                            'language': user.lang or 'en_US'
                        }
                    }
                }
                
                return self._make_json_response(profile_data)
            
            elif request.httprequest.method == 'PUT':
                # Update user profile
                update_vals = {}
                
                if kwargs.get('name'):
                    update_vals['name'] = kwargs.get('name').strip()
                
                if kwargs.get('phone'):
                    update_vals['phone'] = kwargs.get('phone').strip()
                
                if kwargs.get('timezone'):
                    update_vals['tz'] = kwargs.get('timezone')
                
                if kwargs.get('language'):
                    update_vals['lang'] = kwargs.get('language')
                
                if update_vals:
                    user.sudo().write(update_vals)
                    
                    return self._make_json_response({
                        'status': 'success',
                        'message': 'Profile updated successfully',
                        'data': {
                            'updated_fields': list(update_vals.keys()),
                            'user': {
                                'id': user.id,
                                'name': user.name,
                                'email': user.email,
                                'phone': user.phone or '',
                                'timezone': user.tz or 'UTC',
                                'language': user.lang or 'en_US'
                            }
                        }
                    })
                else:
                    return self._make_json_response({
                        'status': 'error',
                        'message': 'No valid fields provided for update',
                        'data': None
                    }, 400)
                    
        except Exception as e:
            _logger.error(f"API profile error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': 'Internal server error',
                'data': None
            }, 500)

    @http.route('/api/auth/logout', type='http', auth='user', methods=['POST', 'OPTIONS'], csrf=False)
    def api_logout(self, **kwargs):
        """Logout user and invalidate session"""
        try:
            # Handle OPTIONS request for CORS
            if request.httprequest.method == 'OPTIONS':
                return self._make_json_response({'message': 'OK'})
            
            user_email = request.env.user.email
            user_id = request.env.user.id
            
            # Destroy the session
            request.session.logout()
            
            # Log successful logout
            _logger.info(f"User logged out: {user_email} (ID: {user_id})")
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Logout successful',
                'data': {
                    'logged_out_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'session_terminated': True
                }
            })
            
        except Exception as e:
            _logger.error(f"API logout error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': 'Internal server error',
                'data': None
            }, 500)

    @http.route('/api/auth/change-password', type='http', auth='user', methods=['POST', 'OPTIONS'], csrf=False)
    def api_change_password(self, **kwargs):
        """Change user password"""
        try:
            # Handle OPTIONS request for CORS
            if request.httprequest.method == 'OPTIONS':
                return self._make_json_response({'message': 'OK'})
            
            user = request.env.user
            current_password = kwargs.get('current_password', '').strip()
            new_password = kwargs.get('new_password', '').strip()
            
            if not current_password or not new_password:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Current password and new password are required',
                    'data': None
                }, 400)
            
            # Validate new password strength
            if len(new_password) < 6:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'New password must be at least 6 characters long',
                    'data': None
                }, 400)
            
            # Verify current password
            try:
                uid = request.session.authenticate(request.session.db, user.login, current_password)
                if not uid:
                    return self._make_json_response({
                        'status': 'error',
                        'message': 'Current password is incorrect',
                        'data': None
                    }, 401)
            except Exception:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Current password is incorrect',
                    'data': None
                }, 401)
            
            # Update password
            try:
                user.sudo().write({'password': new_password})
                
                # Log password change
                _logger.info(f"Password changed for user: {user.email} (ID: {user.id})")
                
                return self._make_json_response({
                    'status': 'success',
                    'message': 'Password changed successfully',
                    'data': {
                        'changed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
                
            except Exception as e:
                _logger.error(f"Password change error: {str(e)}")
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Failed to change password',
                    'data': None
                }, 500)
                
        except Exception as e:
            _logger.error(f"API change password error: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': 'Internal server error',
                'data': None
            }, 500)

class AppointmentsAPI(http.Controller):
    
    def _make_response(self, data, status=200):
        """Helper method to create standardized JSON responses"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            ],
            status=status
        )

    def _success_response(self, data=None, message="Success"):
        """Standard success response format"""
        response = {
            'success': True,
            'message': message,
            'data': data or {}
        }
        return self._make_response(response)

    def _error_response(self, message="Error", status=400, error_code=None):
        """Standard error response format"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code,
            'data': None
        }
        return self._make_response(response, status)

    def _serialize_appointment(self, appointment):
        """Serialize appointment object to dictionary"""
        return {
            'id': appointment.id,
            'reference': appointment.name,
            'status': appointment.availability,
            'appointment_date': appointment.start_datetime.strftime('%Y-%m-%d') if appointment.start_datetime else None,
            'appointment_time': appointment.start_datetime.strftime('%H:%M') if appointment.start_datetime else None,
            'start_datetime': appointment.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if appointment.start_datetime else None,
            'end_datetime': appointment.stop_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if appointment.stop_datetime else None,
            'duration': appointment.duration or 0,
            'consultation_type': appointment.consultation_type,
            'payment_mode': appointment.payment_mode,
            'amount': appointment.amount or 0.0,
            'free_screening': appointment.free_screening,
            'notes': appointment.notes or '',
            
            # Patient/Lead information
            'patient': {
                'id': appointment.lead_id.id if appointment.lead_id else None,
                'name': appointment.patient_name or '',
                'caller_name': appointment.caller_name or '',
                'mobile': appointment.lead_id.caller_mobile if appointment.lead_id else '',
                'email': appointment.lead_id.caller_email if appointment.lead_id else '',
                'reference': appointment.lead_id.reference if appointment.lead_id else ''
            },
            
            # Doctor information
            'doctor': {
                'id': appointment.doctor_id.id if appointment.doctor_id else None,
                'name': appointment.doctor_id.name if appointment.doctor_id else '',
                'external_id': appointment.doctor_external_id or ''
            },
            
            # Location information
            'campus': {
                'id': appointment.campus_id.id if appointment.campus_id else None,
                'name': appointment.campus_id.name if appointment.campus_id else ''
            },
            'sub_campus': {
                'id': appointment.sub_campus_id.id if appointment.sub_campus_id else None,
                'name': appointment.sub_campus_id.name if appointment.sub_campus_id else ''
            },
            
            # Speciality
            'speciality': {
                'id': appointment.speciality_id.id if appointment.speciality_id else None,
                'name': appointment.speciality_id.name if appointment.speciality_id else ''
            },
            
            # Clinical session
            'clinical_session': {
                'id': appointment.clinical_session_id.id if appointment.clinical_session_id else None,
                'state': appointment.clinical_session_id.state if appointment.clinical_session_id else None
            } if appointment.clinical_session_id else None,
            
            # Additional info
            'virtual_consultation_url': appointment.virtual_consultation_url or '',
            'geo_location': appointment.geo_location or '',
            'feedback_score': appointment.consultation_feedback_score_new or '',
            'cancel_reason': appointment.cancel_reason or '',
            'booked_at': appointment.slot_booked_at.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if appointment.slot_booked_at else None,
            'booked_by': appointment.slot_booking_user_id.name if appointment.slot_booking_user_id else ''
        }

    @http.route('/api/slots', type='http', auth='none', methods=['GET'], csrf=False)
    def get_available_slots(self, **kwargs):
        """
        Get available appointment slots
        Parameters:
        - date: Date for slots (YYYY-MM-DD, default: today)
        - campus_id: Filter by campus ID (optional)
        - doctor_id: Filter by doctor ID (optional)
        - speciality_id: Filter by speciality ID (optional)
        - consultation_type: Filter by consultation type (optional)
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            # Build domain for available slots
            domain = [('availability', '=', 'open')]
            
            # Date filter
            date_str = kwargs.get('date')
            if date_str:
                try:
                    filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    date_start = datetime.combine(filter_date, datetime.min.time())
                    date_end = datetime.combine(filter_date, datetime.max.time())
                    domain.extend([
                        ('start_datetime', '>=', date_start),
                        ('start_datetime', '<=', date_end)
                    ])
                except ValueError:
                    return self._error_response('Invalid date format. Use YYYY-MM-DD', 400, 'INVALID_DATE')
            else:
                # Only future slots if no date specified
                domain.append(('start_datetime', '>=', datetime.now()))
            
            # Apply optional filters
            if kwargs.get('campus_id'):
                try:
                    domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            if kwargs.get('doctor_id'):
                try:
                    domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
                except ValueError:
                    return self._error_response('Invalid doctor_id', 400, 'INVALID_DOCTOR_ID')
            
            if kwargs.get('speciality_id'):
                try:
                    domain.append(('speciality_id', '=', int(kwargs.get('speciality_id'))))
                except ValueError:
                    return self._error_response('Invalid speciality_id', 400, 'INVALID_SPECIALITY_ID')
            
            if kwargs.get('consultation_type'):
                domain.append(('consultation_type', '=', kwargs.get('consultation_type')))
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 50))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid limit or offset', 400, 'INVALID_PAGINATION')
            
            # Search slots
            slots = request.env['slot.booking'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset, 
                order='start_datetime asc'
            )
            
            # Get total count
            total_count = request.env['slot.booking'].sudo().search_count(domain)
            
            # Serialize slots
            slots_data = [self._serialize_appointment(slot) for slot in slots]
            
            return self._success_response({
                'slots': slots_data,
                'pagination': {
                    'count': len(slots_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'date': date_str,
                    'campus_id': kwargs.get('campus_id'),
                    'doctor_id': kwargs.get('doctor_id'),
                    'speciality_id': kwargs.get('speciality_id'),
                    'consultation_type': kwargs.get('consultation_type')
                }
            }, 'Available slots retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_available_slots: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/appointments', type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def manage_appointments(self, **kwargs):
        """
        POST: Book a new appointment
        GET: Get appointments list
        """
        method = request.httprequest.method
        
        if method == 'POST':
            return self._book_appointment(**kwargs)
        elif method == 'GET':
            return self._get_appointments(**kwargs)

    def _book_appointment(self, **kwargs):
        """
        Book an appointment slot
        Parameters:
        - slot_id: ID of the slot to book (required)
        - lead_id: Lead ID (required)
        - caller_name: Caller name (optional)
        - patient_name: Patient name (optional)
        - payment_mode: Payment mode (cash, online, card, insurance)
        - free_screening: Boolean (default: false)
        - amount: Amount (optional)
        - geo_location: For home consultations (optional)
        - notes: Additional notes (optional)
        """
        try:
            # Validate required parameters
            slot_id = kwargs.get('slot_id')
            lead_id = kwargs.get('lead_id')
            
            if not slot_id:
                return self._error_response('slot_id is required', 400, 'MISSING_SLOT_ID')
            
            if not lead_id:
                return self._error_response('lead_id is required', 400, 'MISSING_LEAD_ID')
            
            # Get and validate slot
            try:
                slot = request.env['slot.booking'].sudo().search([('id', '=', int(slot_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid slot_id format', 400, 'INVALID_SLOT_ID')
            
            if not slot:
                return self._error_response('Slot not found', 404, 'SLOT_NOT_FOUND')
            
            if slot.availability != 'open':
                return self._error_response('Selected slot is no longer available', 409, 'SLOT_NOT_AVAILABLE')
            
            # Get and validate lead
            try:
                lead = request.env['crm.lead'].sudo().search([('id', '=', int(lead_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid lead_id format', 400, 'INVALID_LEAD_ID')
            
            if not lead:
                return self._error_response('Lead not found', 404, 'LEAD_NOT_FOUND')
            
            # Prepare booking data
            booking_data = {
                'lead_id': lead.id,
                'availability': 'booked',
                'slot_booking_user_id': request.env.user.id if request.env.user.id != 4 else 1,
                'slot_booked_at': fields.Datetime.now(),
                'caller_name': kwargs.get('caller_name') or lead.caller_name,
                'patient_name': kwargs.get('patient_name') or lead.patient_name or lead.caller_name
            }
            
            # Handle payment mode
            payment_mode = kwargs.get('payment_mode')
            if payment_mode and payment_mode in ['cash', 'online', 'card', 'insurance']:
                booking_data['payment_mode'] = payment_mode
            
            # Handle free screening
            free_screening = kwargs.get('free_screening', '').lower() in ['true', '1', 'yes']
            booking_data['free_screening'] = free_screening
            if free_screening:
                booking_data['amount'] = 0.0
            elif kwargs.get('amount'):
                try:
                    booking_data['amount'] = float(kwargs.get('amount'))
                except ValueError:
                    return self._error_response('Invalid amount format', 400, 'INVALID_AMOUNT')
            
            # Handle geo location for home consultations
            if kwargs.get('geo_location') and slot.consultation_type == 'Home-Based Consultation':
                booking_data['geo_location'] = kwargs.get('geo_location')
            
            # Handle notes
            if kwargs.get('notes'):
                booking_data['notes'] = kwargs.get('notes')
            
            # Generate virtual consultation URL if needed
            if slot.consultation_type == 'Virtual Consultation':
                booking_data['virtual_consultation_url'] = f"https://meeting.hospital.com/room/{slot.id}"
            
            # Update slot
            slot.write(booking_data)
            
            # Update lead status
            if lead.state == 'lead':
                lead.state = 'opportunity'
            
            return self._success_response({
                'appointment': self._serialize_appointment(slot),
                'booking_reference': slot.name
            }, 'Appointment booked successfully')
            
        except Exception as e:
            _logger.error(f"Error in _book_appointment: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _get_appointments(self, **kwargs):
        """
        Get appointments list
        Parameters:
        - lead_id: Filter by lead ID (optional)
        - status: Filter by status (optional)
        - date_from: Date filter (YYYY-MM-DD, optional)
        - date_to: Date filter (YYYY-MM-DD, optional)
        - doctor_id: Filter by doctor ID (optional)
        - campus_id: Filter by campus ID (optional)
        - limit: Number of records (default: 20)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply filters
            if kwargs.get('lead_id'):
                try:
                    domain.append(('lead_id', '=', int(kwargs.get('lead_id'))))
                except ValueError:
                    return self._error_response('Invalid lead_id', 400, 'INVALID_LEAD_ID')
            
            if kwargs.get('status'):
                valid_statuses = ['open', 'booked', 'confirm', 'checked_in', 'consulting', 'completed', 'cancelled', 'no_show']
                if kwargs.get('status') in valid_statuses:
                    domain.append(('availability', '=', kwargs.get('status')))
                else:
                    return self._error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400, 'INVALID_STATUS')
            
            if kwargs.get('doctor_id'):
                try:
                    domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
                except ValueError:
                    return self._error_response('Invalid doctor_id', 400, 'INVALID_DOCTOR_ID')
            
            if kwargs.get('campus_id'):
                try:
                    domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d')
                    domain.append(('start_datetime', '>=', date_from))
                except ValueError:
                    return self._error_response('Invalid date_from format. Use YYYY-MM-DD', 400, 'INVALID_DATE_FROM')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d')
                    domain.append(('start_datetime', '<=', date_to))
                except ValueError:
                    return self._error_response('Invalid date_to format. Use YYYY-MM-DD', 400, 'INVALID_DATE_TO')
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 20))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid limit or offset', 400, 'INVALID_PAGINATION')
            
            # Search appointments
            appointments = request.env['slot.booking'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset, 
                order='start_datetime desc'
            )
            
            total_count = request.env['slot.booking'].sudo().search_count(domain)
            
            appointments_data = [self._serialize_appointment(appointment) for appointment in appointments]
            
            return self._success_response({
                'appointments': appointments_data,
                'pagination': {
                    'count': len(appointments_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'lead_id': kwargs.get('lead_id'),
                    'status': kwargs.get('status'),
                    'date_from': kwargs.get('date_from'),
                    'date_to': kwargs.get('date_to'),
                    'doctor_id': kwargs.get('doctor_id'),
                    'campus_id': kwargs.get('campus_id')
                }
            }, 'Appointments retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in _get_appointments: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/appointment', type='http', auth='none', methods=['GET', 'PUT', 'DELETE'], csrf=False)
    def manage_single_appointment(self, **kwargs):
        """
        GET: Get specific appointment details
        PUT: Update appointment
        DELETE: Cancel appointment
        Parameters:
        - appointment_id: Appointment ID (required)
        """
        method = request.httprequest.method
        appointment_id = kwargs.get('appointment_id')
        
        if not appointment_id:
            return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
        
        try:
            appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
        except ValueError:
            return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
        
        if not appointment:
            return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
        
        if method == 'GET':
            return self._get_appointment_details(appointment)
        elif method == 'PUT':
            return self._update_appointment(appointment, **kwargs)
        elif method == 'DELETE':
            return self._cancel_appointment(appointment, **kwargs)

    def _get_appointment_details(self, appointment):
        """Get detailed appointment information"""
        try:
            return self._success_response({
                'appointment': self._serialize_appointment(appointment)
            }, 'Appointment details retrieved successfully')
        except Exception as e:
            _logger.error(f"Error in _get_appointment_details: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _update_appointment(self, appointment, **kwargs):
        """Update appointment details"""
        try:
            update_data = {}
            
            # Fields that can be updated
            updatable_fields = ['notes', 'amount', 'payment_mode', 'geo_location']
            
            for field in updatable_fields:
                if kwargs.get(field) is not None:
                    if field == 'amount':
                        try:
                            update_data[field] = float(kwargs.get(field))
                        except ValueError:
                            return self._error_response('Invalid amount format', 400, 'INVALID_AMOUNT')
                    elif field == 'payment_mode':
                        if kwargs.get(field) in ['cash', 'online', 'card', 'insurance']:
                            update_data[field] = kwargs.get(field)
                        else:
                            return self._error_response('Invalid payment_mode', 400, 'INVALID_PAYMENT_MODE')
                    else:
                        update_data[field] = kwargs.get(field)
            
            if update_data:
                appointment.write(update_data)
                
                return self._success_response({
                    'appointment': self._serialize_appointment(appointment),
                    'updated_fields': list(update_data.keys())
                }, 'Appointment updated successfully')
            else:
                return self._error_response('No valid fields provided for update', 400, 'NO_UPDATE_FIELDS')
                
        except Exception as e:
            _logger.error(f"Error in _update_appointment: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _cancel_appointment(self, appointment, **kwargs):
        """Cancel appointment"""
        try:
            if appointment.availability in ['completed', 'cancelled']:
                return self._error_response('Cannot cancel appointment in current status', 400, 'CANNOT_CANCEL')
            
            reason = kwargs.get('reason', 'Cancelled by patient')
            
            appointment.write({
                'availability': 'cancelled',
                'cancel_reason': reason
            })
            
            return self._success_response({
                'appointment': self._serialize_appointment(appointment),
                'cancel_reason': reason
            }, 'Appointment cancelled successfully')
            
        except Exception as e:
            _logger.error(f"Error in _cancel_appointment: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/confirm', type='http', auth='none', methods=['POST'], csrf=False)
    def confirm_appointment(self, **kwargs):
        """
        Confirm an appointment
        Parameters:
        - appointment_id: Appointment ID (required)
        """
        try:
            appointment_id = kwargs.get('appointment_id')
            if not appointment_id:
                return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
            
            try:
                appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
            
            if not appointment:
                return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
            
            if appointment.availability != 'booked':
                return self._error_response('Only booked appointments can be confirmed', 400, 'INVALID_STATUS_FOR_CONFIRM')
            
            appointment.act_confirm()
            
            return self._success_response({
                'appointment': self._serialize_appointment(appointment)
            }, 'Appointment confirmed successfully')
            
        except UserError as e:
            return self._error_response(str(e), 400, 'CONFIRM_ERROR')
        except Exception as e:
            _logger.error(f"Error in confirm_appointment: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/checkin', type='http', auth='none', methods=['POST'], csrf=False)
    def check_in_appointment(self, **kwargs):
        """
        Check in for an appointment (creates clinical session)
        Parameters:
        - appointment_id: Appointment ID (required)
        """
        try:
            appointment_id = kwargs.get('appointment_id')
            if not appointment_id:
                return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
            
            try:
                appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
            
            if not appointment:
                return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
            
            if appointment.availability not in ['booked', 'confirm']:
                return self._error_response('Only confirmed appointments can be checked in', 400, 'INVALID_STATUS_FOR_CHECKIN')
            
            # Check in and create clinical session
            appointment.check_in()
            
            response_data = {
                'appointment': self._serialize_appointment(appointment),
                'check_in_time': appointment.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if appointment.start_datetime else None
            }
            
            # Add clinical session info if created
            if appointment.clinical_session_id:
                response_data['clinical_session'] = {
                    'id': appointment.clinical_session_id.id,
                    'name': appointment.clinical_session_id.name,
                    'state': appointment.clinical_session_id.state
                }
            
            return self._success_response(response_data, 'Check-in successful. Clinical session created.')
            
        except UserError as e:
            return self._error_response(str(e), 400, 'CHECKIN_ERROR')
        except Exception as e:
            _logger.error(f"Error in check_in_appointment: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/start', type='http', auth='none', methods=['POST'], csrf=False)
    def start_consultation(self, **kwargs):
        """
        Start consultation for an appointment
        Parameters:
        - appointment_id: Appointment ID (required)
        """
        try:
            appointment_id = kwargs.get('appointment_id')
            if not appointment_id:
                return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
            
            try:
                appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
            
            if not appointment:
                return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
            
            if appointment.availability != 'checked_in':
                return self._error_response('Patient must be checked in before starting consultation', 400, 'INVALID_STATUS_FOR_START')
            
            appointment.start_consultation()
            
            return self._success_response({
                'appointment': self._serialize_appointment(appointment),
                'consultation_started': True
            }, 'Consultation started successfully')
            
        except UserError as e:
            return self._error_response(str(e), 400, 'START_ERROR')
        except Exception as e:
            _logger.error(f"Error in start_consultation: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/finish', type='http', auth='none', methods=['POST'], csrf=False)
    def finish_consultation(self, **kwargs):
        """
        Finish consultation for an appointment
        Parameters:
        - appointment_id: Appointment ID (required)
        - feedback_score: Feedback score (1-5, optional)
        - notes: Consultation notes (optional)
        """
        try:
            appointment_id = kwargs.get('appointment_id')
            if not appointment_id:
                return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
            
            try:
                appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
            
            if not appointment:
                return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
            
            if appointment.availability != 'consulting':
                return self._error_response('Consultation must be started before finishing', 400, 'INVALID_STATUS_FOR_FINISH')
            
            # Update optional fields
            update_data = {}
            if kwargs.get('feedback_score'):
                if kwargs.get('feedback_score') in ['1', '2', '3', '4', '5']:
                    update_data['consultation_feedback_score_new'] = kwargs.get('feedback_score')
                else:
                    return self._error_response('feedback_score must be between 1 and 5', 400, 'INVALID_FEEDBACK_SCORE')
            
            if kwargs.get('notes'):
                update_data['notes'] = kwargs.get('notes')
            
            if update_data:
                appointment.write(update_data)
            
            appointment.finish_consultation()
            
            return self._success_response({
                'appointment': self._serialize_appointment(appointment),
                'consultation_completed': True
            }, 'Consultation completed successfully')
            
        except UserError as e:
            return self._error_response(str(e), 400, 'FINISH_ERROR')
        except Exception as e:
            _logger.error(f"Error in finish_consultation: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/reschedule', type='http', auth='none', methods=['POST'], csrf=False)
    def reschedule_appointment(self, **kwargs):
        """
        Reschedule an appointment to a new slot
        Parameters:
        - appointment_id: Current appointment ID (required)
        - new_slot_id: New slot ID (required)
        - reason: Reschedule reason (optional)
        """
        try:
            appointment_id = kwargs.get('appointment_id')
            new_slot_id = kwargs.get('new_slot_id')
            
            if not appointment_id:
                return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
            
            if not new_slot_id:
                return self._error_response('new_slot_id is required', 400, 'MISSING_NEW_SLOT_ID')
            
            # Get current appointment
            try:
                appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
            
            if not appointment:
                return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
            
            # Get new slot
            try:
                new_slot = request.env['slot.booking'].sudo().search([('id', '=', int(new_slot_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid new_slot_id format', 400, 'INVALID_NEW_SLOT_ID')
            
            if not new_slot:
                return self._error_response('New slot not found', 404, 'NEW_SLOT_NOT_FOUND')
            
            if new_slot.availability != 'open':
                return self._error_response('New slot is not available', 409, 'NEW_SLOT_NOT_AVAILABLE')
            
            if appointment.availability not in ['booked', 'confirm']:
                return self._error_response('Only booked or confirmed appointments can be rescheduled', 400, 'INVALID_STATUS_FOR_RESCHEDULE')
            
            # Store original slot data
            original_data = {
                'lead_id': appointment.lead_id.id,
                'caller_name': appointment.caller_name,
                'patient_name': appointment.patient_name,
                'payment_mode': appointment.payment_mode,
                'amount': appointment.amount,
                'free_screening': appointment.free_screening,
                'notes': appointment.notes,
                'geo_location': appointment.geo_location
            }
            
            # Free up the original slot
            appointment.write({
                'availability': 'open',
                'lead_id': False,
                'caller_name': '',
                'patient_name': '',
                'slot_booked_at': False,
                'notes': kwargs.get('reason', 'Rescheduled by patient')
            })
            
            # Book the new slot
            new_slot.write({
                'availability': 'booked',
                'slot_booking_user_id': request.env.user.id if request.env.user.id != 4 else 1,
                'slot_booked_at': fields.Datetime.now(),
                **original_data
            })
            
            return self._success_response({
                'new_appointment': self._serialize_appointment(new_slot),
                'original_appointment_id': appointment_id,
                'reschedule_reason': kwargs.get('reason', 'Rescheduled by patient')
            }, 'Appointment rescheduled successfully')
            
        except Exception as e:
            _logger.error(f"Error in reschedule_appointment: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/noshow', type='http', auth='none', methods=['POST'], csrf=False)
    def mark_no_show(self, **kwargs):
        """
        Mark appointment as no-show
        Parameters:
        - appointment_id: Appointment ID (required)
        - notes: Additional notes (optional)
        """
        try:
            appointment_id = kwargs.get('appointment_id')
            if not appointment_id:
                return self._error_response('appointment_id is required', 400, 'MISSING_APPOINTMENT_ID')
            
            try:
                appointment = request.env['slot.booking'].sudo().search([('id', '=', int(appointment_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid appointment_id format', 400, 'INVALID_APPOINTMENT_ID')
            
            if not appointment:
                return self._error_response('Appointment not found', 404, 'APPOINTMENT_NOT_FOUND')
            
            if appointment.availability not in ['booked', 'confirm']:
                return self._error_response('Only booked or confirmed appointments can be marked as no-show', 400, 'INVALID_STATUS_FOR_NOSHOW')
            
            update_data = {'availability': 'no_show'}
            if kwargs.get('notes'):
                update_data['notes'] = kwargs.get('notes')
            
            appointment.write(update_data)
            
            return self._success_response({
                'appointment': self._serialize_appointment(appointment)
            }, 'Appointment marked as no-show')
            
        except Exception as e:
            _logger.error(f"Error in mark_no_show: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/search', type='http', auth='none', methods=['GET'], csrf=False)
    def search_appointments(self, **kwargs):
        """
        Search appointments with advanced filters
        Parameters:
        - q: Search query (searches in patient name, reference, phone)
        - status: Filter by status (optional)
        - consultation_type: Filter by consultation type (optional)
        - date_from: Date filter (YYYY-MM-DD, optional)
        - date_to: Date filter (YYYY-MM-DD, optional)
        - campus_id: Filter by campus (optional)
        - doctor_id: Filter by doctor (optional)
        - limit: Number of records (default: 20)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Text search
            search_query = kwargs.get('q', '').strip()
            if search_query:
                domain.append('|')
                domain.append('|')
                domain.append('|')
                domain.append(('patient_name', 'ilike', search_query))
                domain.append(('caller_name', 'ilike', search_query))
                domain.append(('name', 'ilike', search_query))
                domain.append(('lead_id.caller_mobile', 'ilike', search_query))
            
            # Apply other filters (reuse logic from _get_appointments)
            if kwargs.get('status'):
                valid_statuses = ['open', 'booked', 'confirm', 'checked_in', 'consulting', 'completed', 'cancelled', 'no_show']
                if kwargs.get('status') in valid_statuses:
                    domain.append(('availability', '=', kwargs.get('status')))
            
            if kwargs.get('consultation_type'):
                domain.append(('consultation_type', '=', kwargs.get('consultation_type')))
            
            if kwargs.get('campus_id'):
                try:
                    domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            if kwargs.get('doctor_id'):
                try:
                    domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
                except ValueError:
                    return self._error_response('Invalid doctor_id', 400, 'INVALID_DOCTOR_ID')
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d')
                    domain.append(('start_datetime', '>=', date_from))
                except ValueError:
                    return self._error_response('Invalid date_from format', 400, 'INVALID_DATE_FROM')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d')
                    domain.append(('start_datetime', '<=', date_to))
                except ValueError:
                    return self._error_response('Invalid date_to format', 400, 'INVALID_DATE_TO')
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 20))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Search appointments
            appointments = request.env['slot.booking'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='start_datetime desc, id desc'
            )
            
            total_count = request.env['slot.booking'].sudo().search_count(domain)
            
            appointments_data = [self._serialize_appointment(appointment) for appointment in appointments]
            
            return self._success_response({
                'appointments': appointments_data,
                'pagination': {
                    'count': len(appointments_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'search': {
                    'query': search_query,
                    'filters': {
                        'status': kwargs.get('status'),
                        'consultation_type': kwargs.get('consultation_type'),
                        'date_from': kwargs.get('date_from'),
                        'date_to': kwargs.get('date_to'),
                        'campus_id': kwargs.get('campus_id'),
                        'doctor_id': kwargs.get('doctor_id')
                    }
                }
            }, 'Search completed successfully')
            
        except Exception as e:
            _logger.error(f"Error in search_appointments: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')
        

        # -*- coding: utf-8 -*-
# from odoo import http, fields
# from odoo.http import request
# import json
# import logging
# from datetime import datetime
# from odoo.exceptions import ValidationError, UserError
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class ConsultationsAPI(http.Controller):
    
    def _make_response(self, data, status=200):
        """Helper method to create standardized JSON responses"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            ],
            status=status
        )

    def _success_response(self, data=None, message="Success"):
        """Standard success response format"""
        response = {
            'success': True,
            'message': message,
            'data': data or {}
        }
        return self._make_response(response)

    def _error_response(self, message="Error", status=400, error_code=None):
        """Standard error response format"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code,
            'data': None
        }
        return self._make_response(response, status)

    def _serialize_consultation(self, consultation):
        """Serialize consultation object to dictionary"""
        return {
            'id': consultation.id,
            'name': consultation.name,
            'date': consultation.date.strftime(DEFAULT_SERVER_DATE_FORMAT) if consultation.date else None,
            'start_datetime': consultation.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.start_datetime else None,
            'end_datetime': consultation.end_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.end_datetime else None,
            'type': consultation.type,
            'state': consultation.state,
            'consultation_type': consultation.consultation_type,
            'priority': consultation.priority,
            'prescription_status': consultation.prescription_status,
            'is_sos': consultation.is_sos,
            'next_followup': consultation.next_followup,
            'next_followup_date': consultation.next_followup_date.strftime(DEFAULT_SERVER_DATE_FORMAT) if consultation.next_followup_date else None,
            
            # Patient information
            'patient': {
                'id': consultation.patient_id.id if consultation.patient_id else None,
                'name': consultation.patient_id.name if consultation.patient_id else None,
                'identification_code': consultation.patient_id.identification_code if consultation.patient_id else None,
            } if consultation.patient_id else None,
            
            # Psychiatrist information
            'psychiatrist': {
                'id': consultation.psychiatrist_id.id if consultation.psychiatrist_id else None,
                'name': consultation.psychiatrist_id.name if consultation.psychiatrist_id else None,
                'team_role': consultation.team_role,
            } if consultation.psychiatrist_id else None,
            
            # IP/OP information
            'inpatient_admission': {
                'id': consultation.inpatient_admission_id.id if consultation.inpatient_admission_id else None,
                'name': consultation.inpatient_admission_id.name if consultation.inpatient_admission_id else None,
            } if consultation.inpatient_admission_id else None,
            
            'op_visit': {
                'id': consultation.op_visit_id.id if consultation.op_visit_id else None,
                'name': consultation.op_visit_id.name if consultation.op_visit_id else None,
            } if consultation.op_visit_id else None,
            
            # Vitals
            'vitals': {
                'bp': consultation.bp,
                'bp2': consultation.bp2,
                'wt': consultation.wt,
                'grbs': consultation.grbs,
                'spo2': consultation.spo2,
                'pulse': consultation.pulse,
                'vitals_checked_by': consultation.vitals_checked_user_id.name if consultation.vitals_checked_user_id else None,
                'vitals_checked_on': consultation.vitals_checked_on.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.vitals_checked_on else None,
            },
            
            # Clinical information
            'general_observation': consultation.general_observation,
            'current_medication': consultation.current_medication,
            'doctor_advice': consultation.doctor_advice,
            'precautions': consultation.precautions,
            'todo': consultation.todo,
            'advice_to_counsellor': consultation.advice_to_counsellor,
            'advice_to_psychologist': consultation.advice_to_psychologist,
            'lab_advice': consultation.lab_advice,
            'cross_consultation': consultation.cross_consultation,
            
            # Follow-up information
            'followup_type': {
                'id': consultation.followup_type_id.id if consultation.followup_type_id else None,
                'name': consultation.followup_type_id.name if consultation.followup_type_id else None,
            } if consultation.followup_type_id else None,
            
            # CP Therapist
            'cp_therapist': {
                'id': consultation.cp_therapist_id.id if consultation.cp_therapist_id else None,
                'name': consultation.cp_therapist_id.name if consultation.cp_therapist_id else None,
            } if consultation.cp_therapist_id else None,
            
            # Lab tests and specialities
            'lab_tests': [{'id': lab.id, 'name': lab.name} for lab in consultation.labtest_type_ids],
            'specialities': [{'id': spec.id, 'name': spec.name} for spec in consultation.speciality_ids],
            'scale_types': [{'scale_type': scale.scale_type} for scale in consultation.scale_type_ids],
            
            # Prescription info
            'prescription_lines_count': len(consultation.consultation_prescription_line_ids),
            
            # Admission referral information
            'admission_referral': {
                'price_tag': consultation.price_tag.name if consultation.price_tag else None,
                'referral_config': consultation.referral_config_id.name if consultation.referral_config_id else None,
                'illness_tag': consultation.illness_tag.name if consultation.illness_tag else None,
                'bed_type': consultation.bed_type_id.name if consultation.bed_type_id else None,
                'hospitalization_length': consultation.hospitalization_length,
                'approx_cost': consultation.approx_cost,
                'treatment_planned': consultation.treatment_planned,
                'consultation_require': consultation.consultation_require,
                'provisional_admission_date': consultation.provisional_admission_date.strftime(DEFAULT_SERVER_DATE_FORMAT) if consultation.provisional_admission_date else None,
            },
            
            # Metadata
            'created_by': consultation.user_id.name if consultation.user_id else None,
            'company': consultation.company_id.name if consultation.company_id else None,
        }

    @http.route('/api/consultations', type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def manage_consultations(self, **kwargs):
        """
        POST: Create a new consultation
        GET: Get consultations list
        """
        method = request.httprequest.method
        
        if method == 'POST':
            return self._create_consultation(**kwargs)
        elif method == 'GET':
            return self._get_consultations(**kwargs)

    def _create_consultation(self, **kwargs):
        """
        Create a new consultation
        Parameters:
        - type: 'ip' or 'op' (required)
        - psychiatrist_id: ID of the psychiatrist (required)
        - inpatient_admission_id: Required if type='ip'
        - op_visit_id: Required if type='op'
        - date: Consultation date (YYYY-MM-DD, default: today)
        - consultation_type: 'psychiatrist', 'clinical_psychologist', 'counsellor'
        - priority: 'low', 'medium', 'high', 'emergency'
        - general_observation: Text
        - current_medication: Text
        - advice_to_counsellor: Text
        - advice_to_psychologist: Text
        - cp_therapist_id: Clinical psychologist therapist ID
        - lab_advice: Text
        - labtest_type_ids: List of lab test IDs [1,2,3]
        - speciality_ids: List of speciality IDs [1,2,3]
        - followup_type_id: Follow-up type ID
        - cross_consultation: Text
        - doctor_advice: Text
        - precautions: Text
        - todo: Text
        - is_sos: Boolean
        - next_followup: Boolean
        - next_followup_date: Date (YYYY-MM-DD)
        - scale_type_ids: List of scale types ['assist_who', 'basis_32', etc.]
        """
        try:
            # Validate required parameters
            consultation_type = kwargs.get('type')
            psychiatrist_id = kwargs.get('psychiatrist_id')
            
            if not consultation_type or consultation_type not in ['ip', 'op']:
                return self._error_response('type is required and must be either "ip" or "op"', 400, 'INVALID_TYPE')
            
            if not psychiatrist_id:
                return self._error_response('psychiatrist_id is required', 400, 'MISSING_PSYCHIATRIST_ID')
            
            # Validate psychiatrist exists
            try:
                psychiatrist = request.env['hr.employee'].sudo().search([('id', '=', int(psychiatrist_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid psychiatrist_id format', 400, 'INVALID_PSYCHIATRIST_ID')
            
            if not psychiatrist:
                return self._error_response(f'Psychiatrist with ID {psychiatrist_id} not found', 404, 'PSYCHIATRIST_NOT_FOUND')
            
            # Validate admission/visit based on type
            if consultation_type == 'ip':
                inpatient_admission_id = kwargs.get('inpatient_admission_id')
                if not inpatient_admission_id:
                    return self._error_response('inpatient_admission_id is required for IP consultations', 400, 'MISSING_ADMISSION_ID')
                
                try:
                    admission = request.env['hospital.admission'].sudo().search([('id', '=', int(inpatient_admission_id))], limit=1)
                except ValueError:
                    return self._error_response('Invalid inpatient_admission_id format', 400, 'INVALID_ADMISSION_ID')
                
                if not admission:
                    return self._error_response(f'Inpatient admission with ID {inpatient_admission_id} not found', 404, 'ADMISSION_NOT_FOUND')
            
            elif consultation_type == 'op':
                op_visit_id = kwargs.get('op_visit_id')
                if not op_visit_id:
                    return self._error_response('op_visit_id is required for OP consultations', 400, 'MISSING_OP_VISIT_ID')
                
                try:
                    op_visit = request.env['op.visits'].sudo().search([('id', '=', int(op_visit_id))], limit=1)
                except ValueError:
                    return self._error_response('Invalid op_visit_id format', 400, 'INVALID_OP_VISIT_ID')
                
                if not op_visit:
                    return self._error_response(f'OP visit with ID {op_visit_id} not found', 404, 'OP_VISIT_NOT_FOUND')
            
            # Prepare consultation values
            vals = {
                'type': consultation_type,
                'psychiatrist_id': int(psychiatrist_id),
                'date': kwargs.get('date', fields.Date.context_today(request.env['consultation.consultation'])),
            }
            
            # Add type-specific fields
            if consultation_type == 'ip':
                vals['inpatient_admission_id'] = int(inpatient_admission_id)
            else:
                vals['op_visit_id'] = int(op_visit_id)
            
            # Add optional fields
            optional_fields = {
                'consultation_type': kwargs.get('consultation_type'),
                'priority': kwargs.get('priority'),
                'general_observation': kwargs.get('general_observation'),
                'current_medication': kwargs.get('current_medication'),
                'advice_to_counsellor': kwargs.get('advice_to_counsellor'),
                'advice_to_psychologist': kwargs.get('advice_to_psychologist'),
                'lab_advice': kwargs.get('lab_advice', '/'),
                'cross_consultation': kwargs.get('cross_consultation'),
                'doctor_advice': kwargs.get('doctor_advice'),
                'precautions': kwargs.get('precautions'),
                'todo': kwargs.get('todo'),
                'is_sos': kwargs.get('is_sos', '').lower() in ['true', '1', 'yes'],
                'next_followup': kwargs.get('next_followup', '').lower() in ['true', '1', 'yes'],
            }
            
            # Add non-empty optional fields
            for field, value in optional_fields.items():
                if value is not None and value != '':
                    vals[field] = value
            
            # Handle date fields
            if kwargs.get('next_followup_date'):
                try:
                    vals['next_followup_date'] = datetime.strptime(kwargs.get('next_followup_date'), '%Y-%m-%d').date()
                except ValueError:
                    return self._error_response('Invalid next_followup_date format. Use YYYY-MM-DD', 400, 'INVALID_FOLLOWUP_DATE')
            
            # Handle related fields
            if kwargs.get('cp_therapist_id'):
                try:
                    cp_therapist = request.env['hr.employee'].sudo().search([('id', '=', int(kwargs.get('cp_therapist_id')))], limit=1)
                    if cp_therapist:
                        vals['cp_therapist_id'] = cp_therapist.id
                except ValueError:
                    return self._error_response('Invalid cp_therapist_id format', 400, 'INVALID_CP_THERAPIST_ID')
            
            if kwargs.get('followup_type_id'):
                try:
                    followup_type = request.env['followup.type'].sudo().search([('id', '=', int(kwargs.get('followup_type_id')))], limit=1)
                    if followup_type:
                        vals['followup_type_id'] = followup_type.id
                except ValueError:
                    return self._error_response('Invalid followup_type_id format', 400, 'INVALID_FOLLOWUP_TYPE_ID')
            
            # Handle Many2many fields
            if kwargs.get('labtest_type_ids'):
                try:
                    labtest_ids = json.loads(kwargs.get('labtest_type_ids')) if isinstance(kwargs.get('labtest_type_ids'), str) else kwargs.get('labtest_type_ids')
                    if isinstance(labtest_ids, list):
                        vals['labtest_type_ids'] = [(6, 0, labtest_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._error_response('Invalid labtest_type_ids format. Should be a list of IDs', 400, 'INVALID_LABTEST_IDS')
            
            if kwargs.get('speciality_ids'):
                try:
                    speciality_ids = json.loads(kwargs.get('speciality_ids')) if isinstance(kwargs.get('speciality_ids'), str) else kwargs.get('speciality_ids')
                    if isinstance(speciality_ids, list):
                        vals['speciality_ids'] = [(6, 0, speciality_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._error_response('Invalid speciality_ids format. Should be a list of IDs', 400, 'INVALID_SPECIALITY_IDS')
            
            # Handle scale types (One2many)
            if kwargs.get('scale_type_ids'):
                try:
                    scale_types = json.loads(kwargs.get('scale_type_ids')) if isinstance(kwargs.get('scale_type_ids'), str) else kwargs.get('scale_type_ids')
                    if isinstance(scale_types, list):
                        scale_vals = []
                        for scale_type in scale_types:
                            scale_vals.append((0, 0, {'scale_type': scale_type}))
                        vals['scale_type_ids'] = scale_vals
                except (json.JSONDecodeError, TypeError):
                    return self._error_response('Invalid scale_type_ids format. Should be a list of scale types', 400, 'INVALID_SCALE_TYPES')
            
            # Create consultation
            consultation = request.env['consultation.consultation'].sudo().create(vals)
            
            return self._success_response({
                'consultation_id': consultation.id,
                'consultation_name': consultation.name,
                'consultation': self._serialize_consultation(consultation)
            }, 'Consultation created successfully')
            
        except Exception as e:
            _logger.error(f"Error in _create_consultation: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _get_consultations(self, **kwargs):
        """
        Get consultations list
        Parameters:
        - psychiatrist_id: Filter by psychiatrist ID
        - patient_id: Filter by patient ID
        - type: Filter by consultation type ('ip' or 'op')
        - state: Filter by consultation state
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)
        - inpatient_admission_id: Filter by IP admission ID
        - op_visit_id: Filter by OP visit ID
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply filters
            if kwargs.get('psychiatrist_id'):
                try:
                    domain.append(('psychiatrist_id', '=', int(kwargs.get('psychiatrist_id'))))
                except ValueError:
                    return self._error_response('Invalid psychiatrist_id', 400, 'INVALID_PSYCHIATRIST_ID')
            
            if kwargs.get('patient_id'):
                try:
                    domain.append(('patient_id', '=', int(kwargs.get('patient_id'))))
                except ValueError:
                    return self._error_response('Invalid patient_id', 400, 'INVALID_PATIENT_ID')
            
            if kwargs.get('type'):
                if kwargs.get('type') in ['ip', 'op']:
                    domain.append(('type', '=', kwargs.get('type')))
                else:
                    return self._error_response('Invalid type. Must be "ip" or "op"', 400, 'INVALID_TYPE')
            
            if kwargs.get('state'):
                valid_states = ['draft', 'started', 'ended', 'completed', 'cancelled', 'referral', 
                              'followup', 'admission', 'cross_consultation', 'admission_referral', 
                              'admission_followup', 'admission_cross_consultation', 'discharge']
                if kwargs.get('state') in valid_states:
                    domain.append(('state', '=', kwargs.get('state')))
                else:
                    return self._error_response(f'Invalid state. Must be one of: {", ".join(valid_states)}', 400, 'INVALID_STATE')
            
            if kwargs.get('inpatient_admission_id'):
                try:
                    domain.append(('inpatient_admission_id', '=', int(kwargs.get('inpatient_admission_id'))))
                except ValueError:
                    return self._error_response('Invalid inpatient_admission_id', 400, 'INVALID_ADMISSION_ID')
            
            if kwargs.get('op_visit_id'):
                try:
                    domain.append(('op_visit_id', '=', int(kwargs.get('op_visit_id'))))
                except ValueError:
                    return self._error_response('Invalid op_visit_id', 400, 'INVALID_OP_VISIT_ID')
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d').date()
                    domain.append(('date', '>=', date_from))
                except ValueError:
                    return self._error_response('Invalid date_from format. Use YYYY-MM-DD', 400, 'INVALID_DATE_FROM')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d').date()
                    domain.append(('date', '<=', date_to))
                except ValueError:
                    return self._error_response('Invalid date_to format. Use YYYY-MM-DD', 400, 'INVALID_DATE_TO')
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 50))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Search consultations
            consultations = request.env['consultation.consultation'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset, 
                order='date desc, id desc'
            )
            
            # Get total count
            total_count = request.env['consultation.consultation'].sudo().search_count(domain)
            
            consultation_data = [self._serialize_consultation(consultation) for consultation in consultations]
            
            return self._success_response({
                'consultations': consultation_data,
                'pagination': {
                    'count': len(consultation_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'psychiatrist_id': kwargs.get('psychiatrist_id'),
                    'patient_id': kwargs.get('patient_id'),
                    'type': kwargs.get('type'),
                    'state': kwargs.get('state'),
                    'date_from': kwargs.get('date_from'),
                    'date_to': kwargs.get('date_to'),
                    'inpatient_admission_id': kwargs.get('inpatient_admission_id'),
                    'op_visit_id': kwargs.get('op_visit_id')
                }
            }, 'Consultations retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in _get_consultations: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/consultation', type='http', auth='none', methods=['GET', 'PUT', 'DELETE'], csrf=False)
    def manage_single_consultation(self, **kwargs):
        """
        GET: Get specific consultation details
        PUT: Update consultation
        DELETE: Delete consultation
        Parameters:
        - consultation_id: Consultation ID (required)
        """
        method = request.httprequest.method
        consultation_id = kwargs.get('consultation_id')
        
        if not consultation_id:
            return self._error_response('consultation_id is required', 400, 'MISSING_CONSULTATION_ID')
        
        try:
            consultation = request.env['consultation.consultation'].sudo().search([('id', '=', int(consultation_id))], limit=1)
        except ValueError:
            return self._error_response('Invalid consultation_id format', 400, 'INVALID_CONSULTATION_ID')
        
        if not consultation:
            return self._error_response('Consultation not found', 404, 'CONSULTATION_NOT_FOUND')
        
        if method == 'GET':
            return self._get_consultation_details(consultation)
        elif method == 'PUT':
            return self._update_consultation(consultation, **kwargs)
        elif method == 'DELETE':
            return self._delete_consultation(consultation)

    def _get_consultation_details(self, consultation):
        """Get detailed consultation information"""
        try:
            return self._success_response({
                'consultation': self._serialize_consultation(consultation)
            }, 'Consultation details retrieved successfully')
        except Exception as e:
            _logger.error(f"Error in _get_consultation_details: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _update_consultation(self, consultation, **kwargs):
        """Update consultation details"""
        try:
            vals = {}
            
            # Simple text fields
            text_fields = ['general_observation', 'current_medication', 'advice_to_counsellor', 
                          'advice_to_psychologist', 'lab_advice', 'cross_consultation', 
                          'doctor_advice', 'precautions', 'todo', 'treatment_planned']
            
            for field in text_fields:
                if field in kwargs:
                    vals[field] = kwargs[field]
            
            # Selection fields
            selection_fields = {
                'consultation_type': ['psychiatrist', 'clinical_psychologist', 'counsellor'],
                'priority': ['low', 'medium', 'high', 'emergency'],
                'prescription_status': ['changed', 'continued']
            }
            
            for field, valid_values in selection_fields.items():
                if field in kwargs:
                    if kwargs[field] in valid_values:
                        vals[field] = kwargs[field]
                    else:
                        return self._error_response(f'Invalid {field}. Must be one of: {", ".join(valid_values)}', 400, f'INVALID_{field.upper()}')
            
            # Boolean fields
            boolean_fields = ['is_sos', 'next_followup', 'consultation_require']
            for field in boolean_fields:
                if field in kwargs:
                    vals[field] = kwargs[field] in ['true', 'True', '1', 1, True]
            
            # Integer fields
            integer_fields = ['bp', 'bp2', 'wt', 'grbs', 'spo2', 'pulse', 'hospitalization_length', 'age']
            for field in integer_fields:
                if field in kwargs:
                    try:
                        vals[field] = int(kwargs[field])
                    except ValueError:
                        return self._error_response(f'Invalid {field}. Must be an integer', 400, f'INVALID_{field.upper()}')
            
            # Float fields
            if 'approx_cost' in kwargs:
                try:
                    vals['approx_cost'] = float(kwargs['approx_cost'])
                except ValueError:
                    return self._error_response('Invalid approx_cost. Must be a number', 400, 'INVALID_APPROX_COST')
            
            # Date fields
            date_fields = ['date', 'next_followup_date', 'provisional_admission_date']
            for field in date_fields:
                if field in kwargs:
                    try:
                        vals[field] = datetime.strptime(kwargs[field], '%Y-%m-%d').date()
                    except ValueError:
                        return self._error_response(f'Invalid {field} format. Use YYYY-MM-DD', 400, f'INVALID_{field.upper()}')
            
            # Many2one fields
            many2one_fields = {
                'psychiatrist_id': 'hr.employee',
                'cp_therapist_id': 'hr.employee',
                'followup_type_id': 'followup.type',
                'price_tag': 'product.pricelist',
                'referral_config_id': 'admission.referral.config',
                'illness_tag': 'illness.tag',
                'bed_type_id': 'oeh.medical.health.center.ward'
            }
            
            for field, model in many2one_fields.items():
                if field in kwargs:
                    if kwargs[field]:
                        try:
                            record = request.env[model].sudo().search([('id', '=', int(kwargs[field]))], limit=1)
                            if record:
                                vals[field] = record.id
                            else:
                                return self._error_response(f'{field} with ID {kwargs[field]} not found', 404, f'{field.upper()}_NOT_FOUND')
                        except ValueError:
                            return self._error_response(f'Invalid {field} format', 400, f'INVALID_{field.upper()}')
                    else:
                        vals[field] = False
            
            # Many2many fields
            if 'labtest_type_ids' in kwargs:
                try:
                    labtest_ids = json.loads(kwargs['labtest_type_ids']) if isinstance(kwargs['labtest_type_ids'], str) else kwargs['labtest_type_ids']
                    if isinstance(labtest_ids, list):
                        vals['labtest_type_ids'] = [(6, 0, labtest_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._error_response('Invalid labtest_type_ids format', 400, 'INVALID_LABTEST_IDS')
            
            if 'speciality_ids' in kwargs:
                try:
                    speciality_ids = json.loads(kwargs['speciality_ids']) if isinstance(kwargs['speciality_ids'], str) else kwargs['speciality_ids']
                    if isinstance(speciality_ids, list):
                        vals['speciality_ids'] = [(6, 0, speciality_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._error_response('Invalid speciality_ids format', 400, 'INVALID_SPECIALITY_IDS')
            
            # One2many fields - Scale types
            if 'scale_type_ids' in kwargs:
                try:
                    scale_types = json.loads(kwargs['scale_type_ids']) if isinstance(kwargs['scale_type_ids'], str) else kwargs['scale_type_ids']
                    if isinstance(scale_types, list):
                        # Clear existing scales and add new ones
                        scale_vals = [(5, 0, 0)]  # Clear all existing
                        for scale_type in scale_types:
                            scale_vals.append((0, 0, {'scale_type': scale_type}))
                        vals['scale_type_ids'] = scale_vals
                except (json.JSONDecodeError, TypeError):
                    return self._error_response('Invalid scale_type_ids format', 400, 'INVALID_SCALE_TYPES')
            
            # Update consultation
            if vals:
                consultation.write(vals)
                
                return self._success_response({
                    'consultation_id': consultation.id,
                    'updated_fields': list(vals.keys()),
                    'consultation': self._serialize_consultation(consultation)
                }, 'Consultation updated successfully')
            else:
                return self._error_response('No valid fields provided for update', 400, 'NO_UPDATE_FIELDS')
            
        except Exception as e:
            _logger.error(f"Error in _update_consultation: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _delete_consultation(self, consultation):
        """Delete consultation"""
        try:
            # Check if consultation can be deleted (only if in draft or cancelled state)
            if consultation.state not in ['draft', 'cancelled']:
                return self._error_response(f'Cannot delete consultation in {consultation.state} state. Only draft or cancelled consultations can be deleted.', 400, 'CANNOT_DELETE')
            
            consultation_name = consultation.name
            consultation_id = consultation.id
            consultation.unlink()
            
            return self._success_response({
                'consultation_id': consultation_id,
                'consultation_name': consultation_name
            }, 'Consultation deleted successfully')
            
        except Exception as e:
            _logger.error(f"Error in _delete_consultation: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/state', type='http', auth='none', methods=['POST'], csrf=False)
    def change_consultation_state(self, **kwargs):
        """
        Change consultation state
        Parameters:
        - consultation_id: ID of the consultation (required)
        - state: New state to set (optional)
        - action: Optional action to perform ('start', 'end', 'complete', 'cancel')
        """
        try:
            consultation_id = kwargs.get('consultation_id')
            if not consultation_id:
                return self._error_response('consultation_id is required', 400, 'MISSING_CONSULTATION_ID')
            
            try:
                consultation = request.env['consultation.consultation'].sudo().search([('id', '=', int(consultation_id))], limit=1)
            except ValueError:
                return self._error_response('Invalid consultation_id format', 400, 'INVALID_CONSULTATION_ID')
            
            if not consultation:
                return self._error_response('Consultation not found', 404, 'CONSULTATION_NOT_FOUND')
            
            new_state = kwargs.get('state')
            action = kwargs.get('action')
            
            valid_states = ['draft', 'started', 'ended', 'completed', 'cancelled', 'referral', 
                           'followup', 'admission', 'cross_consultation', 'admission_referral', 
                           'admission_followup', 'admission_cross_consultation', 'discharge']
            
            # Handle specific actions
            if action == 'start':
                try:
                    consultation.action_start()
                    return self._success_response({
                        'consultation_id': consultation.id,
                        'new_state': consultation.state,
                        'start_datetime': consultation.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.start_datetime else None
                    }, 'Consultation started successfully')
                except UserError as e:
                    return self._error_response(str(e), 400, 'START_ERROR')
                
            elif action == 'end':
                consultation.action_end()
                return self._success_response({
                    'consultation_id': consultation.id,
                    'new_state': consultation.state,
                    'end_datetime': consultation.end_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.end_datetime else None
                }, 'Consultation ended successfully')
                
            elif action == 'complete':
                try:
                    consultation.action_complete()
                    return self._success_response({
                        'consultation_id': consultation.id,
                        'new_state': consultation.state,
                        'end_datetime': consultation.end_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.end_datetime else None
                    }, 'Consultation completed successfully')
                except UserError as e:
                    return self._error_response(str(e), 400, 'COMPLETE_ERROR')
                
            elif action == 'cancel':
                consultation.state = 'cancelled'
                return self._success_response({
                    'consultation_id': consultation.id,
                    'new_state': consultation.state
                }, 'Consultation cancelled successfully')
            
            # Handle direct state change
            elif new_state:
                if new_state not in valid_states:
                    return self._error_response(f'Invalid state. Must be one of: {", ".join(valid_states)}', 400, 'INVALID_STATE')
                
                consultation.state = new_state
                return self._success_response({
                    'consultation_id': consultation.id,
                    'new_state': consultation.state
                }, f'Consultation state changed to {new_state} successfully')
            
            else:
                return self._error_response('Either "state" or "action" parameter is required', 400, 'MISSING_STATE_OR_ACTION')
            
        except Exception as e:
            _logger.error(f"Error in change_consultation_state: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

class LookupsAPI(http.Controller):
    
    def _make_response(self, data, status=200):
        """Helper method to create standardized JSON responses"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            ],
            status=status
        )

    def _success_response(self, data=None, message="Success"):
        """Standard success response format"""
        response = {
            'success': True,
            'message': message,
            'data': data or {}
        }
        return self._make_response(response)

    def _error_response(self, message="Error", status=400, error_code=None):
        """Standard error response format"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code,
            'data': None
        }
        return self._make_response(response, status)

    @http.route('/api/campuses', type='http', auth='none', methods=['GET'], csrf=False)
    def get_campuses(self, **kwargs):
        """
        Get list of campuses
        Parameters:
        - active: Filter by active status (true/false, optional)
        - limit: Number of records (default: 100)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply active filter
            active_filter = kwargs.get('active')
            if active_filter is not None:
                if active_filter.lower() in ['true', '1']:
                    domain.append(('active', '=', True))
                elif active_filter.lower() in ['false', '0']:
                    domain.append(('active', '=', False))
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 100))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Search campuses (assuming you have a campus model)
            campuses = request.env['hospital.campus'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='name asc'
            )
            
            total_count = request.env['hospital.campus'].sudo().search_count(domain)
            
            campus_data = []
            for campus in campuses:
                campus_data.append({
                    'id': campus.id,
                    'name': campus.name,
                    'code': campus.code if hasattr(campus, 'code') else '',
                    'address': {
                        'street': campus.street or '',
                        'city': campus.city or '',
                        'state': campus.state or '',
                        'country': campus.country or '',
                        'zip': campus.zip or ''
                    },
                    'contact': {
                        'phone': campus.phone or '',
                        'email': campus.email or '',
                        'website': campus.website or ''
                    },
                    'active': campus.active,
                    'timezone': campus.tz if hasattr(campus, 'tz') else '',
                    'facilities': campus.facilities if hasattr(campus, 'facilities') else ''
                })
            
            return self._success_response({
                'campuses': campus_data,
                'pagination': {
                    'count': len(campus_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            }, 'Campuses retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_campuses: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/doctors', type='http', auth='none', methods=['GET'], csrf=False)
    def get_doctors(self, **kwargs):
        """
        Get list of doctors
        Parameters:
        - campus_id: Filter by campus ID (optional)
        - speciality_id: Filter by speciality ID (optional)
        - active: Filter by active status (true/false, optional)
        - limit: Number of records (default: 100)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply filters
            if kwargs.get('campus_id'):
                try:
                    domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            if kwargs.get('speciality_id'):
                try:
                    domain.append(('speciality_id', '=', int(kwargs.get('speciality_id'))))
                except ValueError:
                    return self._error_response('Invalid speciality_id', 400, 'INVALID_SPECIALITY_ID')
            
            # Apply active filter
            active_filter = kwargs.get('active')
            if active_filter is not None:
                if active_filter.lower() in ['true', '1']:
                    domain.append(('active', '=', True))
                elif active_filter.lower() in ['false', '0']:
                    domain.append(('active', '=', False))
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 100))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Search doctors (hr.employee with doctor role)
            doctors = request.env['hr.employee'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='name asc'
            )
            
            total_count = request.env['hr.employee'].sudo().search_count(domain)
            
            doctor_data = []
            for doctor in doctors:
                doctor_data.append({
                    'id': doctor.id,
                    'name': doctor.name,
                    'email': doctor.work_email or '',
                    'phone': doctor.work_phone or '',
                    'mobile': doctor.mobile_phone or '',
                    'employee_id': doctor.employee_id if hasattr(doctor, 'employee_id') else '',
                    'external_id': doctor.external_id if hasattr(doctor, 'external_id') else '',
                    'speciality': {
                        'id': doctor.speciality_id.id if hasattr(doctor, 'speciality_id') and doctor.speciality_id else None,
                        'name': doctor.speciality_id.name if hasattr(doctor, 'speciality_id') and doctor.speciality_id else ''
                    },
                    'campus': {
                        'id': doctor.campus_id.id if hasattr(doctor, 'campus_id') and doctor.campus_id else None,
                        'name': doctor.campus_id.name if hasattr(doctor, 'campus_id') and doctor.campus_id else ''
                    },
                    'department': {
                        'id': doctor.department_id.id if doctor.department_id else None,
                        'name': doctor.department_id.name if doctor.department_id else ''
                    },
                    'job_position': doctor.job_title or '',
                    'active': doctor.active,
                    'avatar': f'/web/image/hr.employee/{doctor.id}/image_128',
                    'qualifications': doctor.qualifications if hasattr(doctor, 'qualifications') else '',
                    'experience_years': doctor.experience_years if hasattr(doctor, 'experience_years') else 0,
                    'consultation_fee': doctor.consultation_fee if hasattr(doctor, 'consultation_fee') else 0.0
                })
            
            return self._success_response({
                'doctors': doctor_data,
                'pagination': {
                    'count': len(doctor_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'campus_id': kwargs.get('campus_id'),
                    'speciality_id': kwargs.get('speciality_id'),
                    'active': kwargs.get('active')
                }
            }, 'Doctors retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_doctors: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/specialities', type='http', auth='none', methods=['GET'], csrf=False)
    def get_specialities(self, **kwargs):
        """
        Get list of medical specialities
        Parameters:
        - active: Filter by active status (true/false, optional)
        - limit: Number of records (default: 100)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply active filter
            active_filter = kwargs.get('active')
            if active_filter is not None:
                if active_filter.lower() in ['true', '1']:
                    domain.append(('active', '=', True))
                elif active_filter.lower() in ['false', '0']:
                    domain.append(('active', '=', False))
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 100))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Search specialities
            specialities = request.env['hospital.speciality'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='name asc'
            )
            
            total_count = request.env['hospital.speciality'].sudo().search_count(domain)
            
            speciality_data = []
            for speciality in specialities:
                speciality_data.append({
                    'id': speciality.id,
                    'name': speciality.name,
                    'code': speciality.code if hasattr(speciality, 'code') else '',
                    'description': speciality.description if hasattr(speciality, 'description') else '',
                    'active': speciality.active,
                    'doctor_count': speciality.doctor_count if hasattr(speciality, 'doctor_count') else 0,
                    'category': speciality.category if hasattr(speciality, 'category') else ''
                })
            
            return self._success_response({
                'specialities': speciality_data,
                'pagination': {
                    'count': len(speciality_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                }
            }, 'Specialities retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_specialities: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/consultation-types', type='http', auth='none', methods=['GET'], csrf=False)
    def get_consultation_types(self, **kwargs):
        """
        Get list of consultation types
        Parameters:
        - category: Filter by category (optional)
        - active: Filter by active status (true/false, optional)
        """
        try:
            # Get consultation types from configuration or predefined list
            consultation_types = [
                {
                    'id': 1,
                    'name': 'In-person Consultation',
                    'code': 'in_person',
                    'description': 'Face-to-face consultation at the clinic',
                    'category': 'physical',
                    'duration_minutes': 30,
                    'active': True
                },
                {
                    'id': 2,
                    'name': 'Virtual Consultation',
                    'code': 'virtual',
                    'description': 'Online video consultation',
                    'category': 'telehealth',
                    'duration_minutes': 30,
                    'active': True
                },
                {
                    'id': 3,
                    'name': 'Home-Based Consultation',
                    'code': 'home_visit',
                    'description': 'Doctor visits patient at home',
                    'category': 'physical',
                    'duration_minutes': 45,
                    'active': True
                },
                {
                    'id': 4,
                    'name': 'Phone Consultation',
                    'code': 'phone',
                    'description': 'Consultation via phone call',
                    'category': 'telehealth',
                    'duration_minutes': 20,
                    'active': True
                },
                {
                    'id': 5,
                    'name': 'Emergency Consultation',
                    'code': 'emergency',
                    'description': 'Urgent medical consultation',
                    'category': 'emergency',
                    'duration_minutes': 60,
                    'active': True
                },
                {
                    'id': 6,
                    'name': 'Follow-up Consultation',
                    'code': 'followup',
                    'description': 'Follow-up appointment',
                    'category': 'followup',
                    'duration_minutes': 20,
                    'active': True
                }
            ]
            
            # Apply filters
            category_filter = kwargs.get('category')
            if category_filter:
                consultation_types = [ct for ct in consultation_types if ct['category'] == category_filter]
            
            active_filter = kwargs.get('active')
            if active_filter is not None:
                if active_filter.lower() in ['true', '1']:
                    consultation_types = [ct for ct in consultation_types if ct['active']]
                elif active_filter.lower() in ['false', '0']:
                    consultation_types = [ct for ct in consultation_types if not ct['active']]
            
            return self._success_response({
                'consultation_types': consultation_types,
                'count': len(consultation_types),
                'categories': ['physical', 'telehealth', 'emergency', 'followup']
            }, 'Consultation types retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_consultation_types: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/leads', type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def manage_leads(self, **kwargs):
        """
        POST: Create a new lead
        GET: Get leads list
        """
        method = request.httprequest.method
        
        if method == 'POST':
            return self._create_lead(**kwargs)
        elif method == 'GET':
            return self._get_leads(**kwargs)

    def _create_lead(self, **kwargs):
        """
        Create a new lead
        Parameters:
        - caller_name: Caller name (required)
        - caller_mobile: Caller mobile (required, 10 digits)
        - patient_name: Patient name (optional)
        - patient_mobile: Patient mobile (optional, 10 digits)
        - patient_email: Patient email (optional)
        - patient_age: Patient age (optional)
        - patient_sex: male/female/other (optional)
        - caller_email: Caller email (optional)
        - services_looking_for: Services description (optional)
        - address: Address (optional)
        - city: City (optional)
        - state: State (optional)
        - country: Country (optional)
        """
        try:
            # Validate required parameters
            caller_name = kwargs.get('caller_name', '').strip()
            caller_mobile = kwargs.get('caller_mobile', '').strip()
            
            if not caller_name:
                return self._error_response('caller_name is required', 400, 'MISSING_CALLER_NAME')
            
            if not caller_mobile:
                return self._error_response('caller_mobile is required', 400, 'MISSING_CALLER_MOBILE')
            
            # Validate phone number
            if len(caller_mobile) != 10 or not caller_mobile.isdigit():
                return self._error_response('caller_mobile must be exactly 10 digits', 400, 'INVALID_CALLER_MOBILE')
            
            # Check if lead already exists
            existing_lead = request.env['crm.lead'].sudo().search([
                ('caller_mobile', '=', caller_mobile)
            ], limit=1)
            
            if existing_lead:
                return self._error_response('Lead with this mobile number already exists', 409, 'LEAD_ALREADY_EXISTS')
            
            # Validate patient mobile if provided
            patient_mobile = kwargs.get('patient_mobile', '').strip()
            if patient_mobile and (len(patient_mobile) != 10 or not patient_mobile.isdigit()):
                return self._error_response('patient_mobile must be exactly 10 digits', 400, 'INVALID_PATIENT_MOBILE')
            
            # Validate patient sex if provided
            patient_sex = kwargs.get('patient_sex', '').lower()
            if patient_sex and patient_sex not in ['male', 'female', 'other']:
                return self._error_response('patient_sex must be male, female, or other', 400, 'INVALID_PATIENT_SEX')
            
            # Validate patient age if provided
            patient_age = kwargs.get('patient_age')
            if patient_age:
                try:
                    patient_age = int(patient_age)
                    if patient_age < 0 or patient_age > 150:
                        return self._error_response('patient_age must be between 0 and 150', 400, 'INVALID_PATIENT_AGE')
                except ValueError:
                    return self._error_response('patient_age must be a number', 400, 'INVALID_PATIENT_AGE')
            
            # Prepare lead data
            lead_data = {
                'name': caller_name,
                'caller_name': caller_name,
                'caller_mobile': caller_mobile,
                'patient_name': kwargs.get('patient_name', '').strip() or caller_name,
                'state': 'lead',
                'type': 'lead'
            }
            
            # Add optional fields
            optional_fields = {
                'patient_mobile': patient_mobile,
                'patient_email': kwargs.get('patient_email', '').strip(),
                'patient_age': patient_age,
                'patient_sex': patient_sex,
                'caller_email': kwargs.get('caller_email', '').strip(),
                'services_looking_for': kwargs.get('services_looking_for', '').strip(),
                'street': kwargs.get('address', '').strip(),
                'city': kwargs.get('city', '').strip(),
                'state_id': kwargs.get('state'),
                'country_id': kwargs.get('country')
            }
            
            for field, value in optional_fields.items():
                if value:
                    lead_data[field] = value
            
            # Create lead
            lead = request.env['crm.lead'].sudo().create(lead_data)
            
            return self._success_response({
                'lead_id': lead.id,
                'reference': lead.reference or '',
                'caller_name': lead.caller_name,
                'patient_name': lead.patient_name,
                'caller_mobile': lead.caller_mobile,
                'state': lead.state
            }, 'Lead created successfully')
            
        except Exception as e:
            _logger.error(f"Error in _create_lead: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _get_leads(self, **kwargs):
        """
        Get leads list
        Parameters:
        - state: Filter by lead state (optional)
        - created_date_from: Filter from creation date (YYYY-MM-DD, optional)
        - created_date_to: Filter to creation date (YYYY-MM-DD, optional)
        - search: Search in name, mobile, email (optional)
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply filters
            if kwargs.get('state'):
                valid_states = ['lead', 'opportunity', 'quotation', 'won', 'lost']
                if kwargs.get('state') in valid_states:
                    domain.append(('state', '=', kwargs.get('state')))
                else:
                    return self._error_response(f'Invalid state. Must be one of: {", ".join(valid_states)}', 400, 'INVALID_STATE')
            
            # Search filter
            search_query = kwargs.get('search', '').strip()
            if search_query:
                domain.append('|')
                domain.append('|')
                domain.append('|')
                domain.append(('name', 'ilike', search_query))
                domain.append(('caller_mobile', 'ilike', search_query))
                domain.append(('caller_email', 'ilike', search_query))
                domain.append(('patient_name', 'ilike', search_query))
            
            # Date filters
            if kwargs.get('created_date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('created_date_from'), '%Y-%m-%d')
                    domain.append(('create_date', '>=', date_from))
                except ValueError:
                    return self._error_response('Invalid created_date_from format. Use YYYY-MM-DD', 400, 'INVALID_DATE_FROM')
            
            if kwargs.get('created_date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('created_date_to'), '%Y-%m-%d')
                    domain.append(('create_date', '<=', date_to))
                except ValueError:
                    return self._error_response('Invalid created_date_to format. Use YYYY-MM-DD', 400, 'INVALID_DATE_TO')
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 50))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Search leads
            leads = request.env['crm.lead'].sudo().search(
                domain,
                limit=limit,
                offset=offset,
                order='create_date desc'
            )
            
            total_count = request.env['crm.lead'].sudo().search_count(domain)
            
            leads_data = []
            for lead in leads:
                leads_data.append({
                    'id': lead.id,
                    'reference': lead.reference or '',
                    'caller_name': lead.caller_name or '',
                    'patient_name': lead.patient_name or '',
                    'caller_mobile': lead.caller_mobile or '',
                    'patient_mobile': lead.patient_mobile or '',
                    'caller_email': lead.caller_email or '',
                    'patient_email': lead.patient_email or '',
                    'patient_age': lead.patient_age or 0,
                    'patient_sex': lead.patient_sex or '',
                    'services_looking_for': lead.services_looking_for or '',
                    'state': lead.state,
                    'address': {
                        'street': lead.street or '',
                        'city': lead.city or '',
                        'state': lead.state_id.name if lead.state_id else '',
                        'country': lead.country_id.name if lead.country_id else ''
                    },
                    'created_date': lead.create_date.strftime('%Y-%m-%d %H:%M:%S') if lead.create_date else None,
                    'last_activity': lead.date_last_stage_update.strftime('%Y-%m-%d %H:%M:%S') if lead.date_last_stage_update else None
                })
            
            return self._success_response({
                'leads': leads_data,
                'pagination': {
                    'count': len(leads_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'state': kwargs.get('state'),
                    'search': search_query,
                    'created_date_from': kwargs.get('created_date_from'),
                    'created_date_to': kwargs.get('created_date_to')
                }
            }, 'Leads retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in _get_leads: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/lead', type='http', auth='none', methods=['GET', 'PUT'], csrf=False)
    def manage_single_lead(self, **kwargs):
        """
        GET: Get specific lead details
        PUT: Update lead
        Parameters:
        - lead_id: Lead ID (required)
        """
        method = request.httprequest.method
        lead_id = kwargs.get('lead_id')
        
        if not lead_id:
            return self._error_response('lead_id is required', 400, 'MISSING_LEAD_ID')
        
        try:
            lead = request.env['crm.lead'].sudo().search([('id', '=', int(lead_id))], limit=1)
        except ValueError:
            return self._error_response('Invalid lead_id format', 400, 'INVALID_LEAD_ID')
        
        if not lead:
            return self._error_response('Lead not found', 404, 'LEAD_NOT_FOUND')
        
        if method == 'GET':
            return self._get_lead_details(lead)
        elif method == 'PUT':
            return self._update_lead(lead, **kwargs)

    def _get_lead_details(self, lead):
        """Get detailed lead information"""
        try:
            lead_data = {
                'id': lead.id,
                'reference': lead.reference or '',
                'caller_name': lead.caller_name or '',
                'patient_name': lead.patient_name or '',
                'caller_mobile': lead.caller_mobile or '',
                'patient_mobile': lead.patient_mobile or '',
                'caller_email': lead.caller_email or '',
                'patient_email': lead.patient_email or '',
                'patient_age': lead.patient_age or 0,
                'patient_sex': lead.patient_sex or '',
                'services_looking_for': lead.services_looking_for or '',
                'state': lead.state,
                'address': {
                    'street': lead.street or '',
                    'city': lead.city or '',
                    'state': lead.state_id.name if lead.state_id else '',
                    'country': lead.country_id.name if lead.country_id else '',
                    'zip': lead.zip or ''
                },
                'created_date': lead.create_date.strftime('%Y-%m-%d %H:%M:%S') if lead.create_date else None,
                'last_activity': lead.date_last_stage_update.strftime('%Y-%m-%d %H:%M:%S') if lead.date_last_stage_update else None,
                'created_by': lead.user_id.name if lead.user_id else '',
                'company': lead.company_id.name if lead.company_id else '',
                'source': lead.source_id.name if lead.source_id else '',
                'probability': lead.probability or 0,
                'description': lead.description or ''
            }
            
            return self._success_response({
                'lead': lead_data
            }, 'Lead details retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in _get_lead_details: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _update_lead(self, lead, **kwargs):
        """Update lead details"""
        try:
            update_data = {}
            
            # Fields that can be updated
            updatable_fields = {
                'caller_name': 'string',
                'patient_name': 'string',
                'patient_email': 'string',
                'patient_age': 'integer',
                'patient_sex': 'selection',
                'caller_email': 'string',
                'services_looking_for': 'text',
                'address': 'string',
                'city': 'string',
                'state': 'selection',
                'description': 'text'
            }
            
            for field, field_type in updatable_fields.items():
                if field in kwargs:
                    value = kwargs[field]
                    
                    if field_type == 'string' or field_type == 'text':
                        if field == 'address':
                            update_data['street'] = value.strip()
                        else:
                            update_data[field] = value.strip()
                    
                    elif field_type == 'integer':
                        if field == 'patient_age':
                            try:
                                age = int(value)
                                if 0 <= age <= 150:
                                    update_data[field] = age
                                else:
                                    return self._error_response('patient_age must be between 0 and 150', 400, 'INVALID_PATIENT_AGE')
                            except ValueError:
                                return self._error_response('patient_age must be a number', 400, 'INVALID_PATIENT_AGE')
                    
                    elif field_type == 'selection':
                        if field == 'patient_sex':
                            if value.lower() in ['male', 'female', 'other']:
                                update_data[field] = value.lower()
                            else:
                                return self._error_response('patient_sex must be male, female, or other', 400, 'INVALID_PATIENT_SEX')
                        elif field == 'state':
                            valid_states = ['lead', 'opportunity', 'quotation', 'won', 'lost']
                            if value in valid_states:
                                update_data[field] = value
                            else:
                                return self._error_response(f'Invalid state. Must be one of: {", ".join(valid_states)}', 400, 'INVALID_STATE')
            
            # Special handling for name field
            if 'caller_name' in update_data:
                update_data['name'] = update_data['caller_name']
            
            if update_data:
                lead.write(update_data)
                
                return self._success_response({
                    'lead_id': lead.id,
                    'updated_fields': list(update_data.keys()),
                    'lead': self._serialize_lead(lead)
                }, 'Lead updated successfully')
            else:
                return self._error_response('No valid fields provided for update', 400, 'NO_UPDATE_FIELDS')
                
        except Exception as e:
            _logger.error(f"Error in _update_lead: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _serialize_lead(self, lead):
        """Serialize lead object to dictionary"""
        return {
            'id': lead.id,
            'reference': lead.reference or '',
            'caller_name': lead.caller_name or '',
            'patient_name': lead.patient_name or '',
            'caller_mobile': lead.caller_mobile or '',
            'patient_mobile': lead.patient_mobile or '',
            'caller_email': lead.caller_email or '',
            'patient_email': lead.patient_email or '',
            'patient_age': lead.patient_age or 0,
            'patient_sex': lead.patient_sex or '',
            'services_looking_for': lead.services_looking_for or '',
            'state': lead.state,
            'address': {
                'street': lead.street or '',
                'city': lead.city or '',
                'state': lead.state_id.name if lead.state_id else '',
                'country': lead.country_id.name if lead.country_id else ''
            },
            'created_date': lead.create_date.strftime('%Y-%m-%d %H:%M:%S') if lead.create_date else None
        }

    @http.route('/api/psychologists', type='http', auth='none', methods=['GET'], csrf=False)
    def get_psychologists(self, **kwargs):
        """
        Get list of psychologists
        Parameters:
        - hospital_id: Filter by hospital/school ID (optional)
        - grade_id: Filter by grade/department ID (optional)
        - classroom_id: Filter by classroom ID (optional)
        - active: Filter by active status (true/false, optional)
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            psychologists = request.env['res.users'].sudo()
            
            if kwargs.get('hospital_id'):
                try:
                    hospital = request.env['hospital.hospital'].sudo().browse(int(kwargs.get('hospital_id')))
                    if hospital.exists():
                        psychologists = hospital.psychologist_ids
                    else:
                        return self._error_response(f'Hospital with ID {kwargs.get("hospital_id")} not found', 404, 'HOSPITAL_NOT_FOUND')
                except ValueError:
                    return self._error_response('Invalid hospital_id', 400, 'INVALID_HOSPITAL_ID')
            
            elif kwargs.get('grade_id'):
                try:
                    grade = request.env['hospital.grade'].sudo().browse(int(kwargs.get('grade_id')))
                    if grade.exists():
                        psychologists = grade.psychologist_ids
                        if grade.school_id:
                            psychologists |= grade.school_id.psychologist_ids
                    else:
                        return self._error_response(f'Grade with ID {kwargs.get("grade_id")} not found', 404, 'GRADE_NOT_FOUND')
                except ValueError:
                    return self._error_response('Invalid grade_id', 400, 'INVALID_GRADE_ID')
            
            elif kwargs.get('classroom_id'):
                try:
                    classroom = request.env['hospital.classroom'].sudo().browse(int(kwargs.get('classroom_id')))
                    if classroom.exists():
                        psychologists = classroom.all_psychologist_ids
                    else:
                        return self._error_response(f'Classroom with ID {kwargs.get("classroom_id")} not found', 404, 'CLASSROOM_NOT_FOUND')
                except ValueError:
                    return self._error_response('Invalid classroom_id', 400, 'INVALID_CLASSROOM_ID')
            
            else:
                # Get all psychologists
                hospital_psychologists = request.env['hospital.hospital'].sudo().search([]).mapped('psychologist_ids')
                grade_psychologists = request.env['hospital.grade'].sudo().search([]).mapped('psychologist_ids')
                classroom_psychologists = request.env['hospital.classroom'].sudo().search([]).mapped('psychologist_ids')
                
                psychologists = hospital_psychologists | grade_psychologists | classroom_psychologists
            
            # Apply active filter
            active_filter = kwargs.get('active')
            if active_filter is not None:
                if active_filter.lower() in ['true', '1']:
                    psychologists = psychologists.filtered(lambda p: p.active)
                elif active_filter.lower() in ['false', '0']:
                    psychologists = psychologists.filtered(lambda p: not p.active)
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 50))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            # Apply pagination manually since we're working with recordsets
            total_count = len(psychologists)
            psychologists = psychologists[offset:offset + limit]
            
            psychologist_data = []
            for psychologist in psychologists:
                # Get assignments for this psychologist
                assigned_hospitals = request.env['hospital.hospital'].sudo().search([
                    ('psychologist_ids', 'in', [psychologist.id])
                ])
                assigned_grades = request.env['hospital.grade'].sudo().search([
                    ('psychologist_ids', 'in', [psychologist.id])
                ])
                assigned_classrooms = request.env['hospital.classroom'].sudo().search([
                    ('psychologist_ids', 'in', [psychologist.id])
                ])
                
                # Calculate total students
                total_students = 0
                for classroom in assigned_classrooms:
                    total_students += classroom.student_count
                for grade in assigned_grades:
                    total_students += grade.total_students
                for hospital in assigned_hospitals:
                    total_students += hospital.total_students
                
                psychologist_info = {
                    'id': psychologist.id,
                    'name': psychologist.name,
                    'email': psychologist.email or '',
                    'phone': psychologist.phone or '',
                    'login': psychologist.login,
                    'active': psychologist.active,
                    'avatar': f'/web/image/res.users/{psychologist.id}/image_128',
                    'total_students': total_students,
                    'assignments': {
                        'hospitals': [{'id': h.id, 'name': h.name, 'type': h.type} for h in assigned_hospitals],
                        'grades': [{'id': g.id, 'name': g.name, 'school': g.school_id.name if g.school_id else ''} for g in assigned_grades],
                        'classrooms': [{'id': c.id, 'name': c.name, 'grade': c.grade_id.name if c.grade_id else '', 'school': c.school_id.name if c.school_id else ''} for c in assigned_classrooms]
                    }
                }
                
                psychologist_data.append(psychologist_info)
            
            return self._success_response({
                'psychologists': psychologist_data,
                'pagination': {
                    'count': len(psychologist_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'filters': {
                    'hospital_id': kwargs.get('hospital_id'),
                    'grade_id': kwargs.get('grade_id'),
                    'classroom_id': kwargs.get('classroom_id'),
                    'active': kwargs.get('active')
                }
            }, 'Psychologists retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_psychologists: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/students', type='http', auth='none', methods=['GET'], csrf=False)
    def get_students(self, **kwargs):
        """
        Get students for a psychologist
        Parameters:
        - psychologist_id: ID of the psychologist (required)
        - classroom_id: Filter by classroom ID (optional)
        - grade_id: Filter by grade ID (optional)
        - hospital_id: Filter by hospital ID (optional)
        - active: Filter by active status (true/false, optional)
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            psychologist_id = kwargs.get('psychologist_id')
            if not psychologist_id:
                return self._error_response('psychologist_id is required', 400, 'MISSING_PSYCHOLOGIST_ID')
            
            try:
                psychologist_id = int(psychologist_id)
            except ValueError:
                return self._error_response('Invalid psychologist_id format', 400, 'INVALID_PSYCHOLOGIST_ID')
            
            # Get students through various assignments
            students_from_classrooms = request.env['res.partner']
            students_from_grades = request.env['res.partner']
            students_from_hospitals = request.env['res.partner']
            
            # Method 1: Get students through classroom assignments
            classroom_domain = [('psychologist_ids', 'in', [psychologist_id])]
            if kwargs.get('classroom_id'):
                try:
                    classroom_domain.append(('id', '=', int(kwargs.get('classroom_id'))))
                except ValueError:
                    return self._error_response('Invalid classroom_id', 400, 'INVALID_CLASSROOM_ID')
            
            classrooms = request.env['hospital.classroom'].sudo().search(classroom_domain)
            for classroom in classrooms:
                students_from_classrooms |= classroom.student_ids
            
            # Method 2: Get students through grade assignments
            grade_domain = [('psychologist_ids', 'in', [psychologist_id])]
            if kwargs.get('grade_id'):
                try:
                    grade_domain.append(('id', '=', int(kwargs.get('grade_id'))))
                except ValueError:
                    return self._error_response('Invalid grade_id', 400, 'INVALID_GRADE_ID')
            
            grades = request.env['hospital.grade'].sudo().search(grade_domain)
            for grade in grades:
                for classroom in grade.classroom_ids:
                    students_from_grades |= classroom.student_ids
            
            # Method 3: Get students through hospital assignments
            hospital_domain = [('psychologist_ids', 'in', [psychologist_id])]
            if kwargs.get('hospital_id'):
                try:
                    hospital_domain.append(('id', '=', int(kwargs.get('hospital_id'))))
                except ValueError:
                    return self._error_response('Invalid hospital_id', 400, 'INVALID_HOSPITAL_ID')
            
            hospitals = request.env['hospital.hospital'].sudo().search(hospital_domain)
            for hospital in hospitals:
                for classroom in hospital.classroom_ids:
                    students_from_hospitals |= classroom.student_ids
            
            # Combine all students and remove duplicates
            all_students = students_from_classrooms | students_from_grades | students_from_hospitals
            
            # Apply active filter
            active_filter = kwargs.get('active')
            if active_filter is not None:
                if active_filter.lower() in ['true', '1']:
                    all_students = all_students.filtered(lambda s: s.active)
                elif active_filter.lower() in ['false', '0']:
                    all_students = all_students.filtered(lambda s: not s.active)
            
            # Pagination
            try:
                limit = int(kwargs.get('limit', 50))
                offset = int(kwargs.get('offset', 0))
            except ValueError:
                return self._error_response('Invalid pagination parameters', 400, 'INVALID_PAGINATION')
            
            total_count = len(all_students)
            all_students = all_students[offset:offset + limit]
            
            student_data = []
            for student in all_students:
                # Get student's classroom information
                student_classrooms = classrooms.filtered(lambda c: student in c.student_ids)
                
                student_info = {
                    'id': student.id,
                    'name': student.name,
                    'email': student.email or '',
                    'phone': student.phone or '',
                    'mobile': student.mobile or '',
                    'active': student.active,
                    'classrooms': []
                }
                
                # Add classroom information
                for classroom in student_classrooms:
                    student_info['classrooms'].append({
                        'id': classroom.id,
                        'name': classroom.name,
                        'grade': classroom.grade_id.name if classroom.grade_id else '',
                        'school': classroom.school_id.name if classroom.school_id else ''
                    })
                
                student_data.append(student_info)
            
            return self._success_response({
                'students': student_data,
                'pagination': {
                    'count': len(student_data),
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + limit < total_count
                },
                'psychologist_id': psychologist_id,
                'filters': {
                    'classroom_id': kwargs.get('classroom_id'),
                    'grade_id': kwargs.get('grade_id'),
                    'hospital_id': kwargs.get('hospital_id'),
                    'active': kwargs.get('active')
                }
            }, 'Students retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_students: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')
        

class AnalyticsAPI(http.Controller):
    
    def _make_response(self, data, status=200):
        """Helper method to create standardized JSON responses"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            ],
            status=status
        )

    def _success_response(self, data=None, message="Success"):
        """Standard success response format"""
        response = {
            'success': True,
            'message': message,
            'data': data or {}
        }
        return self._make_response(response)

    def _error_response(self, message="Error", status=400, error_code=None):
        """Standard error response format"""
        response = {
            'success': False,
            'message': message,
            'error_code': error_code,
            'data': None
        }
        return self._make_response(response, status)

    @http.route('/api/dashboard', type='http', auth='none', methods=['GET'], csrf=False)
    def get_dashboard_overview(self, **kwargs):
        """
        Get dashboard overview statistics
        Parameters:
        - date: Date for dashboard (YYYY-MM-DD, default: today)
        - campus_id: Filter by campus ID (optional)
        - doctor_id: Filter by doctor ID (optional)
        - range_days: Number of days to include in calculations (default: 7)
        """
        try:
            # Parse date parameter
            date_str = kwargs.get('date', datetime.now().strftime('%Y-%m-%d'))
            try:
                dashboard_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return self._error_response('Invalid date format. Use YYYY-MM-DD', 400, 'INVALID_DATE')
            
            # Parse range days
            try:
                range_days = int(kwargs.get('range_days', 7))
            except ValueError:
                return self._error_response('Invalid range_days. Must be a number', 400, 'INVALID_RANGE_DAYS')
            
            # Calculate date range
            start_date = dashboard_date - timedelta(days=range_days - 1)
            end_date = dashboard_date + timedelta(days=1)  # Include the dashboard date
            
            # Build domain filters
            appointment_domain = [
                ('start_datetime', '>=', datetime.combine(start_date, datetime.min.time())),
                ('start_datetime', '<', datetime.combine(end_date, datetime.min.time()))
            ]
            
            if kwargs.get('campus_id'):
                try:
                    appointment_domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            if kwargs.get('doctor_id'):
                try:
                    appointment_domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
                except ValueError:
                    return self._error_response('Invalid doctor_id', 400, 'INVALID_DOCTOR_ID')
            
            # Get today's statistics
            today_domain = [
                ('start_datetime', '>=', datetime.combine(dashboard_date, datetime.min.time())),
                ('start_datetime', '<', datetime.combine(dashboard_date + timedelta(days=1), datetime.min.time()))
            ] + ([('campus_id', '=', int(kwargs.get('campus_id')))] if kwargs.get('campus_id') else []) + \
              ([('doctor_id', '=', int(kwargs.get('doctor_id')))] if kwargs.get('doctor_id') else [])
            
            # Calculate statistics
            appointments_env = request.env['slot.booking'].sudo()
            
            # Today's appointments
            today_total = appointments_env.search_count(today_domain)
            today_booked = appointments_env.search_count(today_domain + [('availability', '=', 'booked')])
            today_confirmed = appointments_env.search_count(today_domain + [('availability', '=', 'confirm')])
            today_checkedin = appointments_env.search_count(today_domain + [('availability', '=', 'checked_in')])
            today_consulting = appointments_env.search_count(today_domain + [('availability', '=', 'consulting')])
            today_completed = appointments_env.search_count(today_domain + [('availability', '=', 'completed')])
            today_cancelled = appointments_env.search_count(today_domain + [('availability', '=', 'cancelled')])
            today_noshow = appointments_env.search_count(today_domain + [('availability', '=', 'no_show')])
            
            # Range statistics
            range_total = appointments_env.search_count(appointment_domain)
            range_completed = appointments_env.search_count(appointment_domain + [('availability', '=', 'completed')])
            range_cancelled = appointments_env.search_count(appointment_domain + [('availability', '=', 'cancelled')])
            
            # Calculate utilization rate
            utilization_rate = (range_completed / range_total * 100) if range_total > 0 else 0
            
            # Get active doctors and campuses count
            total_doctors = request.env['hr.employee'].sudo().search_count([('active', '=', True)])
            total_campuses = request.env['hospital.campus'].sudo().search_count([('active', '=', True)])
            
            # Recent activity
            recent_appointments = appointments_env.search(
                today_domain,
                order='slot_booked_at desc',
                limit=5
            )
            
            recent_activity = []
            for appointment in recent_appointments:
                recent_activity.append({
                    'id': appointment.id,
                    'patient_name': appointment.patient_name or '',
                    'doctor_name': appointment.doctor_id.name if appointment.doctor_id else '',
                    'time': appointment.start_datetime.strftime('%H:%M') if appointment.start_datetime else '',
                    'status': appointment.availability,
                    'booked_at': appointment.slot_booked_at.strftime('%H:%M') if appointment.slot_booked_at else ''
                })
            
            dashboard_data = {
                'overview': {
                    'date': dashboard_date.strftime('%Y-%m-%d'),
                    'range_days': range_days,
                    'total_appointments_today': today_total,
                    'total_doctors': total_doctors,
                    'total_campuses': total_campuses,
                    'utilization_rate': round(utilization_rate, 1)
                },
                'today_summary': {
                    'total': today_total,
                    'booked': today_booked,
                    'confirmed': today_confirmed,
                    'checked_in': today_checkedin,
                    'consulting': today_consulting,
                    'completed': today_completed,
                    'cancelled': today_cancelled,
                    'no_show': today_noshow
                },
                'range_summary': {
                    'period': f'{start_date.strftime("%Y-%m-%d")} to {dashboard_date.strftime("%Y-%m-%d")}',
                    'total_appointments': range_total,
                    'completed_appointments': range_completed,
                    'cancelled_appointments': range_cancelled,
                    'completion_rate': round((range_completed / range_total * 100) if range_total > 0 else 0, 1),
                    'cancellation_rate': round((range_cancelled / range_total * 100) if range_total > 0 else 0, 1)
                },
                'recent_activity': recent_activity,
                'filters_applied': {
                    'campus_id': kwargs.get('campus_id'),
                    'doctor_id': kwargs.get('doctor_id')
                }
            }
            
            return self._success_response(dashboard_data, 'Dashboard overview retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_dashboard_overview: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/analytics', type='http', auth='none', methods=['GET'], csrf=False)
    def get_appointment_analytics(self, **kwargs):
        """
        Get detailed appointment analytics
        Parameters:
        - date_from: Start date (YYYY-MM-DD, default: 30 days ago)
        - date_to: End date (YYYY-MM-DD, default: today)
        - campus_id: Filter by campus ID (optional)
        - doctor_id: Filter by doctor ID (optional)
        - group_by: Group results by ('day', 'week', 'month', default: 'day')
        """
        try:
            # Parse date parameters
            today = datetime.now().date()
            date_from_str = kwargs.get('date_from', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
            date_to_str = kwargs.get('date_to', today.strftime('%Y-%m-%d'))
            
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            except ValueError:
                return self._error_response('Invalid date format. Use YYYY-MM-DD', 400, 'INVALID_DATE')
            
            if date_from > date_to:
                return self._error_response('date_from cannot be later than date_to', 400, 'INVALID_DATE_RANGE')
            
            # Parse group_by parameter
            group_by = kwargs.get('group_by', 'day')
            if group_by not in ['day', 'week', 'month']:
                return self._error_response('Invalid group_by. Must be day, week, or month', 400, 'INVALID_GROUP_BY')
            
            # Build domain
            domain = [
                ('start_datetime', '>=', datetime.combine(date_from, datetime.min.time())),
                ('start_datetime', '<=', datetime.combine(date_to, datetime.max.time()))
            ]
            
            if kwargs.get('campus_id'):
                try:
                    domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            if kwargs.get('doctor_id'):
                try:
                    domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
                except ValueError:
                    return self._error_response('Invalid doctor_id', 400, 'INVALID_DOCTOR_ID')
            
            appointments_env = request.env['slot.booking'].sudo()
            
            # Get total statistics
            total_appointments = appointments_env.search_count(domain)
            completed_appointments = appointments_env.search_count(domain + [('availability', '=', 'completed')])
            cancelled_appointments = appointments_env.search_count(domain + [('availability', '=', 'cancelled')])
            no_show_appointments = appointments_env.search_count(domain + [('availability', '=', 'no_show')])
            
            # Status breakdown
            status_breakdown = {}
            statuses = ['open', 'booked', 'confirm', 'checked_in', 'consulting', 'completed', 'cancelled', 'no_show']
            for status in statuses:
                status_breakdown[status] = appointments_env.search_count(domain + [('availability', '=', status)])
            
            # Consultation type breakdown
            consultation_types = appointments_env.search(domain).mapped('consultation_type')
            consultation_type_breakdown = {}
            for cons_type in set(consultation_types):
                if cons_type:
                    consultation_type_breakdown[cons_type] = appointments_env.search_count(
                        domain + [('consultation_type', '=', cons_type)]
                    )
            
            # Time series data
            time_series = []
            current_date = date_from
            
            while current_date <= date_to:
                if group_by == 'day':
                    period_start = current_date
                    period_end = current_date
                    next_date = current_date + timedelta(days=1)
                    period_label = current_date.strftime('%Y-%m-%d')
                elif group_by == 'week':
                    # Start of week (Monday)
                    period_start = current_date - timedelta(days=current_date.weekday())
                    period_end = period_start + timedelta(days=6)
                    next_date = period_end + timedelta(days=1)
                    period_label = f"Week of {period_start.strftime('%Y-%m-%d')}"
                else:  # month
                    period_start = current_date.replace(day=1)
                    if period_start.month == 12:
                        period_end = period_start.replace(year=period_start.year + 1, month=1) - timedelta(days=1)
                    else:
                        period_end = period_start.replace(month=period_start.month + 1) - timedelta(days=1)
                    next_date = period_end + timedelta(days=1)
                    period_label = period_start.strftime('%Y-%m')
                
                period_domain = domain + [
                    ('start_datetime', '>=', datetime.combine(period_start, datetime.min.time())),
                    ('start_datetime', '<=', datetime.combine(period_end, datetime.max.time()))
                ]
                
                period_total = appointments_env.search_count(period_domain)
                period_completed = appointments_env.search_count(period_domain + [('availability', '=', 'completed')])
                period_cancelled = appointments_env.search_count(period_domain + [('availability', '=', 'cancelled')])
                
                time_series.append({
                    'period': period_label,
                    'total': period_total,
                    'completed': period_completed,
                    'cancelled': period_cancelled,
                    'completion_rate': round((period_completed / period_total * 100) if period_total > 0 else 0, 1)
                })
                
                current_date = next_date
                if current_date > date_to:
                    break
            
            # Doctor performance (if not filtering by specific doctor)
            doctor_performance = []
            if not kwargs.get('doctor_id'):
                doctor_data = appointments_env.read_group(
                    domain + [('doctor_id', '!=', False)],
                    ['doctor_id', 'availability'],
                    ['doctor_id', 'availability'],
                    lazy=False
                )
                
                doctor_stats = {}
                for data in doctor_data:
                    doctor_id = data['doctor_id'][0]
                    status = data['availability']
                    count = data['__count']
                    
                    if doctor_id not in doctor_stats:
                        doctor_stats[doctor_id] = {
                            'doctor_name': data['doctor_id'][1],
                            'total': 0,
                            'completed': 0,
                            'cancelled': 0
                        }
                    
                    doctor_stats[doctor_id]['total'] += count
                    if status == 'completed':
                        doctor_stats[doctor_id]['completed'] += count
                    elif status == 'cancelled':
                        doctor_stats[doctor_id]['cancelled'] += count
                
                for doctor_id, stats in doctor_stats.items():
                    stats['completion_rate'] = round((stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
                    stats['cancellation_rate'] = round((stats['cancelled'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1)
                    doctor_performance.append({
                        'doctor_id': doctor_id,
                        **stats
                    })
                
                # Sort by total appointments descending
                doctor_performance.sort(key=lambda x: x['total'], reverse=True)
                doctor_performance = doctor_performance[:10]  # Top 10 doctors
            
            analytics_data = {
                'summary': {
                    'period': f'{date_from.strftime("%Y-%m-%d")} to {date_to.strftime("%Y-%m-%d")}',
                    'total_appointments': total_appointments,
                    'completed_appointments': completed_appointments,
                    'cancelled_appointments': cancelled_appointments,
                    'no_show_appointments': no_show_appointments,
                    'completion_rate': round((completed_appointments / total_appointments * 100) if total_appointments > 0 else 0, 1),
                    'cancellation_rate': round((cancelled_appointments / total_appointments * 100) if total_appointments > 0 else 0, 1),
                    'no_show_rate': round((no_show_appointments / total_appointments * 100) if total_appointments > 0 else 0, 1)
                },
                'status_breakdown': status_breakdown,
                'consultation_type_breakdown': consultation_type_breakdown,
                'time_series': time_series,
                'doctor_performance': doctor_performance,
                'filters_applied': {
                    'date_from': date_from_str,
                    'date_to': date_to_str,
                    'campus_id': kwargs.get('campus_id'),
                    'doctor_id': kwargs.get('doctor_id'),
                    'group_by': group_by
                }
            }
            
            return self._success_response(analytics_data, 'Analytics retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_appointment_analytics: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/schedule', type='http', auth='none', methods=['GET'], csrf=False)
    def get_doctor_schedule(self, **kwargs):
        """
        Get doctor schedule
        Parameters:
        - doctor_id: Doctor ID (required)
        - date: Date for schedule (YYYY-MM-DD, default: today)
        - days: Number of days to include (default: 1)
        """
        try:
            doctor_id = kwargs.get('doctor_id')
            if not doctor_id:
                return self._error_response('doctor_id is required', 400, 'MISSING_DOCTOR_ID')
            
            try:
                doctor_id = int(doctor_id)
            except ValueError:
                return self._error_response('Invalid doctor_id format', 400, 'INVALID_DOCTOR_ID')
            
            # Verify doctor exists
            doctor = request.env['hr.employee'].sudo().search([('id', '=', doctor_id)], limit=1)
            if not doctor:
                return self._error_response('Doctor not found', 404, 'DOCTOR_NOT_FOUND')
            
            # Parse date parameter
            date_str = kwargs.get('date', datetime.now().strftime('%Y-%m-%d'))
            try:
                schedule_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return self._error_response('Invalid date format. Use YYYY-MM-DD', 400, 'INVALID_DATE')
            
            # Parse days parameter
            try:
                days = int(kwargs.get('days', 1))
                if days < 1 or days > 30:
                    return self._error_response('days must be between 1 and 30', 400, 'INVALID_DAYS')
            except ValueError:
                return self._error_response('Invalid days format', 400, 'INVALID_DAYS')
            
            # Get schedule for the specified period
            end_date = schedule_date + timedelta(days=days - 1)
            domain = [
                ('doctor_id', '=', doctor_id),
                ('start_datetime', '>=', datetime.combine(schedule_date, datetime.min.time())),
                ('start_datetime', '<=', datetime.combine(end_date, datetime.max.time()))
            ]
            
            appointments = request.env['slot.booking'].sudo().search(
                domain,
                order='start_datetime asc'
            )
            
            # Group appointments by date
            schedule_by_date = {}
            for appointment in appointments:
                if appointment.start_datetime:
                    appt_date = appointment.start_datetime.date().strftime('%Y-%m-%d')
                    if appt_date not in schedule_by_date:
                        schedule_by_date[appt_date] = {
                            'date': appt_date,
                            'appointments': [],
                            'summary': {
                                'total': 0,
                                'booked': 0,
                                'available': 0,
                                'completed': 0,
                                'cancelled': 0
                            }
                        }
                    
                    appointment_data = {
                        'id': appointment.id,
                        'time': appointment.start_datetime.strftime('%H:%M') if appointment.start_datetime else '',
                        'duration': appointment.duration or 0,
                        'status': appointment.availability,
                        'consultation_type': appointment.consultation_type or '',
                        'patient': {
                            'name': appointment.patient_name or '',
                            'mobile': appointment.lead_id.caller_mobile if appointment.lead_id else ''
                        } if appointment.availability != 'open' else None,
                        'campus': appointment.campus_id.name if appointment.campus_id else '',
                        'notes': appointment.notes or ''
                    }
                    
                    schedule_by_date[appt_date]['appointments'].append(appointment_data)
                    schedule_by_date[appt_date]['summary']['total'] += 1
                    
                    if appointment.availability == 'open':
                        schedule_by_date[appt_date]['summary']['available'] += 1
                    elif appointment.availability in ['booked', 'confirm', 'checked_in', 'consulting']:
                        schedule_by_date[appt_date]['summary']['booked'] += 1
                    elif appointment.availability == 'completed':
                        schedule_by_date[appt_date]['summary']['completed'] += 1
                    elif appointment.availability in ['cancelled', 'no_show']:
                        schedule_by_date[appt_date]['summary']['cancelled'] += 1
            
            # Convert to list and sort by date
            schedule_list = list(schedule_by_date.values())
            schedule_list.sort(key=lambda x: x['date'])
            
            # Calculate overall summary
            overall_summary = {
                'total': sum(day['summary']['total'] for day in schedule_list),
                'booked': sum(day['summary']['booked'] for day in schedule_list),
                'available': sum(day['summary']['available'] for day in schedule_list),
                'completed': sum(day['summary']['completed'] for day in schedule_list),
                'cancelled': sum(day['summary']['cancelled'] for day in schedule_list)
            }
            
            schedule_data = {
                'doctor': {
                    'id': doctor.id,
                    'name': doctor.name,
                    'email': doctor.work_email or '',
                    'phone': doctor.work_phone or '',
                    'speciality': doctor.speciality_id.name if hasattr(doctor, 'speciality_id') and doctor.speciality_id else ''
                },
                'period': {
                    'start_date': schedule_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': days
                },
                'overall_summary': overall_summary,
                'schedule': schedule_list
            }
            
            return self._success_response(schedule_data, 'Doctor schedule retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in get_doctor_schedule: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    @http.route('/api/reports', type='http', auth='none', methods=['GET'], csrf=False)
    def generate_report(self, **kwargs):
        """
        Generate various reports
        Parameters:
        - report_type: Type of report ('appointments', 'doctors', 'campuses', 'revenue')
        - format: Format of report ('json', 'summary', default: 'json')
        - date_from: Start date (YYYY-MM-DD, optional)
        - date_to: End date (YYYY-MM-DD, optional)
        - campus_id: Filter by campus ID (optional)
        - doctor_id: Filter by doctor ID (optional)
        """
        try:
            report_type = kwargs.get('report_type', 'appointments')
            if report_type not in ['appointments', 'doctors', 'campuses', 'revenue']:
                return self._error_response('Invalid report_type. Must be appointments, doctors, campuses, or revenue', 400, 'INVALID_REPORT_TYPE')
            
            report_format = kwargs.get('format', 'json')
            if report_format not in ['json', 'summary']:
                return self._error_response('Invalid format. Must be json or summary', 400, 'INVALID_FORMAT')
            
            # Date parameters
            today = datetime.now().date()
            date_from_str = kwargs.get('date_from', (today - timedelta(days=30)).strftime('%Y-%m-%d'))
            date_to_str = kwargs.get('date_to', today.strftime('%Y-%m-%d'))
            
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date()
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date()
            except ValueError:
                return self._error_response('Invalid date format. Use YYYY-MM-DD', 400, 'INVALID_DATE')
            
            # Build base domain
            domain = [
                ('start_datetime', '>=', datetime.combine(date_from, datetime.min.time())),
                ('start_datetime', '<=', datetime.combine(date_to, datetime.max.time()))
            ]
            
            if kwargs.get('campus_id'):
                try:
                    domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
                except ValueError:
                    return self._error_response('Invalid campus_id', 400, 'INVALID_CAMPUS_ID')
            
            if kwargs.get('doctor_id'):
                try:
                    domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
                except ValueError:
                    return self._error_response('Invalid doctor_id', 400, 'INVALID_DOCTOR_ID')
            
            if report_type == 'appointments':
                report_data = self._generate_appointments_report(domain, report_format, date_from, date_to)
            elif report_type == 'doctors':
                report_data = self._generate_doctors_report(domain, report_format, date_from, date_to)
            elif report_type == 'campuses':
                report_data = self._generate_campuses_report(domain, report_format, date_from, date_to)
            elif report_type == 'revenue':
                report_data = self._generate_revenue_report(domain, report_format, date_from, date_to)
            
            report_data['metadata'] = {
                'report_type': report_type,
                'format': report_format,
                'period': f'{date_from.strftime("%Y-%m-%d")} to {date_to.strftime("%Y-%m-%d")}',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filters': {
                    'campus_id': kwargs.get('campus_id'),
                    'doctor_id': kwargs.get('doctor_id')
                }
            }
            
            return self._success_response(report_data, f'{report_type.title()} report generated successfully')
            
        except Exception as e:
            _logger.error(f"Error in generate_report: {str(e)}")
            return self._error_response('Internal server error', 500, 'INTERNAL_ERROR')

    def _generate_appointments_report(self, domain, report_format, date_from, date_to):
        """Generate appointments report"""
        appointments_env = request.env['slot.booking'].sudo()
        
        # Basic statistics
        total_appointments = appointments_env.search_count(domain)
        completed = appointments_env.search_count(domain + [('availability', '=', 'completed')])
        cancelled = appointments_env.search_count(domain + [('availability', '=', 'cancelled')])
        no_show = appointments_env.search_count(domain + [('availability', '=', 'no_show')])
        
        report_data = {
            'summary': {
                'total_appointments': total_appointments,
                'completed': completed,
                'cancelled': cancelled,
                'no_show': no_show,
                'completion_rate': round((completed / total_appointments * 100) if total_appointments > 0 else 0, 1),
                'cancellation_rate': round((cancelled / total_appointments * 100) if total_appointments > 0 else 0, 1)
            }
        }
        
        if report_format == 'json':
            appointments = appointments_env.search(domain, order='start_datetime desc', limit=1000)
            report_data['appointments'] = []
            
            for appointment in appointments:
                report_data['appointments'].append({
                    'id': appointment.id,
                    'reference': appointment.name,
                    'date': appointment.start_datetime.strftime('%Y-%m-%d') if appointment.start_datetime else '',
                    'time': appointment.start_datetime.strftime('%H:%M') if appointment.start_datetime else '',
                    'patient_name': appointment.patient_name or '',
                    'doctor_name': appointment.doctor_id.name if appointment.doctor_id else '',
                    'campus_name': appointment.campus_id.name if appointment.campus_id else '',
                    'consultation_type': appointment.consultation_type or '',
                    'status': appointment.availability,
                    'amount': appointment.amount or 0,
                    'payment_mode': appointment.payment_mode or ''
                })
        
        return report_data

    def _generate_doctors_report(self, domain, report_format, date_from, date_to):
        """Generate doctors performance report"""
        appointments_env = request.env['slot.booking'].sudo()
        
        # Get doctor statistics
        doctor_data = appointments_env.read_group(
            domain + [('doctor_id', '!=', False)],
            ['doctor_id', 'availability'],
            ['doctor_id', 'availability'],
            lazy=False
        )
        
        doctor_stats = {}
        for data in doctor_data:
            doctor_id = data['doctor_id'][0]
            status = data['availability']
            count = data['__count']
            
            if doctor_id not in doctor_stats:
                doctor_stats[doctor_id] = {
                    'doctor_id': doctor_id,
                    'doctor_name': data['doctor_id'][1],
                    'total': 0,
                    'completed': 0,
                    'cancelled': 0,
                    'no_show': 0
                }
            
            doctor_stats[doctor_id]['total'] += count
            if status == 'completed':
                doctor_stats[doctor_id]['completed'] += count
            elif status == 'cancelled':
                doctor_stats[doctor_id]['cancelled'] += count
            elif status == 'no_show':
                doctor_stats[doctor_id]['no_show'] += count
        
        # Calculate rates
        for stats in doctor_stats.values():
            total = stats['total']
            stats['completion_rate'] = round((stats['completed'] / total * 100) if total > 0 else 0, 1)
            stats['cancellation_rate'] = round((stats['cancelled'] / total * 100) if total > 0 else 0, 1)
            stats['no_show_rate'] = round((stats['no_show'] / total * 100) if total > 0 else 0, 1)
        
        doctors_list = list(doctor_stats.values())
        doctors_list.sort(key=lambda x: x['total'], reverse=True)
        
        return {
            'summary': {
                'total_doctors': len(doctors_list),
                'total_appointments': sum(d['total'] for d in doctors_list),
                'avg_appointments_per_doctor': round(sum(d['total'] for d in doctors_list) / len(doctors_list) if doctors_list else 0, 1)
            },
            'doctors': doctors_list
        }

    def _generate_campuses_report(self, domain, report_format, date_from, date_to):
        """Generate campuses utilization report"""
        appointments_env = request.env['slot.booking'].sudo()
        
        # Get campus statistics
        campus_data = appointments_env.read_group(
            domain + [('campus_id', '!=', False)],
            ['campus_id', 'availability'],
            ['campus_id', 'availability'],
            lazy=False
        )
        
        campus_stats = {}
        for data in campus_data:
            campus_id = data['campus_id'][0]
            status = data['availability']
            count = data['__count']
            
            if campus_id not in campus_stats:
                campus_stats[campus_id] = {
                    'campus_id': campus_id,
                    'campus_name': data['campus_id'][1],
                    'total': 0,
                    'completed': 0,
                    'cancelled': 0
                }
            
            campus_stats[campus_id]['total'] += count
            if status == 'completed':
                campus_stats[campus_id]['completed'] += count
            elif status in ['cancelled', 'no_show']:
                campus_stats[campus_id]['cancelled'] += count
        
        # Calculate utilization rates
        for stats in campus_stats.values():
            total = stats['total']
            stats['utilization_rate'] = round((stats['completed'] / total * 100) if total > 0 else 0, 1)
        
        campuses_list = list(campus_stats.values())
        campuses_list.sort(key=lambda x: x['total'], reverse=True)
        
        return {
            'summary': {
                'total_campuses': len(campuses_list),
                'total_appointments': sum(c['total'] for c in campuses_list),
                'avg_utilization_rate': round(sum(c['utilization_rate'] for c in campuses_list) / len(campuses_list) if campuses_list else 0, 1)
            },
            'campuses': campuses_list
        }

    def _generate_revenue_report(self, domain, report_format, date_from, date_to):
        """Generate revenue report"""
        appointments_env = request.env['slot.booking'].sudo()
        
        # Get completed appointments with amounts
        completed_appointments = appointments_env.search(
            domain + [('availability', '=', 'completed'), ('amount', '>', 0)]
        )
        
        total_revenue = sum(appointment.amount for appointment in completed_appointments)
        total_appointments = len(completed_appointments)
        avg_appointment_value = total_revenue / total_appointments if total_appointments > 0 else 0
        
        # Revenue by payment mode
        payment_modes = {}
        for appointment in completed_appointments:
            mode = appointment.payment_mode or 'unknown'
            if mode not in payment_modes:
                payment_modes[mode] = {'count': 0, 'amount': 0}
            payment_modes[mode]['count'] += 1
            payment_modes[mode]['amount'] += appointment.amount
        
        # Revenue by consultation type
        consultation_types = {}
        for appointment in completed_appointments:
            cons_type = appointment.consultation_type or 'unknown'
            if cons_type not in consultation_types:
                consultation_types[cons_type] = {'count': 0, 'amount': 0}
            consultation_types[cons_type]['count'] += 1
            consultation_types[cons_type]['amount'] += appointment.amount
        
        return {
            'summary': {
                'total_revenue': total_revenue,
                'total_paid_appointments': total_appointments,
                'average_appointment_value': round(avg_appointment_value, 2),
                'period_days': (date_to - date_from).days + 1,
                'daily_average_revenue': round(total_revenue / ((date_to - date_from).days + 1), 2)
            },
            'by_payment_mode': payment_modes,
            'by_consultation_type': consultation_types
        }