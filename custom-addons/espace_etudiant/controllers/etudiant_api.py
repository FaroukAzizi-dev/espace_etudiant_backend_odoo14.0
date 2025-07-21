from odoo import http
from odoo.http import request, Response
from datetime import datetime, timedelta, timezone
import jwt
import os
import logging
import json

_logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("STUDENT_PORTAL_JWT_SECRET")

class StudentAuthController(http.Controller):

    # SOLUTION 1: Change to type='json' to handle JSON-RPC requests
    @http.route('/api/student/login', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def login(self):
        try:
            # For type='json', use request.jsonrequest to get the data
            data = request.jsonrequest
        except Exception as e:
            _logger.error(f"Error parsing request data: {e}")
            return {"error": "Failed to parse request data."}

        email = data.get('email')
        cin = data.get('cin')

        if not email or not cin:
            _logger.warning("Login attempt with missing email or CIN.")
            return {"error": "Email and CIN are required."}

        try:
            student = request.env['student.etudiant'].sudo().search([
                ('email_personnel', '=', email),
                ('cin', '=', cin)
            ], limit=1)
        except Exception as e:
            _logger.error(f"Database query error during login: {e}")
            return {"error": "An internal error occurred."}

        if not student:
            _logger.warning(f"Failed login attempt for email: {email}")
            return {"error": "Invalid credentials."}

        if not SECRET_KEY:
            _logger.error("JWT Secret Key is not set in environment variables.")
            return {"error": "Server configuration error."}

        try:
            payload = {
                "uid": student.user_id.id if student.user_id else None,
                "student_id": student.id,
                "exp": datetime.now(timezone.utc) + timedelta(hours=6)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        except Exception as e:
            _logger.error(f"Error encoding JWT token: {e}")
            return {"error": "Failed to generate authentication token."}

        response_data = {
            "token": token,
            "student": {
                "id": student.id,
                "name": student.partner_id.name if student.partner_id else "N/A",
                "email": student.email_personnel,
                "identifiant": student.identifiant
            }
        }
        
        # For type='json', return a Python dict/list, Odoo handles JSON conversion
        return response_data


    # OPTIONS route for CORS preflight (keep as type='http')
    @http.route('/api/student/login', type='http', auth='public', methods=['OPTIONS'], csrf=False)
    def _options_login_preflight(self, **kw):
        headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ('Access-Control-Max-Age', '86400'),
        ]
        return Response(headers=headers)