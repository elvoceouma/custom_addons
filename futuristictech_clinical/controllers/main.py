# -*- coding: utf-8 -*-
from odoo import http, models
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