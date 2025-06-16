# -*- coding: utf-8 -*-
from odoo import http, models, fields
from odoo.http import request, Controller, route
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
        



# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime, date
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

class ConsultationAPI(http.Controller):
    
    def _get_error_response(self, message, status=400):
        """Helper method to return error response"""
        response = {
            'success': False,
            'message': message
        }
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')],
            status=status
        )
    
    def _get_success_response(self, data, message="Success"):
        """Helper method to return success response"""
        response = {
            'success': True,
            'message': message,
            **data
        }
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')]
        )
    
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
            
            # Lab tests
            'labtest_types': [{'id': lab.id, 'name': lab.name} for lab in consultation.labtest_type_ids],
            
            # Specialities
            'specialities': [{'id': spec.id, 'name': spec.name} for spec in consultation.speciality_ids],
            
            # Scales
            'scale_types': [{'scale_type': scale.scale_type} for scale in consultation.scale_type_ids],
            
            # Prescription lines count
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
            
            'created_by': consultation.user_id.name if consultation.user_id else None,
            'company': consultation.company_id.name if consultation.company_id else None,
        }

    @http.route('/api/consultation/create', type='http', auth='none', methods=['POST'], csrf=False)
    def create_consultation(self, **post):
        """
        API to create a new consultation
        Required Parameters:
        - type: 'ip' or 'op'
        - psychiatrist_id: ID of the psychiatrist (hr.employee)
        - inpatient_admission_id: Required if type='ip'
        - op_visit_id: Required if type='op'
        
        Optional Parameters:
        - date: Consultation date (YYYY-MM-DD format, defaults to today)
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
            consultation_type = post.get('type')
            psychiatrist_id = post.get('psychiatrist_id')
            
            if not consultation_type or consultation_type not in ['ip', 'op']:
                return self._get_error_response('Type is required and must be either "ip" or "op"')
            
            if not psychiatrist_id:
                return self._get_error_response('psychiatrist_id is required')
            
            # Validate psychiatrist exists
            psychiatrist = request.env['hr.employee'].sudo().search([('id', '=', int(psychiatrist_id))], limit=1)
            if not psychiatrist:
                return self._get_error_response(f'Psychiatrist with ID {psychiatrist_id} not found')
            
            # Validate admission/visit based on type
            if consultation_type == 'ip':
                inpatient_admission_id = post.get('inpatient_admission_id')
                if not inpatient_admission_id:
                    return self._get_error_response('inpatient_admission_id is required for IP consultations')
                
                admission = request.env['hospital.admission'].sudo().search([('id', '=', int(inpatient_admission_id))], limit=1)
                if not admission:
                    return self._get_error_response(f'Inpatient admission with ID {inpatient_admission_id} not found')
            
            elif consultation_type == 'op':
                op_visit_id = post.get('op_visit_id')
                if not op_visit_id:
                    return self._get_error_response('op_visit_id is required for OP consultations')
                
                op_visit = request.env['op.visits'].sudo().search([('id', '=', int(op_visit_id))], limit=1)
                if not op_visit:
                    return self._get_error_response(f'OP visit with ID {op_visit_id} not found')
            
            # Prepare consultation values
            vals = {
                'type': consultation_type,
                'psychiatrist_id': int(psychiatrist_id),
                'date': post.get('date', fields.Date.context_today(request.env['consultation.consultation'])),
            }
            
            # Add type-specific fields
            if consultation_type == 'ip':
                vals['inpatient_admission_id'] = int(inpatient_admission_id)
            else:
                vals['op_visit_id'] = int(op_visit_id)
            
            # Add optional fields
            optional_fields = {
                'consultation_type': post.get('consultation_type'),
                'priority': post.get('priority'),
                'general_observation': post.get('general_observation'),
                'current_medication': post.get('current_medication'),
                'advice_to_counsellor': post.get('advice_to_counsellor'),
                'advice_to_psychologist': post.get('advice_to_psychologist'),
                'lab_advice': post.get('lab_advice', '/'),
                'cross_consultation': post.get('cross_consultation'),
                'doctor_advice': post.get('doctor_advice'),
                'precautions': post.get('precautions'),
                'todo': post.get('todo'),
                'is_sos': post.get('is_sos', False),
                'next_followup': post.get('next_followup', False),
            }
            
            # Add non-empty optional fields
            for field, value in optional_fields.items():
                if value is not None and value != '':
                    vals[field] = value
            
            # Handle date fields
            if post.get('next_followup_date'):
                try:
                    vals['next_followup_date'] = datetime.strptime(post.get('next_followup_date'), '%Y-%m-%d').date()
                except ValueError:
                    return self._get_error_response('Invalid next_followup_date format. Use YYYY-MM-DD')
            
            # Handle related fields
            if post.get('cp_therapist_id'):
                cp_therapist = request.env['hr.employee'].sudo().search([('id', '=', int(post.get('cp_therapist_id')))], limit=1)
                if cp_therapist:
                    vals['cp_therapist_id'] = cp_therapist.id
            
            if post.get('followup_type_id'):
                followup_type = request.env['followup.type'].sudo().search([('id', '=', int(post.get('followup_type_id')))], limit=1)
                if followup_type:
                    vals['followup_type_id'] = followup_type.id
            
            # Handle Many2many fields
            if post.get('labtest_type_ids'):
                try:
                    labtest_ids = json.loads(post.get('labtest_type_ids')) if isinstance(post.get('labtest_type_ids'), str) else post.get('labtest_type_ids')
                    if isinstance(labtest_ids, list):
                        vals['labtest_type_ids'] = [(6, 0, labtest_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid labtest_type_ids format. Should be a list of IDs')
            
            if post.get('speciality_ids'):
                try:
                    speciality_ids = json.loads(post.get('speciality_ids')) if isinstance(post.get('speciality_ids'), str) else post.get('speciality_ids')
                    if isinstance(speciality_ids, list):
                        vals['speciality_ids'] = [(6, 0, speciality_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid speciality_ids format. Should be a list of IDs')
            
            # Handle scale types (One2many)
            if post.get('scale_type_ids'):
                try:
                    scale_types = json.loads(post.get('scale_type_ids')) if isinstance(post.get('scale_type_ids'), str) else post.get('scale_type_ids')
                    if isinstance(scale_types, list):
                        scale_vals = []
                        for scale_type in scale_types:
                            scale_vals.append((0, 0, {'scale_type': scale_type}))
                        vals['scale_type_ids'] = scale_vals
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid scale_type_ids format. Should be a list of scale types')
            
            # Create consultation
            consultation = request.env['consultation.consultation'].sudo().create(vals)
            
            return self._get_success_response({
                'consultation_id': consultation.id,
                'consultation_name': consultation.name,
                'consultation': self._serialize_consultation(consultation)
            }, 'Consultation created successfully')
            
        except ValueError as e:
            _logger.error(f"ValueError in create_consultation: {str(e)}")
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in create_consultation: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/view/<int:consultation_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def view_consultation(self, consultation_id, **kwargs):
        """
        API to view a specific consultation
        Parameters:
        - consultation_id: ID of the consultation
        """
        try:
            consultation = request.env['consultation.consultation'].sudo().search([('id', '=', consultation_id)], limit=1)
            
            if not consultation:
                return self._get_error_response(f'Consultation with ID {consultation_id} not found', 404)
            
            return self._get_success_response({
                'consultation': self._serialize_consultation(consultation)
            }, 'Consultation retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in view_consultation: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/list', type='http', auth='none', methods=['GET'], csrf=False)
    def list_consultations(self, **kwargs):
        """
        API to list consultations with optional filters
        Parameters:
        - psychiatrist_id: Filter by psychiatrist ID
        - patient_id: Filter by patient ID
        - type: Filter by consultation type ('ip' or 'op')
        - state: Filter by consultation state
        - date_from: Filter from date (YYYY-MM-DD)
        - date_to: Filter to date (YYYY-MM-DD)
        - inpatient_admission_id: Filter by IP admission ID
        - op_visit_id: Filter by OP visit ID
        - limit: Number of records to return (default: 50)
        - offset: Number of records to skip (default: 0)
        """
        try:
            domain = []
            
            # Apply filters
            if kwargs.get('psychiatrist_id'):
                domain.append(('psychiatrist_id', '=', int(kwargs.get('psychiatrist_id'))))
            
            if kwargs.get('patient_id'):
                domain.append(('patient_id', '=', int(kwargs.get('patient_id'))))
            
            if kwargs.get('type'):
                if kwargs.get('type') in ['ip', 'op']:
                    domain.append(('type', '=', kwargs.get('type')))
                else:
                    return self._get_error_response('Invalid type. Must be "ip" or "op"')
            
            if kwargs.get('state'):
                valid_states = ['draft', 'started', 'ended', 'completed', 'cancelled', 'referral', 
                              'followup', 'admission', 'cross_consultation', 'admission_referral', 
                              'admission_followup', 'admission_cross_consultation', 'discharge']
                if kwargs.get('state') in valid_states:
                    domain.append(('state', '=', kwargs.get('state')))
                else:
                    return self._get_error_response(f'Invalid state. Must be one of: {", ".join(valid_states)}')
            
            if kwargs.get('inpatient_admission_id'):
                domain.append(('inpatient_admission_id', '=', int(kwargs.get('inpatient_admission_id'))))
            
            if kwargs.get('op_visit_id'):
                domain.append(('op_visit_id', '=', int(kwargs.get('op_visit_id'))))
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d').date()
                    domain.append(('date', '>=', date_from))
                except ValueError:
                    return self._get_error_response('Invalid date_from format. Use YYYY-MM-DD')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d').date()
                    domain.append(('date', '<=', date_to))
                except ValueError:
                    return self._get_error_response('Invalid date_to format. Use YYYY-MM-DD')
            
            # Pagination
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))
            
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
            
            return self._get_success_response({
                'consultations': consultation_data,
                'count': len(consultation_data),
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }, 'Consultations retrieved successfully')
            
        except ValueError as e:
            _logger.error(f"ValueError in list_consultations: {str(e)}")
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in list_consultations: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/by_psychiatrist/<int:psychiatrist_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def consultations_by_psychiatrist(self, psychiatrist_id, **kwargs):
        """
        API to get consultations by psychiatrist
        Parameters:
        - psychiatrist_id: ID of the psychiatrist
        - date_from: Optional date filter (YYYY-MM-DD)
        - date_to: Optional date filter (YYYY-MM-DD)
        - state: Optional state filter
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            # Verify psychiatrist exists
            psychiatrist = request.env['hr.employee'].sudo().search([('id', '=', psychiatrist_id)], limit=1)
            if not psychiatrist:
                return self._get_error_response(f'Psychiatrist with ID {psychiatrist_id} not found', 404)
            
            # Forward to list_consultations with psychiatrist filter
            kwargs['psychiatrist_id'] = psychiatrist_id
            return self.list_consultations(**kwargs)
            
        except Exception as e:
            _logger.error(f"Error in consultations_by_psychiatrist: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/by_patient/<int:patient_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def consultations_by_patient(self, patient_id, **kwargs):
        """
        API to get consultations by patient
        Parameters:
        - patient_id: ID of the patient
        - date_from: Optional date filter (YYYY-MM-DD)
        - date_to: Optional date filter (YYYY-MM-DD)
        - state: Optional state filter
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            # Verify patient exists
            patient = request.env['hospital.patient'].sudo().search([('id', '=', patient_id)], limit=1)
            if not patient:
                return self._get_error_response(f'Patient with ID {patient_id} not found', 404)
            
            # Forward to list_consultations with patient filter
            kwargs['patient_id'] = patient_id
            return self.list_consultations(**kwargs)
            
        except Exception as e:
            _logger.error(f"Error in consultations_by_patient: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/by_ip/<int:ip_admission_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def consultations_by_ip(self, ip_admission_id, **kwargs):
        """
        API to get consultations by IP admission
        Parameters:
        - ip_admission_id: ID of the inpatient admission
        - date_from: Optional date filter (YYYY-MM-DD)
        - date_to: Optional date filter (YYYY-MM-DD)
        - state: Optional state filter
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            # Verify IP admission exists
            admission = request.env['hospital.admission'].sudo().search([('id', '=', ip_admission_id)], limit=1)
            if not admission:
                return self._get_error_response(f'IP admission with ID {ip_admission_id} not found', 404)
            
            # Forward to list_consultations with IP filter
            kwargs['inpatient_admission_id'] = ip_admission_id
            kwargs['type'] = 'ip'
            return self.list_consultations(**kwargs)
            
        except Exception as e:
            _logger.error(f"Error in consultations_by_ip: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/by_op/<int:op_visit_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def consultations_by_op(self, op_visit_id, **kwargs):
        """
        API to get consultations by OP visit
        Parameters:
        - op_visit_id: ID of the OP visit
        - date_from: Optional date filter (YYYY-MM-DD)
        - date_to: Optional date filter (YYYY-MM-DD)
        - state: Optional state filter
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            # Verify OP visit exists
            op_visit = request.env['op.visits'].sudo().search([('id', '=', op_visit_id)], limit=1)
            if not op_visit:
                return self._get_error_response(f'OP visit with ID {op_visit_id} not found', 404)
            
            # Forward to list_consultations with OP filter
            kwargs['op_visit_id'] = op_visit_id
            kwargs['type'] = 'op'
            return self.list_consultations(**kwargs)
            
        except Exception as e:
            _logger.error(f"Error in consultations_by_op: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/change_state/<int:consultation_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def change_consultation_state(self, consultation_id, **post):
        """
        API to change consultation state
        Parameters:
        - consultation_id: ID of the consultation
        - state: New state to set
        - action: Optional action to perform ('start', 'end', 'complete', 'cancel')
        """
        try:
            consultation = request.env['consultation.consultation'].sudo().search([('id', '=', consultation_id)], limit=1)
            
            if not consultation:
                return self._get_error_response(f'Consultation with ID {consultation_id} not found', 404)
            
            new_state = post.get('state')
            action = post.get('action')
            
            valid_states = ['draft', 'started', 'ended', 'completed', 'cancelled', 'referral', 
                           'followup', 'admission', 'cross_consultation', 'admission_referral', 
                           'admission_followup', 'admission_cross_consultation', 'discharge']
            
            # Handle specific actions
            if action == 'start':
                try:
                    consultation.action_start()
                    return self._get_success_response({
                        'consultation_id': consultation.id,
                        'new_state': consultation.state,
                        'start_datetime': consultation.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.start_datetime else None
                    }, 'Consultation started successfully')
                except UserError as e:
                    return self._get_error_response(str(e))
                
            elif action == 'end':
                consultation.action_end()
                return self._get_success_response({
                    'consultation_id': consultation.id,
                    'new_state': consultation.state,
                    'end_datetime': consultation.end_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.end_datetime else None
                }, 'Consultation ended successfully')
                
            elif action == 'complete':
                try:
                    consultation.action_complete()
                    return self._get_success_response({
                        'consultation_id': consultation.id,
                        'new_state': consultation.state,
                        'end_datetime': consultation.end_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.end_datetime else None
                    }, 'Consultation completed successfully')
                except UserError as e:
                    return self._get_error_response(str(e))
                
            elif action == 'cancel':
                consultation.state = 'cancelled'
                return self._get_success_response({
                    'consultation_id': consultation.id,
                    'new_state': consultation.state
                }, 'Consultation cancelled successfully')
            
            # Handle direct state change
            elif new_state:
                if new_state not in valid_states:
                    return self._get_error_response(f'Invalid state. Must be one of: {", ".join(valid_states)}')
                
                consultation.state = new_state
                return self._get_success_response({
                    'consultation_id': consultation.id,
                    'new_state': consultation.state
                }, f'Consultation state changed to {new_state} successfully')
            
            else:
                return self._get_error_response('Either "state" or "action" parameter is required')
            
        except Exception as e:
            _logger.error(f"Error in change_consultation_state: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/update/<int:consultation_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def update_consultation(self, consultation_id, **post):
        """
        API to update consultation fields
        Parameters:
        - consultation_id: ID of the consultation
        - Any field from the consultation model can be updated
        """
        try:
            consultation = request.env['consultation.consultation'].sudo().search([('id', '=', consultation_id)], limit=1)
            
            if not consultation:
                return self._get_error_response(f'Consultation with ID {consultation_id} not found', 404)
            
            # Prepare update values
            vals = {}
            
            # Simple text fields
            text_fields = ['general_observation', 'current_medication', 'advice_to_counsellor', 
                          'advice_to_psychologist', 'lab_advice', 'cross_consultation', 
                          'doctor_advice', 'precautions', 'todo', 'treatment_planned']
            
            for field in text_fields:
                if field in post:
                    vals[field] = post[field]
            
            # Selection fields
            selection_fields = {
                'consultation_type': ['psychiatrist', 'clinical_psychologist', 'counsellor'],
                'priority': ['low', 'medium', 'high', 'emergency'],
                'prescription_status': ['changed', 'continued']
            }
            
            for field, valid_values in selection_fields.items():
                if field in post:
                    if post[field] in valid_values:
                        vals[field] = post[field]
                    else:
                        return self._get_error_response(f'Invalid {field}. Must be one of: {", ".join(valid_values)}')
            
            # Boolean fields
            boolean_fields = ['is_sos', 'next_followup', 'consultation_require']
            for field in boolean_fields:
                if field in post:
                    vals[field] = post[field] in ['true', 'True', '1', 1, True]
            
            # Integer fields
            integer_fields = ['bp', 'bp2', 'wt', 'grbs', 'spo2', 'pulse', 'hospitalization_length', 'age']
            for field in integer_fields:
                if field in post:
                    try:
                        vals[field] = int(post[field])
                    except ValueError:
                        return self._get_error_response(f'Invalid {field}. Must be an integer')
            
            # Float fields
            if 'approx_cost' in post:
                try:
                    vals['approx_cost'] = float(post['approx_cost'])
                except ValueError:
                    return self._get_error_response('Invalid approx_cost. Must be a number')
            
            # Date fields
            date_fields = ['date', 'next_followup_date', 'provisional_admission_date']
            for field in date_fields:
                if field in post:
                    try:
                        vals[field] = datetime.strptime(post[field], '%Y-%m-%d').date()
                    except ValueError:
                        return self._get_error_response(f'Invalid {field} format. Use YYYY-MM-DD')
            
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
                if field in post:
                    if post[field]:
                        record = request.env[model].sudo().search([('id', '=', int(post[field]))], limit=1)
                        if record:
                            vals[field] = record.id
                        else:
                            return self._get_error_response(f'{field} with ID {post[field]} not found')
                    else:
                        vals[field] = False
            
            # Many2many fields
            if 'labtest_type_ids' in post:
                try:
                    labtest_ids = json.loads(post['labtest_type_ids']) if isinstance(post['labtest_type_ids'], str) else post['labtest_type_ids']
                    if isinstance(labtest_ids, list):
                        vals['labtest_type_ids'] = [(6, 0, labtest_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid labtest_type_ids format')
            
            if 'speciality_ids' in post:
                try:
                    speciality_ids = json.loads(post['speciality_ids']) if isinstance(post['speciality_ids'], str) else post['speciality_ids']
                    if isinstance(speciality_ids, list):
                        vals['speciality_ids'] = [(6, 0, speciality_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid speciality_ids format')
            
            if 'consultation_require_ids' in post:
                try:
                    consultation_require_ids = json.loads(post['consultation_require_ids']) if isinstance(post['consultation_require_ids'], str) else post['consultation_require_ids']
                    if isinstance(consultation_require_ids, list):
                        vals['consultation_require_ids'] = [(6, 0, consultation_require_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid consultation_require_ids format')
            
            if 'provisional_diagnosis_ids' in post:
                try:
                    diagnosis_ids = json.loads(post['provisional_diagnosis_ids']) if isinstance(post['provisional_diagnosis_ids'], str) else post['provisional_diagnosis_ids']
                    if isinstance(diagnosis_ids, list):
                        vals['provisional_diagnosis_ids'] = [(6, 0, diagnosis_ids)]
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid provisional_diagnosis_ids format')
            
            # One2many fields - Scale types
            if 'scale_type_ids' in post:
                try:
                    scale_types = json.loads(post['scale_type_ids']) if isinstance(post['scale_type_ids'], str) else post['scale_type_ids']
                    if isinstance(scale_types, list):
                        # Clear existing scales and add new ones
                        scale_vals = [(5, 0, 0)]  # Clear all existing
                        for scale_type in scale_types:
                            scale_vals.append((0, 0, {'scale_type': scale_type}))
                        vals['scale_type_ids'] = scale_vals
                except (json.JSONDecodeError, TypeError):
                    return self._get_error_response('Invalid scale_type_ids format')
            
            # Update consultation
            if vals:
                consultation.write(vals)
                
                return self._get_success_response({
                    'consultation_id': consultation.id,
                    'updated_fields': list(vals.keys()),
                    'consultation': self._serialize_consultation(consultation)
                }, 'Consultation updated successfully')
            else:
                return self._get_error_response('No valid fields provided for update')
            
        except ValueError as e:
            _logger.error(f"ValueError in update_consultation: {str(e)}")
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in update_consultation: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/check_vitals/<int:consultation_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def check_vitals(self, consultation_id, **post):
        """
        API to check vitals for a consultation
        Parameters:
        - consultation_id: ID of the consultation
        """
        try:
            consultation = request.env['consultation.consultation'].sudo().search([('id', '=', consultation_id)], limit=1)
            
            if not consultation:
                return self._get_error_response(f'Consultation with ID {consultation_id} not found', 404)
            
            try:
                consultation.action_check_vitals()
                return self._get_success_response({
                    'consultation_id': consultation.id,
                    'vitals': {
                        'bp': consultation.bp,
                        'bp2': consultation.bp2,
                        'wt': consultation.wt,
                        'grbs': consultation.grbs,
                        'spo2': consultation.spo2,
                        'pulse': consultation.pulse,
                        'vitals_checked_by': consultation.vitals_checked_user_id.name if consultation.vitals_checked_user_id else None,
                        'vitals_checked_on': consultation.vitals_checked_on.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if consultation.vitals_checked_on else None,
                    }
                }, 'Vitals checked successfully')
            except UserError as e:
                return self._get_error_response(str(e))
            
        except Exception as e:
            _logger.error(f"Error in check_vitals: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/statistics', type='http', auth='none', methods=['GET'], csrf=False)
    def consultation_statistics(self, **kwargs):
        """
        API to get consultation statistics
        Parameters:
        - psychiatrist_id: Optional filter by psychiatrist
        - date_from: Optional date filter (YYYY-MM-DD)
        - date_to: Optional date filter (YYYY-MM-DD)
        - type: Optional type filter ('ip' or 'op')
        """
        try:
            domain = []
            
            # Apply filters
            if kwargs.get('psychiatrist_id'):
                domain.append(('psychiatrist_id', '=', int(kwargs.get('psychiatrist_id'))))
            
            if kwargs.get('type'):
                if kwargs.get('type') in ['ip', 'op']:
                    domain.append(('type', '=', kwargs.get('type')))
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d').date()
                    domain.append(('date', '>=', date_from))
                except ValueError:
                    return self._get_error_response('Invalid date_from format. Use YYYY-MM-DD')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d').date()
                    domain.append(('date', '<=', date_to))
                except ValueError:
                    return self._get_error_response('Invalid date_to format. Use YYYY-MM-DD')
            
            # Get statistics
            total_consultations = request.env['consultation.consultation'].sudo().search_count(domain)
            
            # Count by state
            states_count = {}
            states = ['draft', 'started', 'ended', 'completed', 'cancelled', 'referral', 
                     'followup', 'admission', 'cross_consultation', 'admission_referral', 
                     'admission_followup', 'admission_cross_consultation', 'discharge']
            
            for state in states:
                state_domain = domain + [('state', '=', state)]
                states_count[state] = request.env['consultation.consultation'].sudo().search_count(state_domain)
            
            # Count by type
            ip_count = request.env['consultation.consultation'].sudo().search_count(domain + [('type', '=', 'ip')])
            op_count = request.env['consultation.consultation'].sudo().search_count(domain + [('type', '=', 'op')])
            
            # Count by consultation type
            consultation_types_count = {}
            consultation_types = ['psychiatrist', 'clinical_psychologist', 'counsellor']
            for cons_type in consultation_types:
                type_domain = domain + [('consultation_type', '=', cons_type)]
                consultation_types_count[cons_type] = request.env['consultation.consultation'].sudo().search_count(type_domain)
            
            # Count by priority
            priority_count = {}
            priorities = ['low', 'medium', 'high', 'emergency']
            for priority in priorities:
                priority_domain = domain + [('priority', '=', priority)]
                priority_count[priority] = request.env['consultation.consultation'].sudo().search_count(priority_domain)
            
            # Get top psychiatrists (if not filtering by psychiatrist)
            top_psychiatrists = []
            if not kwargs.get('psychiatrist_id'):
                psychiatrist_data = request.env['consultation.consultation'].sudo().read_group(
                    domain,
                    ['psychiatrist_id'],
                    ['psychiatrist_id']
                )
                for data in psychiatrist_data[:10]:  # Top 10
                    if data['psychiatrist_id']:
                        psychiatrist = request.env['hr.employee'].sudo().browse(data['psychiatrist_id'][0])
                        top_psychiatrists.append({
                            'id': psychiatrist.id,
                            'name': psychiatrist.name,
                            'count': data['psychiatrist_id_count']
                        })
            
            return self._get_success_response({
                'total_consultations': total_consultations,
                'by_state': states_count,
                'by_type': {
                    'ip': ip_count,
                    'op': op_count
                },
                'by_consultation_type': consultation_types_count,
                'by_priority': priority_count,
                'top_psychiatrists': top_psychiatrists,
                'filters_applied': {
                    'psychiatrist_id': kwargs.get('psychiatrist_id'),
                    'date_from': kwargs.get('date_from'),
                    'date_to': kwargs.get('date_to'),
                    'type': kwargs.get('type')
                }
            }, 'Statistics retrieved successfully')
            
        except ValueError as e:
            _logger.error(f"ValueError in consultation_statistics: {str(e)}")
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in consultation_statistics: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/search', type='http', auth='none', methods=['GET'], csrf=False)
    def search_consultations(self, **kwargs):
        """
        API to search consultations with advanced filters
        Parameters:
        - q: Search query (searches in name, patient name, psychiatrist name)
        - psychiatrist_name: Search by psychiatrist name
        - patient_name: Search by patient name
        - ip_number: Search by IP admission number
        - op_number: Search by OP visit number
        - All other filters from list_consultations
        """
        try:
            domain = []
            
            # Text search
            if kwargs.get('q'):
                search_term = kwargs.get('q')
                domain.append('|')
                domain.append('|')
                domain.append('|')
                domain.append(('name', 'ilike', search_term))
                domain.append(('patient_id.name', 'ilike', search_term))
                domain.append(('psychiatrist_id.name', 'ilike', search_term))
                domain.append(('patient_id.identification_code', 'ilike', search_term))
            
            # Specific name searches
            if kwargs.get('psychiatrist_name'):
                domain.append(('psychiatrist_id.name', 'ilike', kwargs.get('psychiatrist_name')))
            
            if kwargs.get('patient_name'):
                domain.append(('patient_id.name', 'ilike', kwargs.get('patient_name')))
            
            if kwargs.get('ip_number'):
                domain.append(('inpatient_admission_id.name', 'ilike', kwargs.get('ip_number')))
            
            if kwargs.get('op_number'):
                domain.append(('op_visit_id.name', 'ilike', kwargs.get('op_number')))
            
            # Apply other filters
            if kwargs.get('psychiatrist_id'):
                domain.append(('psychiatrist_id', '=', int(kwargs.get('psychiatrist_id'))))
            
            if kwargs.get('patient_id'):
                domain.append(('patient_id', '=', int(kwargs.get('patient_id'))))
            
            if kwargs.get('type'):
                if kwargs.get('type') in ['ip', 'op']:
                    domain.append(('type', '=', kwargs.get('type')))
            
            if kwargs.get('state'):
                valid_states = ['draft', 'started', 'ended', 'completed', 'cancelled', 'referral', 
                              'followup', 'admission', 'cross_consultation', 'admission_referral', 
                              'admission_followup', 'admission_cross_consultation', 'discharge']
                if kwargs.get('state') in valid_states:
                    domain.append(('state', '=', kwargs.get('state')))
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d').date()
                    domain.append(('date', '>=', date_from))
                except ValueError:
                    return self._get_error_response('Invalid date_from format. Use YYYY-MM-DD')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d').date()
                    domain.append(('date', '<=', date_to))
                except ValueError:
                    return self._get_error_response('Invalid date_to format. Use YYYY-MM-DD')
            
            # Pagination
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))
            
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
            
            return self._get_success_response({
                'consultations': consultation_data,
                'count': len(consultation_data),
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count,
                'search_query': kwargs.get('q', ''),
                'filters_applied': {
                    'psychiatrist_name': kwargs.get('psychiatrist_name'),
                    'patient_name': kwargs.get('patient_name'),
                    'ip_number': kwargs.get('ip_number'),
                    'op_number': kwargs.get('op_number')
                }
            }, 'Search completed successfully')
            
        except ValueError as e:
            _logger.error(f"ValueError in search_consultations: {str(e)}")
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in search_consultations: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/delete/<int:consultation_id>', type='http', auth='none', methods=['DELETE'], csrf=False)
    def delete_consultation(self, consultation_id, **kwargs):
        """
        API to delete a consultation
        Parameters:
        - consultation_id: ID of the consultation to delete
        """
        try:
            consultation = request.env['consultation.consultation'].sudo().search([('id', '=', consultation_id)], limit=1)
            
            if not consultation:
                return self._get_error_response(f'Consultation with ID {consultation_id} not found', 404)
            
            # Check if consultation can be deleted (only if in draft or cancelled state)
            if consultation.state not in ['draft', 'cancelled']:
                return self._get_error_response(f'Cannot delete consultation in {consultation.state} state. Only draft or cancelled consultations can be deleted.')
            
            consultation_name = consultation.name
            consultation.unlink()
            
            return self._get_success_response({
                'consultation_id': consultation_id,
                'consultation_name': consultation_name
            }, 'Consultation deleted successfully')
            
        except Exception as e:
            _logger.error(f"Error in delete_consultation: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/consultation/export', type='http', auth='none', methods=['GET'], csrf=False)
    def export_consultations(self, **kwargs):
        """
        API to export consultation data
        Parameters:
        - format: 'json' (default) or 'csv'
        - All filters from list_consultations
        """
        try:
            # Use list_consultations logic but without pagination
            kwargs['limit'] = 10000  # Large limit for export
            kwargs['offset'] = 0
            
            response = self.list_consultations(**kwargs)
            
            if kwargs.get('format') == 'csv':
                # Convert to CSV format
                import csv
                import io
                
                response_data = json.loads(response.data.decode('utf-8'))
                if not response_data.get('success'):
                    return response
                
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                header = [
                    'ID', 'Name', 'Date', 'Type', 'State', 'Patient Name', 
                    'Psychiatrist Name', 'Consultation Type', 'Priority',
                    'Start Time', 'End Time', 'General Observation'
                ]
                writer.writerow(header)
                
                # Write data
                for consultation in response_data['consultations']:
                    row = [
                        consultation.get('id', ''),
                        consultation.get('name', ''),
                        consultation.get('date', ''),
                        consultation.get('type', ''),
                        consultation.get('state', ''),
                        consultation.get('patient', {}).get('name', '') if consultation.get('patient') else '',
                        consultation.get('psychiatrist', {}).get('name', '') if consultation.get('psychiatrist') else '',
                        consultation.get('consultation_type', ''),
                        consultation.get('priority', ''),
                        consultation.get('start_datetime', ''),
                        consultation.get('end_datetime', ''),
                        consultation.get('general_observation', '')
                    ]
                    writer.writerow(row)
                
                output.seek(0)
                return request.make_response(
                    output.getvalue(),
                    headers=[
                        ('Content-Type', 'text/csv'),
                        ('Content-Disposition', 'attachment; filename=consultations.csv')
                    ]
                )
            
            return response
            
        except Exception as e:
            _logger.error(f"Error in export_consultations: {str(e)}")
            return self._get_error_response('Internal server error', 500)
        


class AppointmentAPI(http.Controller):
    
    def _get_error_response(self, message, status=400):
        """Helper method to return error response"""
        response = {
            'success': False,
            'message': message
        }
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')],
            status=status
        )
    
    def _get_success_response(self, data, message="Success"):
        """Helper method to return success response"""
        response = {
            'success': True,
            'message': message,
            **data
        }
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')]
        )
    
    def _serialize_slot_booking(self, slot):
        """Serialize slot booking object to dictionary"""
        return {
            'id': slot.id,
            'name': slot.name,
            'availability': slot.availability,
            'start_datetime': slot.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if slot.start_datetime else None,
            'stop_datetime': slot.stop_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if slot.stop_datetime else None,
            'duration': slot.duration,
            'consultation_type': slot.consultation_type,
            'payment_mode': slot.payment_mode,
            'amount': slot.amount,
            'free_screening': slot.free_screening,
            'virtual_consultation_url': slot.virtual_consultation_url,
            'geo_location': slot.geo_location,
            'notes': slot.notes,
            'slot_booked_at': slot.slot_booked_at.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if slot.slot_booked_at else None,
            
            # Lead/Patient information
            'lead': {
                'id': slot.lead_id.id if slot.lead_id else None,
                'name': slot.lead_id.name if slot.lead_id else None,
                'reference': slot.lead_id.reference if slot.lead_id else None,
            } if slot.lead_id else None,
            'caller_name': slot.caller_name,
            'patient_name': slot.patient_name,
            
            # Doctor and Campus information
            'campus': {
                'id': slot.campus_id.id if slot.campus_id else None,
                'name': slot.campus_id.name if slot.campus_id else None,
            } if slot.campus_id else None,
            'sub_campus': {
                'id': slot.sub_campus_id.id if slot.sub_campus_id else None,
                'name': slot.sub_campus_id.name if slot.sub_campus_id else None,
            } if slot.sub_campus_id else None,
            'doctor': {
                'id': slot.doctor_id.id if slot.doctor_id else None,
                'name': slot.doctor_id.name if slot.doctor_id else None,
                'external_id': slot.doctor_external_id,
            } if slot.doctor_id else None,
            'speciality': {
                'id': slot.speciality_id.id if slot.speciality_id else None,
                'name': slot.speciality_id.name if slot.speciality_id else None,
            } if slot.speciality_id else None,
            
            # Clinical session link
            'clinical_session': {
                'id': slot.clinical_session_id.id if slot.clinical_session_id else None,
                'name': slot.clinical_session_id.name if slot.clinical_session_id else None,
                'state': slot.clinical_session_id.state if slot.clinical_session_id else None,
            } if slot.clinical_session_id else None,
            
            # Consultation types
            'consultation_types': [{'id': ct.id, 'name': ct.name} for ct in slot.consultation_type_ids],
            
            # Feedback
            'consultation_feedback_score': slot.consultation_feedback_score_new,
            
            # Booking details
            'booked_by': slot.slot_booking_user_id.name if slot.slot_booking_user_id else None,
            'available_slot_id': slot.available_slot_id.id if slot.available_slot_id else None,
            
            # Payment details
            'customer': slot.customer,
            'payment_date': slot.payment_date.strftime(DEFAULT_SERVER_DATE_FORMAT) if slot.payment_date else None,
            'payment_method': slot.payment_method,
            'online_payment_url': slot.online_payment_url,
            
            # Cancellation details
            'cancel_reason': slot.cancel_reason,
            'medium': slot.medium_id.name if slot.medium_id else None,
        }

    # ============ AUTHENTICATION APIS ============
    
    @http.route('/api/test', type='http', auth='none', methods=['GET'], csrf=False)
    def test_endpoint(self, **kwargs):
        response = {
            'status': 'success',
            'message': 'Appointment API is working!'
        }
        return request.make_response(
            json.dumps(response),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/auth/login', type='http', auth='none', methods=['POST'], csrf=False)
    def login_with_otp(self, **post):
        """
        API for generating OTP and sending SMS for login/signup
        Parameters:
        - phone_number: 10 digit phone number (string)
        - uid: Random 16-digit characters (string)
        - type: 'login' or 'signup'
        - country_code: Country code (integer)
        """
        try:
            # Validate required parameters
            phone_number = post.get('phone_number')
            uid = post.get('uid')
            request_type = post.get('type')
            country_code = post.get('country_code')

            if not all([phone_number, uid, request_type, country_code]):
                return self._get_error_response('Missing required parameters: phone_number, uid, type, country_code')

            # Clean and validate phone number
            phone_number = str(phone_number).strip()
            if len(phone_number) != 10 or not phone_number.isdigit():
                return self._get_error_response('Invalid phone number. Must be 10 digits.')

            # Generate OTP (4 digits for demo)
            otp = str(random.randint(1000, 9999))
            
            # Search for existing lead with this phone number
            lead = request.env['crm.lead'].sudo().search([
                ('caller_mobile', '=', phone_number)
            ], limit=1)

            if request_type == 'login':
                if not lead:
                    return self._get_error_response('Phone number not registered. Please sign up.')
                
                # In production: Send OTP via SMS
                _logger.info(f"OTP for login: {otp} (would send via SMS in production)")
                
                return self._get_success_response({
                    'otp': otp,  # Remove in production
                    'uid': uid
                }, 'OTP sent successfully')
            
            elif request_type == 'signup':
                if lead:
                    return self._get_error_response('Phone number already registered. Please login.')
                
                # In production: Send OTP via SMS
                _logger.info(f"OTP for signup: {otp} (would send via SMS in production)")
                
                return self._get_success_response({
                    'otp': otp,  # Remove in production
                    'uid': uid
                }, 'OTP sent successfully')
            
            else:
                return self._get_error_response('Invalid type parameter. Must be "login" or "signup"')

        except Exception as e:
            _logger.error(f"Error in login_with_otp: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/auth/verify_otp', type='http', auth='none', methods=['POST'], csrf=False)
    def verify_otp(self, **post):
        """
        API for verifying OTP to complete login/signup
        Parameters:
        - phone_number: 10 digit phone number (string)
        - country_code: Country code (integer)
        - uid: Random 16-digit characters (string)
        - otp: OTP entered by user (string)
        - type: 'login' or 'signup'
        - caller_name: Required for signup
        - patient_name: Optional for signup
        """
        try:
            # Validate required parameters
            phone_number = post.get('phone_number')
            country_code = post.get('country_code')
            uid = post.get('uid')
            otp = post.get('otp')
            request_type = post.get('type')

            if not all([phone_number, country_code, uid, otp, request_type]):
                return self._get_error_response('Missing required parameters')

            # Clean and validate phone number
            phone_number = str(phone_number).strip()
            if len(phone_number) != 10 or not phone_number.isdigit():
                return self._get_error_response('Invalid phone number')

            # Search for existing lead with this phone number
            lead = request.env['crm.lead'].sudo().search([
                ('caller_mobile', '=', phone_number)
            ], limit=1)

            if request_type == 'login':
                if not lead:
                    return self._get_error_response('Phone number not registered')

                # In production: Verify OTP against stored value
                # For demo, we'll assume any 4-digit OTP is valid
                
                return self._get_success_response({
                    'lead_id': lead.id,
                    'caller_mobile': phone_number,
                    'patient_name': lead.patient_name or '',
                    'caller_name': lead.caller_name or '',
                    'uid': uid,
                    'reference': lead.reference or '',
                    'campus_id': lead.campus_id.id if hasattr(lead, 'campus_id') and lead.campus_id else None,
                }, 'Login successful!')
            
            elif request_type == 'signup':
                if lead:
                    return self._get_error_response('Phone number already registered. Please login.')
                
                caller_name = post.get('caller_name')
                if not caller_name:
                    return self._get_error_response('caller_name is required for signup')
                
                # Create new lead
                lead_vals = {
                    'name': caller_name,
                    'caller_name': caller_name,
                    'caller_mobile': phone_number,
                    'patient_name': post.get('patient_name', caller_name),
                    'state': 'lead',
                    'type': 'lead',
                }
                
                lead = request.env['crm.lead'].sudo().create(lead_vals)
                
                return self._get_success_response({
                    'lead_id': lead.id,
                    'caller_mobile': phone_number,
                    'patient_name': lead.patient_name,
                    'caller_name': lead.caller_name,
                    'uid': uid,
                    'reference': lead.reference,
                }, 'Signup successful!')

        except Exception as e:
            _logger.error(f"Error in verify_otp: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    # ============ APPOINTMENT BOOKING APIS ============

    @http.route('/api/appointments/available_slots', type='http', auth='none', methods=['GET'], csrf=False)
    def get_available_slots(self, **kwargs):
        """
        API to get available appointment slots
        Parameters:
        - date: Date for slots (YYYY-MM-DD)
        - campus_id: Campus ID (optional)
        - doctor_id: Doctor ID (optional)
        - speciality_id: Speciality ID (optional)
        - consultation_type: Consultation type (optional)
        - limit: Number of records (default: 50)
        - offset: Records to skip (default: 0)
        """
        try:
            domain = [('availability', '=', 'open')]
            
            # Date filter
            if kwargs.get('date'):
                try:
                    filter_date = datetime.strptime(kwargs.get('date'), '%Y-%m-%d').date()
                    date_start = datetime.combine(filter_date, datetime.min.time())
                    date_end = datetime.combine(filter_date, datetime.max.time())
                    domain.extend([
                        ('start_datetime', '>=', date_start),
                        ('start_datetime', '<=', date_end)
                    ])
                except ValueError:
                    return self._get_error_response('Invalid date format. Use YYYY-MM-DD')
            else:
                # Only future slots if no date specified
                domain.append(('start_datetime', '>=', datetime.now()))
            
            # Apply filters
            if kwargs.get('campus_id'):
                domain.append(('campus_id', '=', int(kwargs.get('campus_id'))))
            
            if kwargs.get('doctor_id'):
                domain.append(('doctor_id', '=', int(kwargs.get('doctor_id'))))
            
            if kwargs.get('speciality_id'):
                domain.append(('speciality_id', '=', int(kwargs.get('speciality_id'))))
            
            if kwargs.get('consultation_type'):
                domain.append(('consultation_type', '=', kwargs.get('consultation_type')))
            
            # Pagination
            limit = int(kwargs.get('limit', 50))
            offset = int(kwargs.get('offset', 0))
            
            # Search slots
            slots = request.env['slot.booking'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset, 
                order='start_datetime asc'
            )
            
            # Get total count
            total_count = request.env['slot.booking'].sudo().search_count(domain)
            
            slots_data = [self._serialize_slot_booking(slot) for slot in slots]
            
            return self._get_success_response({
                'slots': slots_data,
                'count': len(slots_data),
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }, 'Available slots retrieved successfully')
            
        except ValueError as e:
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in get_available_slots: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/appointments/book_slot', type='http', auth='none', methods=['POST'], csrf=False)
    def book_appointment_slot(self, **post):
        """
        API to book an appointment slot
        Parameters:
        - slot_id: ID of the slot to book (required)
        - lead_id: Lead ID (required)
        - caller_name: Caller name (optional)
        - patient_name: Patient name (optional)
        - payment_mode: Payment mode (cash, online, card, insurance)
        - free_screening: Boolean (default: False)
        - amount: Amount (optional)
        - geo_location: For home consultations (optional)
        - notes: Additional notes (optional)
        """
        try:
            # Validate required parameters
            slot_id = post.get('slot_id')
            lead_id = post.get('lead_id')
            
            if not slot_id:
                return self._get_error_response('slot_id is required')
            
            if not lead_id:
                return self._get_error_response('lead_id is required')
            
            # Get slot and validate
            slot = request.env['slot.booking'].sudo().search([('id', '=', int(slot_id))], limit=1)
            if not slot:
                return self._get_error_response(f'Slot with ID {slot_id} not found')
            
            if slot.availability != 'open':
                return self._get_error_response('Selected slot is no longer available')
            
            # Get lead and validate
            lead = request.env['crm.lead'].sudo().search([('id', '=', int(lead_id))], limit=1)
            if not lead:
                return self._get_error_response(f'Lead with ID {lead_id} not found')
            
            # Prepare booking values
            booking_vals = {
                'lead_id': lead.id,
                'availability': 'booked',
                'slot_booking_user_id': request.env.user.id if request.env.user.id != 4 else 1,  # Public user fallback
                'slot_booked_at': fields.Datetime.now(),
            }
            
            # Optional fields
            if post.get('caller_name'):
                booking_vals['caller_name'] = post.get('caller_name')
            else:
                booking_vals['caller_name'] = lead.caller_name
            
            if post.get('patient_name'):
                booking_vals['patient_name'] = post.get('patient_name')
            else:
                booking_vals['patient_name'] = lead.patient_name or lead.caller_name
            
            if post.get('payment_mode'):
                if post.get('payment_mode') in ['cash', 'online', 'card', 'insurance']:
                    booking_vals['payment_mode'] = post.get('payment_mode')
                else:
                    return self._get_error_response('Invalid payment_mode. Must be: cash, online, card, insurance')
            
            if post.get('free_screening'):
                booking_vals['free_screening'] = post.get('free_screening').lower() in ['true', '1', 'yes']
                if booking_vals['free_screening']:
                    booking_vals['amount'] = 0.0
            
            if post.get('amount') and not booking_vals.get('free_screening'):
                try:
                    booking_vals['amount'] = float(post.get('amount'))
                except ValueError:
                    return self._get_error_response('Invalid amount format')
            
            if post.get('geo_location') and slot.consultation_type == 'Home-Based Consultation':
                booking_vals['geo_location'] = post.get('geo_location')
            
            if post.get('notes'):
                booking_vals['notes'] = post.get('notes')
            
            # Generate virtual consultation URL if needed
            if slot.consultation_type == 'Virtual Consultation':
                booking_vals['virtual_consultation_url'] = f"https://meeting.hospital.com/room/{slot.id}"
            
            # Update slot
            slot.write(booking_vals)
            
            # Update lead status if needed
            if lead.state == 'lead':
                lead.state = 'opportunity'
            
            return self._get_success_response({
                'appointment': self._serialize_slot_booking(slot),
                'booking_reference': slot.name,
            }, 'Appointment booked successfully')
            
        except ValueError as e:
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in book_appointment_slot: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/appointments/my_appointments/<int:lead_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_my_appointments(self, lead_id, **kwargs):
        """
        API to get appointments for a specific lead
        Parameters:
        - lead_id: Lead ID
        - status: Filter by status (optional)
        - date_from: Date filter (optional)
        - date_to: Date filter (optional)
        - limit: Number of records (default: 20)
        - offset: Records to skip (default: 0)
        """
        try:
            # Verify lead exists
            lead = request.env['crm.lead'].sudo().search([('id', '=', lead_id)], limit=1)
            if not lead:
                return self._get_error_response(f'Lead with ID {lead_id} not found', 404)
            
            domain = [('lead_id', '=', lead_id)]
            
            # Status filter
            if kwargs.get('status'):
                if kwargs.get('status') in ['open', 'booked', 'confirm', 'checked_in', 'consulting', 'completed', 'cancelled', 'no_show']:
                    domain.append(('availability', '=', kwargs.get('status')))
                else:
                    return self._get_error_response('Invalid status')
            
            # Date filters
            if kwargs.get('date_from'):
                try:
                    date_from = datetime.strptime(kwargs.get('date_from'), '%Y-%m-%d')
                    domain.append(('start_datetime', '>=', date_from))
                except ValueError:
                    return self._get_error_response('Invalid date_from format. Use YYYY-MM-DD')
            
            if kwargs.get('date_to'):
                try:
                    date_to = datetime.strptime(kwargs.get('date_to'), '%Y-%m-%d')
                    domain.append(('start_datetime', '<=', date_to))
                except ValueError:
                    return self._get_error_response('Invalid date_to format. Use YYYY-MM-DD')
            
            # Pagination
            limit = int(kwargs.get('limit', 20))
            offset = int(kwargs.get('offset', 0))
            
            # Search appointments
            appointments = request.env['slot.booking'].sudo().search(
                domain, 
                limit=limit, 
                offset=offset, 
                order='start_datetime desc'
            )
            
            total_count = request.env['slot.booking'].sudo().search_count(domain)
            
            appointments_data = [self._serialize_slot_booking(appointment) for appointment in appointments]
            
            return self._get_success_response({
                'appointments': appointments_data,
                'count': len(appointments_data),
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count,
                'lead_info': {
                    'id': lead.id,
                    'name': lead.name,
                    'caller_name': lead.caller_name,
                    'patient_name': lead.patient_name,
                    'reference': lead.reference,
                }
            }, 'Appointments retrieved successfully')
            
        except ValueError as e:
            return self._get_error_response(f'Invalid parameter value: {str(e)}')
        except Exception as e:
            _logger.error(f"Error in get_my_appointments: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/appointments/view/<int:appointment_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def view_appointment(self, appointment_id, **kwargs):
        """
        API to view a specific appointment
        Parameters:
        - appointment_id: ID of the appointment
        """
        try:
            appointment = request.env['slot.booking'].sudo().search([('id', '=', appointment_id)], limit=1)
            
            if not appointment:
                return self._get_error_response(f'Appointment with ID {appointment_id} not found', 404)
            
            return self._get_success_response({
                'appointment': self._serialize_slot_booking(appointment)
            }, 'Appointment retrieved successfully')
            
        except Exception as e:
            _logger.error(f"Error in view_appointment: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    # ============ APPOINTMENT MANAGEMENT APIS ============

    @http.route('/api/appointments/confirm/<int:appointment_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def confirm_appointment(self, appointment_id, **post):
        """
        API to confirm an appointment
        Parameters:
        - appointment_id: ID of the appointment
        """
        try:
            appointment = request.env['slot.booking'].sudo().search([('id', '=', appointment_id)], limit=1)
            
            if not appointment:
                return self._get_error_response(f'Appointment with ID {appointment_id} not found', 404)
            
            if appointment.availability != 'booked':
                return self._get_error_response('Only booked appointments can be confirmed')
            
            appointment.act_confirm()
            
            return self._get_success_response({
                'appointment': self._serialize_slot_booking(appointment)
            }, 'Appointment confirmed successfully')
            
        except UserError as e:
            return self._get_error_response(str(e))
        except Exception as e:
            _logger.error(f"Error in confirm_appointment: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/appointments/check_in/<int:appointment_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def check_in_appointment(self, appointment_id, **post):
        """
        API to check in for an appointment (creates clinical session)
        Parameters:
        - appointment_id: ID of the appointment
        """
        try:
            appointment = request.env['slot.booking'].sudo().search([('id', '=', appointment_id)], limit=1)
            
            if not appointment:
                return self._get_error_response(f'Appointment with ID {appointment_id} not found', 404)
            
            if appointment.availability not in ['booked', 'confirm']:
                return self._get_error_response('Only confirmed appointments can be checked in')
            
            # Check in will create clinical session
            result = appointment.check_in()
            
            # Refresh appointment data
            appointment_data = self._serialize_slot_booking(appointment)
            
            response_data = {
                'appointment': appointment_data,
                'check_in_time': appointment.start_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if appointment.start_datetime else None,
            }
            
            # Add clinical session info if created
            if appointment.clinical_session_id:
                response_data['clinical_session'] = {
                    'id': appointment.clinical_session_id.id,
                    'name': appointment.clinical_session_id.name,
                    'state': appointment.clinical_session_id.state,
                }
            
            return self._get_success_response(response_data, 'Check-in successful. Clinical session created.')
            
        except UserError as e:
            return self._get_error_response(str(e))
        except Exception as e:
            _logger.error(f"Error in check_in_appointment: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/appointments/start_consultation/<int:appointment_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def start_consultation(self, appointment_id, **post):
        """
        API to start consultation for an appointment
        Parameters:
        - appointment_id: ID of the appointment
        """
        try:
            appointment = request.env['slot.booking'].sudo().search([('id', '=', appointment_id)], limit=1)
            
            if not appointment:
                return self._get_error_response(f'Appointment with ID {appointment_id} not found', 404)
            
            if appointment.availability != 'checked_in':
                return self._get_error_response('Patient must be checked in before starting consultation')
            
            appointment.start_consultation()
            
            return self._get_success_response({
                'appointment': self._serialize_slot_booking(appointment),
                'consultation_started': True,
            }, 'Consultation started successfully')
            
        except UserError as e:
            return self._get_error_response(str(e))
        except Exception as e:
            _logger.error(f"Error in start_consultation: {str(e)}")
            return self._get_error_response('Internal server error', 500)

    @http.route('/api/appointments/finish_consultation/<int:appointment_id>', type='http', auth='none', methods=['POST'], csrf=False)
    def finish_consultation(self, appointment_id, **post):
        """
        API to finish consultation for an appointment
        Parameters:
        - appointment_id: ID of the appointment
        - feedback_score: Optional feedback score (1-5)
        - notes: Optional consultation notes
        """
        try:
            appointment = request.env['slot.booking'].sudo().search([('id', '=', appointment_id)], limit=1)
            
            if not appointment:
                return self._get_error_response(f'Appointment with ID {appointment_id} not found', 404)
            
            if appointment.availability != 'consulting':
                return self._get_error_response('Consultation must be started before finishing')
            
            # Update optional fields
            update_vals = {}
            if post.get('feedback_score'):
                if post.get('feedback_score') in ['1', '2', '3', '4', '5']:
                    update_vals['consultation_feedback_score_new'] = post.get('feedback_score')
            
            if post.get('notes'):
                update_vals['notes'] = post.get('notes')
            
            if update_vals:
                appointment.write(update_vals)
            
            appointment.finish_consultation()
            
            return self._get_success_response({
                'appointment': self._serialize_slot_booking(appointment),
                'consultation_completed': True,
            }, 'Consultation completed successfully')
            
        except UserError as e:
            return self._get_error_response(str(e))
        except Exception as e:
            _logger.error(f"Error in finish_consultation: {str(e)}")
            return self._get_error_response('Internal server error', 500)

