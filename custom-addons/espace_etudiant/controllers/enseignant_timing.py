from odoo import http, fields
from odoo.http import request
from datetime import datetime

class ScheduleController(http.Controller):
    
    @http.route('/api/sessions', type='json', auth='user', methods=['POST'], csrf=False)
    def get_teacher_sessions(self, **params):
        try:
            enseignant = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not enseignant:
                return {"error": "Enseignant non trouvé"}
            
            # Récupérer toutes les sessions sans filtre de date
            sessions = request.env['student.session'].sudo().search([
                ('enseignant_id', '=', enseignant.id),
                ('state', 'in', ['confirm', 'done'])
            ], order="start_datetime asc")
            
            result = []
            for session in sessions:
                session_data = {
                    'id': session.id,
                    'name': session.name,
                    'matiere_id': (session.matiere_id.id, session.matiere_id.name),
                    'enseignant_id': (session.enseignant_id.id, session.enseignant_id.name),
                    'classe_id': (session.classe_id.id, session.classe_id.name),
                    'start_datetime': session.start_datetime.isoformat(),
                    'end_datetime': session.end_datetime.isoformat(),
                    'timing_id': (session.timing_id.id, session.timing_id.name),
                    'state': session.state
                }
                result.append(session_data)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}