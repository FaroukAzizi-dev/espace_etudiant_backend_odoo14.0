from odoo import http
from odoo.http import request, Response
import logging

_logger = logging.getLogger(__name__)

class StudentAuthController(http.Controller):

    @http.route('/api/student/authenticate', type='json', auth='public', methods=['POST'], csrf=False, cors="*")
    def authenticate(self):
        """
        Student authentication - validates student exists then uses Odoo's built-in auth
        """
        try:
            params = request.jsonrequest.get('params', {})
        except Exception as e:
            _logger.error(f"Error parsing request data: {e}")
            return {"error": "Failed to parse request data."}

        # Extract parameters
        # Set the database name directly in the backend
        db = 'db_pacu-6csq-3ta6' 
        email = params.get('login')
        cin = params.get('password')

        if not email or not cin:
            return {"error": "Email and CIN are required."}

        try:
            # Validate that this is actually a student
            student = request.env['student.etudiant'].sudo().search([
                ('email_personnel', '=', email),
                ('cin', '=', cin)
            ], limit=1)

            if not student:
                _logger.warning(f"Student not found for email: {email}")
                return {"error": "Invalid student credentials."}

            if not student.user_id:
                _logger.warning(f"Student {email} doesn't have a user account")
                return {"error": "No user account found for this student."}

            # Use Odoo's built-in authentication - it handles everything
            uid = request.session.authenticate(db, student.user_id.login, cin)
            
            if not uid:
                return {"error": "Authentication failed."}

            # Get the standard session info that Odoo provides
            session_info = request.env['ir.http'].session_info()
            
            # Just return what Odoo gives us
            return session_info
            
        except Exception as e:
            _logger.error(f"Authentication error: {e}")
            return {"error": "Authentication failed."}

    @http.route('/api/student/logout', type='json', auth='user', methods=['POST'], csrf=False, cors="*")
    def logout(self):
        """Logout using Odoo's built-in method"""
        try:
            request.session.logout(keep_db=False)
            return {"message": "Logged out successfully"}
        except Exception as e:
            _logger.error(f"Logout error: {e}")
            return {"error": "Logout failed"}

    # OPTIONS route for CORS preflight
    @http.route([
        '/api/student/authenticate', 
        '/api/student/login',
        '/api/student/session/info', 
        '/api/student/logout'
    ], type='http', auth='public', methods=['OPTIONS'], csrf=False)
    def _options_preflight(self, **kw):
        headers = [
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'POST, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
            ('Access-Control-Max-Age', '86400'),
        ]
        return Response(headers=headers)