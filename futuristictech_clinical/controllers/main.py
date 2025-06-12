# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import random
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class TestAPI(http.Controller):
    @http.route('/api/test', type='http', auth='none', methods=['GET'], csrf=False)
    def test_endpoint(self, **kwargs):
        response = {
            'status': 'success',
            'message': 'Hello World'
        }
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/crm_lead/login', type='http', auth='none', methods=['POST'], csrf=False)
    def login_with_otp(self, **post):
        """
        API for generating OTP and sending SMS for login/signup
        Parameters:
        - phone_number: 10 digit phone number (integer)
        - uid: Random 16-digit characters (string)
        - type: 'login' or 'signup'
        - country_code: Country code (integer)
        """
        # model.res.partner
        try:
            # Validate required parameters
            phone_number = post.get('phone_number')
            uid = post.get('uid')
            request_type = post.get('type')
            country_code = post.get('country_code')

            if not all([phone_number, uid, request_type, country_code]):
                response = {
                    'success': False,
                    'message': 'Missing required parameters'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

            # Clean and validate phone number
            phone_number = str(phone_number).strip()
            if len(phone_number) != 10 or not phone_number.isdigit():
                response = {
                    'success': False,
                    'message': 'Invalid phone number'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

            # Generate OTP (4 digits for demo)
            otp = str(random.randint(1000, 9999))
            
            # Search for existing lead with this phone number
            lead = request.env['crm.lead'].sudo().search([
                ('caller_mobile', '=', phone_number)
            ], limit=1)

            if request_type == 'login':
                if not lead:
                    response = {
                        'success': False,
                        'message': 'Phone number not registered. Please sign up.'

                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')]
                    )
                
                # In production: Send OTP via SMS
                _logger.info(f"OTP for login: {otp} (would send via SMS in production)")
                
                response = {
                    'message': 'OTP Message Sent',
                    'success': True
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )
            
            elif request_type == 'signup':
                if lead:
                    response = {
                        'success': False,
                        'message': 'Phone number already registered. Please login.'
                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')]
                    )
                
                # In production: Send OTP via SMS
                _logger.info(f"OTP for signup: {otp} (would send via SMS in production)")
                
                response = {
                    'OTP': otp,
                    'uid': uid,
                    'success': True
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )
            
            else:
                response = {
                    'success': False,
                    'message': 'Invalid type parameter'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

        except Exception as e:
            _logger.error(f"Error in login_with_otp: {str(e)}")
            response = {
                'success': False,
                'message': 'Internal server error'
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/crm_lead/send_otp', type='http', auth='none', methods=['POST'], csrf=False)
    def verify_otp(self, **post):
        """
        API for verifying OTP to complete login
        Parameters:
        - phone_number: 10 digit phone number (integer)
        - country_code: Country code (integer)
        - uid: Random 16-digit characters (string)
        - otp: OTP entered by user (integer)
        """
        try:
            # Validate required parameters
            phone_number = post.get('phone_number')
            country_code = post.get('country_code')
            uid = post.get('uid')
            otp = post.get('otp')

            if not all([phone_number, country_code, uid, otp]):
                response = {
                    'success': False,
                    'message': 'Missing required parameters'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

            # Clean and validate phone number
            phone_number = str(phone_number).strip()
            if len(phone_number) != 10 or not phone_number.isdigit():
                response = {
                    'success': False,
                    'message': 'Invalid phone number'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

            # Search for existing lead with this phone number
            lead = request.env['crm.lead'].sudo().search([
                ('caller_mobile', '=', phone_number)
            ], limit=1)

            if not lead:
                response = {
                    'success': False,
                    'message': 'Phone number not registered'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

            # In production: Verify OTP against stored value
            # For demo, we'll assume any 4-digit OTP is valid
            
            # Get patient name (if exists) or use caller name
            patient_name = lead.patient_name if lead.patient_name else lead.caller_name

            response = {
                'lead_id': lead.id,
                'success': True,
                'caller_mobile': phone_number,
                'patient_name': patient_name or '',
                'caller_name': lead.caller_name or '',
                'message': 'login is successful!',
                'uid': uid
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            _logger.error(f"Error in verify_otp: {str(e)}")
            response = {
                'success': False,
                'message': 'Internal server error'
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
        

    # Add this corrected endpoint to your main.py file

    @http.route('/api/students', type='http', auth='none', methods=['GET'], csrf=False)
    def get_students(self, psychologist_id=None, **kwargs):
        """
        API to get all students for a given psychologist
        Parameters:
        - psychologist_id: ID of the psychologist (integer)
        """
        try:
            if not psychologist_id:
                response = {
                    'success': False,
                    'message': 'Missing psychologist_id parameter'
                }
                return request.make_response(
                    json.dumps(response),
                    headers=[('Content-Type', 'application/json')]
                )

            # Convert psychologist_id to integer
            psychologist_id = int(psychologist_id)
            
            # Method 1: Get students through classroom assignments
            # First, find all classrooms where this psychologist is assigned
            classrooms = request.env['hospital.classroom'].sudo().search([
                ('psychologist_ids', 'in', [psychologist_id])
            ])
            
            # Get students from these classrooms
            students_from_classrooms = request.env['res.partner']
            for classroom in classrooms:
                students_from_classrooms |= classroom.student_ids
            
            # Method 2: Get students through grade assignments
            # Find all grades where this psychologist is assigned
            grades = request.env['hospital.grade'].sudo().search([
                ('psychologist_ids', 'in', [psychologist_id])
            ])
            
            # Get students from classrooms in these grades
            students_from_grades = request.env['res.partner']
            for grade in grades:
                for classroom in grade.classroom_ids:
                    students_from_grades |= classroom.student_ids
            
            # Method 3: Get students through hospital/school assignments
            # Find all hospitals/schools where this psychologist is assigned
            hospitals = request.env['hospital.hospital'].sudo().search([
                ('psychologist_ids', 'in', [psychologist_id])
            ])
            
            # Get students from all classrooms in these hospitals
            students_from_hospitals = request.env['res.partner']
            for hospital in hospitals:
                for classroom in hospital.classroom_ids:
                    students_from_hospitals |= classroom.student_ids
            
            # Combine all students and remove duplicates
            all_students = students_from_classrooms | students_from_grades | students_from_hospitals
            
            # Alternative method if you have a direct relationship (uncomment if applicable):
            # If there's a direct psychologist_id field in res.partner, use this instead:
            # all_students = request.env['res.partner'].sudo().search([
            #     ('psychologist_id', '=', psychologist_id),
            #     ('is_company', '=', False)  # Ensure we're getting individuals, not companies
            # ])

            student_data = []
            for student in all_students:
                # Get additional student information
                student_info = {
                    'id': student.id,
                    'name': student.name,
                    'email': student.email or '',
                    'phone': student.phone or '',
                    'mobile': student.mobile or '',
                }
                
                # Add classroom information if available
                student_classrooms = classrooms.filtered(lambda c: student in c.student_ids)
                if student_classrooms:
                    student_info['classrooms'] = []
                    for classroom in student_classrooms:
                        student_info['classrooms'].append({
                            'id': classroom.id,
                            'name': classroom.name,
                            'grade': classroom.grade_id.name if classroom.grade_id else '',
                            'school': classroom.school_id.name if classroom.school_id else ''
                        })
                
                student_data.append(student_info)

            response = {
                'success': True,
                'count': len(student_data),
                'students': student_data,
                'psychologist_id': psychologist_id
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )

        except ValueError:
            response = {
                'success': False,
                'message': 'Invalid psychologist_id parameter. Must be an integer.'
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error in get_students: {str(e)}")
            response = {
                'success': False,
                'message': 'Internal server error'
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
        


    @http.route('/api/psychologists', type='http', auth='none', methods=['GET'], csrf=False)
    def get_psychologists(self, hospital_id=None, grade_id=None, classroom_id=None, **kwargs):
        """
        API to get all psychologists
        Parameters (optional filters):
        - hospital_id: Filter by specific hospital/school (integer)
        - grade_id: Filter by specific grade/department (integer)
        - classroom_id: Filter by specific classroom (integer)
        """
        try:
            psychologists = request.env['res.users'].sudo()
            
            if hospital_id:
                # Get psychologists assigned to a specific hospital/school
                hospital = request.env['hospital.hospital'].sudo().browse(int(hospital_id))
                if hospital.exists():
                    psychologists = hospital.psychologist_ids
                else:
                    response = {
                        'success': False,
                        'message': f'Hospital with ID {hospital_id} not found'
                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')]
                    )
            
            elif grade_id:
                # Get psychologists assigned to a specific grade/department
                grade = request.env['hospital.grade'].sudo().browse(int(grade_id))
                if grade.exists():
                    # Include psychologists from grade, and also from the parent school
                    psychologists = grade.psychologist_ids
                    if grade.school_id:
                        psychologists |= grade.school_id.psychologist_ids
                else:
                    response = {
                        'success': False,
                        'message': f'Grade with ID {grade_id} not found'
                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')]
                    )
            
            elif classroom_id:
                # Get psychologists assigned to a specific classroom
                classroom = request.env['hospital.classroom'].sudo().browse(int(classroom_id))
                if classroom.exists():
                    # Include psychologists from classroom, grade, and school
                    psychologists = classroom.all_psychologist_ids
                else:
                    response = {
                        'success': False,
                        'message': f'Classroom with ID {classroom_id} not found'
                    }
                    return request.make_response(
                        json.dumps(response),
                        headers=[('Content-Type', 'application/json')]
                    )
            
            else:
                # Get all psychologists assigned to any hospital, grade, or classroom
                hospital_psychologists = request.env['hospital.hospital'].sudo().search([]).mapped('psychologist_ids')
                grade_psychologists = request.env['hospital.grade'].sudo().search([]).mapped('psychologist_ids')
                classroom_psychologists = request.env['hospital.classroom'].sudo().search([]).mapped('psychologist_ids')
                
                # Combine and remove duplicates
                psychologists = hospital_psychologists | grade_psychologists | classroom_psychologists
                
                # Alternative: If you want ALL users with psychologist role, you could search by groups:
                # psychologists = request.env['res.users'].sudo().search([
                #     ('groups_id', 'in', [request.env.ref('your_module.group_psychologist').id])
                # ])

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
                
                psychologist_info = {
                    'id': psychologist.id,
                    'name': psychologist.name,
                    'email': psychologist.email or '',
                    'phone': psychologist.phone or '',
                    'login': psychologist.login,
                    'active': psychologist.active,
                    'assignments': {
                        'hospitals': [{'id': h.id, 'name': h.name, 'type': h.type} for h in assigned_hospitals],
                        'grades': [{'id': g.id, 'name': g.name, 'school': g.school_id.name if g.school_id else ''} for g in assigned_grades],
                        'classrooms': [{'id': c.id, 'name': c.name, 'grade': c.grade_id.name if c.grade_id else '', 'school': c.school_id.name if c.school_id else ''} for c in assigned_classrooms]
                    }
                }
                
                # Calculate total students assigned
                total_students = 0
                for classroom in assigned_classrooms:
                    total_students += classroom.student_count
                for grade in assigned_grades:
                    total_students += grade.total_students
                for hospital in assigned_hospitals:
                    total_students += hospital.total_students
                
                psychologist_info['total_students'] = total_students
                
                psychologist_data.append(psychologist_info)

            response = {
                'success': True,
                'count': len(psychologist_data),
                'psychologists': psychologist_data
            }
            
            # Add filter information to response
            if hospital_id:
                response['filter'] = {'type': 'hospital', 'id': int(hospital_id)}
            elif grade_id:
                response['filter'] = {'type': 'grade', 'id': int(grade_id)}
            elif classroom_id:
                response['filter'] = {'type': 'classroom', 'id': int(classroom_id)}
            else:
                response['filter'] = {'type': 'all'}
                
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )

        except ValueError as e:
            response = {
                'success': False,
                'message': f'Invalid parameter value: {str(e)}'
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error(f"Error in get_psychologists: {str(e)}")
            response = {
                'success': False,
                'message': 'Internal server error'
            }
            return request.make_response(
                json.dumps(response),
                headers=[('Content-Type', 'application/json')],
                status=500
            )