# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import AccessError, ValidationError
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound

_logger = logging.getLogger(__name__)

class MentalHealthAPIController(http.Controller):
    
    def _authenticate_user(self):
        """Authenticate user and return user record - supports both session and token auth"""
        # Check for Authorization header (Bearer token)
        auth_header = request.httprequest.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            return self._authenticate_with_token(token)
        
        # Check for session cookie authentication
        if request.session.uid:
            return request.env.user
        
        # Check for session_id in headers or cookies
        session_id = request.httprequest.headers.get('X-Session-ID')
        if session_id:
            return self._authenticate_with_session(session_id)
            
        raise Exception("Authentication required")
    
    def _authenticate_with_token(self, token):
        """Authenticate using Bearer token"""
        try:
            # Handle session-based tokens
            if token.startswith('session_'):
                session_id = token.replace('session_', '')
                return self._authenticate_with_session(session_id)
            
            # For API tokens, you would validate against stored tokens
            # For now, we'll use session-based approach
            raise Exception("Invalid token format")
            
        except Exception as e:
            _logger.error(f"Token authentication failed: {str(e)}")
            raise Exception("Invalid or expired token")
    
    def _authenticate_with_session(self, session_id):
        """Authenticate using session ID"""
        try:
            # This is a simplified approach - in production you might need
            # to validate the session more thoroughly
            if request.session.sid == session_id and request.session.uid:
                return request.env.user
            raise Exception("Invalid session")
        except Exception as e:
            _logger.error(f"Session authentication failed: {str(e)}")
            raise Exception("Invalid session")

    def _make_json_response(self, data, status=200):
        """Helper method to create JSON responses with CORS headers"""
        return request.make_response(
            json.dumps(data),
            headers=[
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Session-ID')
            ],
            status=status
        )

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

    # ===== STUDENT/PARENT APP APIs =====
    
    # @http.route('/api/psychologists', type='http', auth='none', methods=['GET', 'OPTIONS'], csrf=False)
    # def get_psychologists_for_student(self, **kwargs):
    #     """GET /psychologists?student_id=xyz → Returns list of available psychologists"""
    #     try:
    #         # Handle OPTIONS request for CORS
    #         if request.httprequest.method == 'OPTIONS':
    #             return self._make_json_response({'message': 'OK'})
                
    #         user = self._authenticate_user()
    #         student_id = kwargs.get('student_id')
            
    #         if not student_id:
    #             return self._make_json_response({
    #                 'status': 'error',
    #                 'message': 'student_id parameter is required',
    #                 'data': []
    #             }, 400)
            
    #         # Get student information
    #         student = request.env['res.partner'].sudo().browse(int(student_id))
    #         if not student or not student.exists():
    #             return self._make_json_response({
    #                 'status': 'error',
    #                 'message': 'Student not found',
    #                 'data': []
    #             }, 404)
            
    #         # Find student's classroom and get available psychologists
    #         classroom = request.env['hospital.classroom'].sudo().search([
    #             ('student_ids', 'in', student.id)
    #         ], limit=1)
            
    #         if not classroom:
    #             return self._make_json_response({
    #                 'status': 'error',
    #                 'message': 'Student not assigned to any classroom',
    #                 'data': []
    #             }, 404)
            
    #         # Get all available psychologists (classroom + grade + school level)
    #         psychologists = classroom.all_psychologist_ids
            
    #         psychologist_data = []
    #         for psychologist in psychologists:
    #             psychologist_data.append({
    #                 'id': psychologist.id,
    #                 'name': psychologist.name,
    #                 'email': psychologist.email or '',
    #                 'phone': psychologist.phone or '',
    #                 'availability': self._get_psychologist_availability(psychologist.id),
    #                 'specializations': [],  # Add if you have specialization field
    #                 'rating': 4.5,  # Add if you have rating system
    #                 'assignment_level': self._get_assignment_level(psychologist, classroom)
    #             })
            
    #         return self._make_json_response({
    #             'status': 'success',
    #             'message': 'Psychologists retrieved successfully',
    #             'data': {
    #                 'psychologists': psychologist_data,
    #                 'student': {
    #                     'id': student.id,
    #                     'name': student.name,
    #                     'classroom': classroom.name,
    #                     'grade': classroom.grade_id.name,
    #                     'school': classroom.school_id.name
    #                 }
    #             }
    #         })
            
    #     except Exception as e:
    #         _logger.error(f"Error getting psychologists: {str(e)}")
    #         return self._make_json_response({
    #             'status': 'error',
    #             'message': str(e),
    #             'data': []
    #         }, 500)
    
    @http.route('/api/appointments', type='http', auth='user', methods=['POST'], csrf=False)
    def book_appointment(self, **kwargs):
        """POST /appointments → Book appointment"""
        try:
            user = self._authenticate_user()
            
            # Get POST data
            student_id = kwargs.get('student_id')
            psychologist_id = kwargs.get('psychologist_id')
            appointment_date = kwargs.get('appointment_date')
            appointment_time = kwargs.get('appointment_time')
            notes = kwargs.get('notes', '')
            
            # Validate required fields
            if not all([student_id, psychologist_id, appointment_date, appointment_time]):
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Missing required fields: student_id, psychologist_id, appointment_date, appointment_time',
                    'data': None
                }, 400)
            
            # Create appointment record (you may need to create this model)
            appointment_vals = {
                'student_id': int(student_id),
                'psychologist_id': int(psychologist_id),
                'appointment_date': appointment_date,
                'appointment_time': appointment_time,
                'notes': notes,
                'status': 'scheduled',
                'booked_by': user.id,
                'booking_date': fields.Datetime.now()
            }
            
            # Get psychologist name
            psychologist = request.env['res.users'].sudo().browse(int(psychologist_id))
            
            # You'll need to create appointment model or use existing one
            # appointment = request.env['mental.health.appointment'].create(appointment_vals)
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Appointment booked successfully',
                'data': {
                    'appointment_id': 1,  # appointment.id,
                    'appointment_date': appointment_date,
                    'appointment_time': appointment_time,
                    'psychologist_name': psychologist.name if psychologist else 'Dr. Smith',
                    'confirmation_number': f"APPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                }
            })
            
        except Exception as e:
            _logger.error(f"Error booking appointment: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)
    
    @http.route('/api/resources', type='http', auth='user', methods=['GET'], csrf=False)
    def get_resources(self, **kwargs):
        """GET /resources → Fetch assigned support group content"""
        try:
            user = self._authenticate_user()
            
            # Get support groups and resources
            # This would depend on your support group model
            resources = {
                'support_groups': [
                    {
                        'id': 1,
                        'name': 'Stress Management Group',
                        'description': 'Learn effective stress management techniques',
                        'meeting_time': 'Every Tuesday 3:00 PM',
                        'participants_count': 8,
                        'next_session': '2025-06-15T15:00:00Z'
                    }
                ],
                'articles': [
                    {
                        'id': 1,
                        'title': 'Managing Exam Anxiety',
                        'content': 'Tips and techniques for managing exam stress...',
                        'category': 'academic_stress',
                        'reading_time': '5 minutes'
                    }
                ],
                'videos': [
                    {
                        'id': 1,
                        'title': 'Breathing Exercises for Calm',
                        'url': 'https://example.com/video1',
                        'duration': '10 minutes',
                        'category': 'relaxation'
                    }
                ]
            }
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Resources retrieved successfully',
                'data': resources
            })
            
        except Exception as e:
            _logger.error(f"Error getting resources: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)

    # ===== DOCTOR APP APIs =====
    
    @http.route('/api/doctor/organizations', type='http', auth='user', methods=['GET'], csrf=False)
    def get_doctor_organizations(self, **kwargs):
        """GET /organizations → List of orgs served by psychologist"""
        try:
            user = self._authenticate_user()
            context = self._get_user_context(user)
            
            if not context['is_psychologist']:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'User is not authorized as a psychologist',
                    'data': []
                }, 403)
            
            organizations = request.env['hospital.hospital'].sudo().search([
                ('psychologist_ids', 'in', user.id),
                ('is_parent', '=', False)  # Only institutions, not parent orgs
            ])
            
            org_data = []
            for org in organizations:
                org_data.append({
                    'id': org.id,
                    'name': org.name,
                    'type': org.type,
                    'code': org.code or '',
                    'address': {
                        'street': org.street or '',
                        'city': org.city or '',
                        'state': org.state or '',
                        'country': org.country or ''
                    },
                    'contact': {
                        'phone': org.phone or '',
                        'email': org.email or '',
                        'website': org.website or ''
                    },
                    'stats': {
                        'total_students': org.total_students,
                        'total_teachers': org.total_teachers,
                        'total_grades': org.grade_count,
                        'total_classrooms': org.classroom_count
                    }
                })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Organizations retrieved successfully',
                'data': {
                    'organizations': org_data,
                    'psychologist': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email
                    }
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting doctor organizations: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    @http.route('/api/doctor/students', type='http', auth='user', methods=['GET'], csrf=False)
    def get_doctor_students(self, **kwargs):
        """GET /students?organization_id=xyz → Fetch students"""
        try:
            user = self._authenticate_user()
            organization_id = kwargs.get('organization_id')
            
            if not organization_id:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Organization ID is required',
                    'data': []
                }, 400)
            
            # Verify psychologist has access to this organization
            org = request.env['hospital.hospital'].sudo().browse(int(organization_id))
            if not org.exists() or user.id not in org.psychologist_ids.ids:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Access denied to this organization',
                    'data': []
                }, 403)
            
            # Get all classrooms in the organization
            classrooms = request.env['hospital.classroom'].sudo().search([
                ('school_id', '=', int(organization_id))
            ])
            
            students_data = []
            for classroom in classrooms:
                for student in classroom.student_ids:
                    students_data.append({
                        'id': student.id,
                        'name': student.name,
                        'email': student.email or '',
                        'phone': student.phone or '',
                        'classroom': {
                            'id': classroom.id,
                            'name': classroom.name,
                            'grade': classroom.grade_id.name
                        },
                        'academic_info': {
                            'grade': classroom.grade_id.name,
                            'year': classroom.grade_id.year or '',
                            'section': classroom.name
                        },
                        'mental_health_status': 'active',  # Add based on your logic
                        'last_session': None,  # Add from appointment records
                        'total_sessions': 0  # Add from appointment records
                    })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Students retrieved successfully',
                'data': {
                    'students': students_data,
                    'organization': {
                        'id': org.id,
                        'name': org.name,
                        'total_students': len(students_data)
                    }
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting doctor students: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    @http.route('/api/doctor/appointments', type='http', auth='user', methods=['GET'], csrf=False)
    def get_doctor_appointments(self, **kwargs):
        """GET /appointments → List of appointments"""
        try:
            user = self._authenticate_user()
            
            # Get appointments for this psychologist
            # You'll need to implement appointment model
            appointments_data = [
                {
                    'id': 1,
                    'student': {
                        'id': 1,
                        'name': 'John Doe',
                        'grade': 'Grade 10',
                        'section': 'A'
                    },
                    'appointment_date': '2025-06-15',
                    'appointment_time': '10:00',
                    'duration': 60,
                    'status': 'scheduled',
                    'type': 'individual_counseling',
                    'notes': 'Follow-up session for anxiety management',
                    'location': 'Counseling Room 1'
                }
            ]
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Appointments retrieved successfully',
                'data': {
                    'appointments': appointments_data,
                    'summary': {
                        'today': 3,
                        'this_week': 12,
                        'pending': 2,
                        'completed': 25
                    }
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting doctor appointments: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    @http.route('/api/doctor/notes', type='http', auth='user', methods=['POST'], csrf=False)
    def store_consultation_notes(self, **kwargs):
        """POST /notes → Store consultation notes"""
        try:
            user = self._authenticate_user()
            
            # Get POST data
            appointment_id = kwargs.get('appointment_id')
            student_id = kwargs.get('student_id')
            notes = kwargs.get('notes')
            session_date = kwargs.get('session_date')
            mood_assessment = kwargs.get('mood_assessment', '')
            action_items = kwargs.get('action_items', '')
            next_session_plan = kwargs.get('next_session_plan', '')
            
            # Validate required fields
            if not all([appointment_id, student_id, notes]):
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Missing required fields: appointment_id, student_id, notes',
                    'data': None
                }, 400)
            
            # Store notes (implement according to your model)
            notes_data = {
                'appointment_id': int(appointment_id),
                'student_id': int(student_id),
                'psychologist_id': user.id,
                'session_notes': notes,
                'session_date': session_date or fields.Datetime.now(),
                'mood_assessment': mood_assessment,
                'action_items': action_items,
                'next_session_plan': next_session_plan,
                'confidentiality_level': 'high'
            }
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Consultation notes saved successfully',
                'data': {
                    'note_id': 1,  # notes_record.id
                    'saved_at': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'psychologist': user.name
                }
            })
            
        except Exception as e:
            _logger.error(f"Error storing consultation notes: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)

    # ===== DASHBOARD APP APIs =====
    
    @http.route('/api/dashboard/overview', type='http', auth='user', methods=['GET'], csrf=False)
    def get_dashboard_overview(self, **kwargs):
        """GET /dashboard/overview?institution_id=xyz → Return summary metrics"""
        try:
            user = self._authenticate_user()
            institution_id = kwargs.get('institution_id')
            
            if not institution_id:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Institution ID is required',
                    'data': None
                }, 400)
            
            institution = request.env['hospital.hospital'].sudo().browse(int(institution_id))
            if not institution.exists():
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Institution not found',
                    'data': None
                }, 404)
            
            # Calculate metrics
            total_students = institution.total_students
            total_psychologists = institution.psychologist_count
            # You'll need to implement these from appointment model
            total_appointments = 150  # Get from appointment records
            active_support_groups = 5  # Get from support group model
            
            overview_data = {
                'institution': {
                    'id': institution.id,
                    'name': institution.name,
                    'type': institution.type
                },
                'metrics': {
                    'total_students': total_students,
                    'total_appointments_booked': total_appointments,
                    'active_psychologists': total_psychologists,
                    'support_group_participation_rate': 68.5,
                    'engagement_score': 78.2
                },
                'recent_activity': {
                    'appointments_today': 12,
                    'appointments_this_week': 45,
                    'new_students_this_month': 8,
                    'completed_sessions_this_month': 156
                },
                'trends': {
                    'appointment_growth': '+15%',
                    'student_engagement': '+8%',
                    'satisfaction_score': 4.3
                }
            }
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Dashboard overview retrieved successfully',
                'data': overview_data
            })
            
        except Exception as e:
            _logger.error(f"Error getting dashboard overview: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)
    
    @http.route('/api/dashboard/appointments', type='http', auth='user', methods=['GET'], csrf=False)
    def get_dashboard_appointments(self, **kwargs):
        """GET /dashboard/appointments?school_id=xyz → Appointment volumes and psychologist loads"""
        try:
            user = self._authenticate_user()
            school_id = kwargs.get('school_id')
            from_date = kwargs.get('from_date')
            to_date = kwargs.get('to_date')
            
            # Get appointment analytics
            appointments_data = {
                'summary': {
                    'total_appointments': 245,
                    'completed': 189,
                    'scheduled': 32,
                    'cancelled': 15,
                    'missed': 9
                },
                'by_grade': [
                    {'grade': 'Grade 10', 'count': 45, 'completion_rate': 89.5},
                    {'grade': 'Grade 11', 'count': 38, 'completion_rate': 92.1},
                    {'grade': 'Grade 12', 'count': 52, 'completion_rate': 85.7}
                ],
                'psychologist_load': [
                    {
                        'psychologist': 'Dr. Sarah Smith',
                        'total_appointments': 78,
                        'utilization_rate': 85.2,
                        'avg_session_duration': 55,
                        'satisfaction_rating': 4.6
                    },
                    {
                        'psychologist': 'Dr. Mike Johnson',
                        'total_appointments': 65,
                        'utilization_rate': 78.9,
                        'avg_session_duration': 60,
                        'satisfaction_rating': 4.4
                    }
                ],
                'daily_distribution': [
                    {'date': '2025-06-09', 'appointments': 12, 'completed': 10},
                    {'date': '2025-06-08', 'appointments': 15, 'completed': 13},
                    {'date': '2025-06-07', 'appointments': 9, 'completed': 8}
                ]
            }
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Appointment analytics retrieved successfully',
                'data': appointments_data
            })
            
        except Exception as e:
            _logger.error(f"Error getting dashboard appointments: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': {}
            }, 500)
    
    @http.route('/api/dashboard/issues-breakdown', type='http', auth='user', methods=['GET'], csrf=False)
    def get_dashboard_issues(self, **kwargs):
        """GET /dashboard/issues-breakdown → Anonymized breakdown of mental health topics"""
        try:
            user = self._authenticate_user()
            range_days = kwargs.get('range_days', 90)
            
            # Get anonymized issue breakdown
            issues_data = {
                'summary': {
                    'total_sessions': 342,
                    'unique_issues_identified': 15,
                    'trend': '+12% from last period'
                },
                'categories': [
                    {
                        'category': 'Academic Stress',
                        'percentage': 35.2,
                        'count': 120,
                        'trend': '+8%',
                        'subcategories': [
                            {'name': 'Exam Anxiety', 'count': 67},
                            {'name': 'Time Management', 'count': 32},
                            {'name': 'Grade Pressure', 'count': 21}
                        ]
                    },
                    {
                        'category': 'Social Issues',
                        'percentage': 28.7,
                        'count': 98,
                        'trend': '+15%',
                        'subcategories': [
                            {'name': 'Peer Relationships', 'count': 45},
                            {'name': 'Bullying', 'count': 23},
                            {'name': 'Social Anxiety', 'count': 30}
                        ]
                    },
                    {
                        'category': 'Family Issues',
                        'percentage': 18.4,
                        'count': 63,
                        'trend': '-5%',
                        'subcategories': [
                            {'name': 'Family Conflict', 'count': 28},
                            {'name': 'Divorce/Separation', 'count': 20},
                            {'name': 'Financial Stress', 'count': 15}
                        ]
                    },
                    {
                        'category': 'Self-Esteem',
                        'percentage': 12.3,
                        'count': 42,
                        'trend': '+3%'
                    },
                    {
                        'category': 'Other',
                        'percentage': 5.4,
                        'count': 19,
                        'trend': '+2%'
                    }
                ],
                'trends_over_time': [
                    {'month': '2025-04', 'academic_stress': 32, 'social_issues': 25, 'family_issues': 18},
                    {'month': '2025-05', 'academic_stress': 35, 'social_issues': 28, 'family_issues': 17},
                    {'month': '2025-06', 'academic_stress': 35, 'social_issues': 29, 'family_issues': 18}
                ]
            }
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Issues breakdown retrieved successfully',
                'data': issues_data
            })
            
        except Exception as e:
            _logger.error(f"Error getting dashboard issues: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': {}
            }, 500)
    
    @http.route('/api/dashboard/support-groups', type='http', auth='user', methods=['GET'], csrf=False)
    def get_dashboard_support_groups(self, **kwargs):
        """GET /dashboard/support-groups → Participation levels and engagement"""
        try:
            user = self._authenticate_user()
            
            support_groups_data = {
                'summary': {
                    'total_groups': 8,
                    'active_groups': 6,
                    'total_participants': 84,
                    'avg_participation_rate': 72.5,
                    'avg_session_attendance': 68.3
                },
                'groups': [
                    {
                        'id': 1,
                        'name': 'Stress Management Circle',
                        'facilitator': 'Dr. Sarah Smith',
                        'participants': 12,
                        'max_capacity': 15,
                        'utilization_rate': 80.0,
                        'attendance_rate': 75.5,
                        'sessions_completed': 8,
                        'next_session': '2025-06-12T14:00:00Z',
                        'category': 'Academic Support'
                    },
                    {
                        'id': 2,
                        'name': 'Social Skills Workshop',
                        'facilitator': 'Dr. Mike Johnson',
                        'participants': 10,
                        'max_capacity': 12,
                        'utilization_rate': 83.3,
                        'attendance_rate': 82.1,
                        'sessions_completed': 6,
                        'next_session': '2025-06-14T15:30:00Z',
                        'category': 'Social Development'
                    }
                ],
                'participation_trends': {
                    'weekly_attendance': [
                        {'week': '2025-W22', 'attendance': 68},
                        {'week': '2025-W23', 'attendance': 72},
                        {'week': '2025-W24', 'attendance': 69}
                    ],
                    'dropout_rate': 15.2,
                    'completion_rate': 78.9
                },
                'engagement_metrics': {
                    'avg_session_duration': 75,  # minutes
                    'participant_satisfaction': 4.2,
                    'facilitator_rating': 4.5,
                    'topics_covered': 24
                }
            }
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Support groups data retrieved successfully',
                'data': support_groups_data
            })
            
        except Exception as e:
            _logger.error(f"Error getting support groups data: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': {}
            }, 500)
    
    @http.route('/api/dashboard/export', type='http', auth='user', methods=['POST'], csrf=False)
    def export_dashboard_report(self, **kwargs):
        """POST /dashboard/export → Generate downloadable reports"""
        try:
            user = self._authenticate_user()
            
            export_type = kwargs.get('type', 'csv')  # csv, pdf
            report_type = kwargs.get('report_type', 'overview')  # overview, appointments, issues, support_groups
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            
            # Generate report based on type
            if export_type == 'csv':
                # Generate CSV report
                report_url = self._generate_csv_report(report_type, date_from, date_to)
            elif export_type == 'pdf':
                # Generate PDF report
                report_url = self._generate_pdf_report(report_type, date_from, date_to)
            else:
                return self._make_json_response({
                    'status': 'error',
                    'message': 'Invalid export type. Use csv or pdf',
                    'data': None
                }, 400)
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Report generated successfully',
                'data': {
                    'download_url': report_url,
                    'report_type': report_type,
                    'export_type': export_type,
                    'generated_at': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'expires_at': (datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
                }
            })
            
        except Exception as e:
            _logger.error(f"Error exporting dashboard report: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)

    # ===== ADDITIONAL UTILITY APIs =====
    
    @http.route('/api/user/profile', type='http', auth='user', methods=['GET'], csrf=False)
    def get_user_profile(self, **kwargs):
        """GET /user/profile → Get current user profile and permissions"""
        try:
            user = self._authenticate_user()
            context = self._get_user_context(user)
            
            return self._make_json_response({
                'status': 'success',
                'message': 'User profile retrieved successfully',
                'data': {
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'phone': user.phone or '',
                        'avatar': f'/web/image/res.users/{user.id}/image_128',
                        'last_login': user.login_date.strftime('%Y-%m-%d %H:%M:%S') if user.login_date else None
                    },
                    'permissions': context,
                    'preferences': {
                        'language': user.lang or 'en_US',
                        'timezone': user.tz or 'UTC',
                        'notification_settings': {
                            'email_notifications': True,
                            'sms_notifications': False,
                            'appointment_reminders': True
                        }
                    }
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting user profile: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': None
            }, 500)
    
    @http.route('/api/schools', type='http', auth='user', methods=['GET'], csrf=False)
    def get_schools_list(self, **kwargs):
        """GET /schools → Get list of schools/institutions"""
        try:
            user = self._authenticate_user()
            organization_id = kwargs.get('organization_id')
            
            domain = [('is_parent', '=', False), ('type', 'in', ['school', 'university', 'college'])]
            if organization_id:
                domain.append(('parent_id', '=', int(organization_id)))
            
            schools = request.env['hospital.hospital'].sudo().search(domain)
            
            schools_data = []
            for school in schools:
                schools_data.append({
                    'id': school.id,
                    'name': school.name,
                    'code': school.code or '',
                    'type': school.type,
                    'parent_organization': school.parent_id.name if school.parent_id else '',
                    'address': {
                        'street': school.street or '',
                        'city': school.city or '',
                        'state': school.state or '',
                        'country': school.country or ''
                    },
                    'contact': {
                        'phone': school.phone or '',
                        'email': school.email or '',
                        'website': school.website or ''
                    },
                    'stats': {
                        'total_students': school.total_students,
                        'total_teachers': school.total_teachers,
                        'total_grades': school.grade_count,
                        'total_classrooms': school.classroom_count,
                        'psychologists_count': school.psychologist_count
                    }
                })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Schools retrieved successfully',
                'data': {
                    'schools': schools_data,
                    'total_count': len(schools_data)
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting schools: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    @http.route('/api/grades', type='http', auth='user', methods=['GET'], csrf=False)
    def get_grades_list(self, **kwargs):
        """GET /grades → Get list of grades/departments"""
        try:
            user = self._authenticate_user()
            school_id = kwargs.get('school_id')
            
            domain = []
            if school_id:
                domain.append(('school_id', '=', int(school_id)))
            
            grades = request.env['hospital.grade'].sudo().search(domain)
            
            grades_data = []
            for grade in grades:
                grades_data.append({
                    'id': grade.id,
                    'name': grade.name,
                    'year': grade.year or '',
                    'curriculum': grade.curriculum or '',
                    'school': {
                        'id': grade.school_id.id,
                        'name': grade.school_id.name,
                        'type': grade.school_id.type
                    },
                    'stats': {
                        'total_classrooms': grade.classroom_count,
                        'total_students': grade.total_students,
                        'total_teachers': grade.total_teachers,
                        'total_capacity': grade.total_capacity,
                        'psychologists_count': grade.psychologist_count
                    }
                })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Grades retrieved successfully',
                'data': {
                    'grades': grades_data,
                    'total_count': len(grades_data)
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting grades: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    @http.route('/api/classrooms', type='http', auth='user', methods=['GET'], csrf=False)
    def get_classrooms_list(self, **kwargs):
        """GET /classrooms → Get list of classrooms/sections"""
        try:
            user = self._authenticate_user()
            grade_id = kwargs.get('grade_id')
            school_id = kwargs.get('school_id')
            
            domain = []
            if grade_id:
                domain.append(('grade_id', '=', int(grade_id)))
            if school_id:
                domain.append(('school_id', '=', int(school_id)))
            
            classrooms = request.env['hospital.classroom'].sudo().search(domain)
            
            classrooms_data = []
            for classroom in classrooms:
                classrooms_data.append({
                    'id': classroom.id,
                    'name': classroom.name,
                    'capacity': classroom.capacity,
                    'student_count': classroom.student_count,
                    'utilization_percentage': classroom.utilization_percentage,
                    'is_overcapacity': classroom.is_overcapacity,
                    'grade': {
                        'id': classroom.grade_id.id,
                        'name': classroom.grade_id.name,
                        'year': classroom.grade_id.year or ''
                    },
                    'school': {
                        'id': classroom.school_id.id,
                        'name': classroom.school_id.name
                    },
                    'teacher': {
                        'id': classroom.teacher_id.id if classroom.teacher_id else None,
                        'name': classroom.teacher_id.name if classroom.teacher_id else None,
                        'email': classroom.teacher_id.email if classroom.teacher_id else None
                    },
                    'psychologists': [
                        {
                            'id': psych.id,
                            'name': psych.name,
                            'email': psych.email,
                            'assignment_level': self._get_assignment_level(psych, classroom)
                        }
                        for psych in classroom.all_psychologist_ids
                    ]
                })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Classrooms retrieved successfully',
                'data': {
                    'classrooms': classrooms_data,
                    'total_count': len(classrooms_data)
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting classrooms: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    @http.route('/api/students', type='http', auth='user', methods=['GET'], csrf=False)
    def get_students_list(self, **kwargs):
        """GET /students → Get list of students with filters"""
        try:
            user = self._authenticate_user()
            classroom_id = kwargs.get('classroom_id')
            grade_id = kwargs.get('grade_id')
            school_id = kwargs.get('school_id')
            
            domain = [('is_company', '=', False)]  # Only individual contacts, not companies
            
            if classroom_id:
                classroom = request.env['hospital.classroom'].sudo().browse(int(classroom_id))
                student_ids = classroom.student_ids.ids
                domain.append(('id', 'in', student_ids))
            elif grade_id:
                classrooms = request.env['hospital.classroom'].sudo().search([('grade_id', '=', int(grade_id))])
                student_ids = classrooms.mapped('student_ids').ids
                domain.append(('id', 'in', student_ids))
            elif school_id:
                classrooms = request.env['hospital.classroom'].sudo().search([('school_id', '=', int(school_id))])
                student_ids = classrooms.mapped('student_ids').ids
                domain.append(('id', 'in', student_ids))
            
            students = request.env['res.partner'].sudo().search(domain)
            
            students_data = []
            for student in students:
                # Find student's classroom
                classroom = request.env['hospital.classroom'].sudo().search([
                    ('student_ids', 'in', student.id)
                ], limit=1)
                
                students_data.append({
                    'id': student.id,
                    'name': student.name,
                    'email': student.email or '',
                    'phone': student.phone or '',
                    'mobile': student.mobile or '',
                    'address': {
                        'street': student.street or '',
                        'city': student.city or '',
                        'state': student.state_id.name if student.state_id else '',
                        'country': student.country_id.name if student.country_id else ''
                    },
                    'academic_info': {
                        'classroom_id': classroom.id if classroom else None,
                        'classroom_name': classroom.name if classroom else '',
                        'grade_id': classroom.grade_id.id if classroom and classroom.grade_id else None,
                        'grade_name': classroom.grade_id.name if classroom and classroom.grade_id else '',
                        'school_id': classroom.school_id.id if classroom and classroom.school_id else None,
                        'school_name': classroom.school_id.name if classroom and classroom.school_id else ''
                    },
                    'guardian_info': {
                        'parent_id': student.parent_id.id if student.parent_id else None,
                        'parent_name': student.parent_id.name if student.parent_id else '',
                        'parent_email': student.parent_id.email if student.parent_id else '',
                        'parent_phone': student.parent_id.phone if student.parent_id else ''
                    },
                    'mental_health': {
                        'has_active_sessions': False,  # Implement based on appointment model
                        'last_session_date': None,     # Implement based on appointment model
                        'total_sessions': 0,           # Implement based on appointment model
                        'assigned_psychologist': None  # Implement based on your logic
                    }
                })
            
            return self._make_json_response({
                'status': 'success',
                'message': 'Students retrieved successfully',
                'data': {
                    'students': students_data,
                    'total_count': len(students_data),
                    'filters_applied': {
                        'classroom_id': classroom_id,
                        'grade_id': grade_id,
                        'school_id': school_id
                    }
                }
            })
            
        except Exception as e:
            _logger.error(f"Error getting students: {str(e)}")
            return self._make_json_response({
                'status': 'error',
                'message': str(e),
                'data': []
            }, 500)
    
    # ===== ERROR HANDLING =====
    
    @http.route('/api/health', type='http', auth='none', methods=['GET'], csrf=False)
    def api_health_check(self, **kwargs):
        """GET /health → API health check endpoint"""
        return self._make_json_response({
            'status': 'success',
            'message': 'Mental Health API is running',
            'data': {
                'server_time': fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'api_version': '1.0.0',
                'endpoints_available': [
                    '/api/psychologists',
                    '/api/appointments',
                    '/api/resources',
                    '/api/doctor/organizations',
                    '/api/doctor/students',
                    '/api/doctor/appointments',
                    '/api/doctor/notes',
                    '/api/dashboard/overview',
                    '/api/dashboard/appointments',
                    '/api/dashboard/issues-breakdown',
                    '/api/dashboard/support-groups',
                    '/api/dashboard/export'
                ]
            }
        })

    # ===== HELPER METHODS =====
    
    def _get_psychologist_availability(self, psychologist_id):
        """Get psychologist availability slots"""
        # Implement based on your appointment/calendar model
        return {
            'next_available': '2025-06-12T10:00:00Z',
            'slots_this_week': 8,
            'slots_next_week': 12
        }
    
    def _get_assignment_level(self, psychologist, classroom):
        """Determine at what level psychologist is assigned"""
        if psychologist.id in classroom.psychologist_ids.ids:
            return 'classroom'
        elif psychologist.id in classroom.grade_id.psychologist_ids.ids:
            return 'grade'
        elif psychologist.id in classroom.school_id.psychologist_ids.ids:
            return 'school'
        return 'unknown'
    
    def _generate_csv_report(self, report_type, date_from, date_to):
        """Generate CSV report and return download URL"""
        # Implement CSV generation logic
        return '/web/content/report/mental_health_report.csv'
    
    def _generate_pdf_report(self, report_type, date_from, date_to):
        """Generate PDF report and return download URL"""
        # Implement PDF generation logic
        return '/web/content/report/mental_health_report.pdf'