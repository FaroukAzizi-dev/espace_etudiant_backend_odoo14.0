from odoo import http
from odoo.http import request, Response
import json

class ScheduleController(http.Controller):
    
    @http.route('/api/student-schedule', type='http', auth='user', methods=['GET'], csrf=False)  # ← GET uniquement
    def get_student_schedule(self, **params):
        try:
            student = request.env['student.etudiant'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not student:
                return Response(json.dumps({"error": "Student not found", "sessions": []}),
                              content_type='application/json')
            
            if not student.classe_id:
                return Response(json.dumps({"error": "Student has no assigned class", "sessions": []}),
                              content_type='application/json')
            
            sessions = request.env['student.session'].sudo().search([
                ('classe_id', '=', student.classe_id.id),
                ('state', 'in', ['confirm', 'done'])
            ], order="start_datetime asc")
            
            result = []
            for session in sessions:
                session_data = {
                    'id': session.id,
                    'name': session.name,
                    'matiere_id': [session.matiere_id.id, session.matiere_id.name],
                    'enseignant_id': [session.enseignant_id.id, session.enseignant_id.name],
                    'classe_id': [session.classe_id.id, session.classe_id.name],
                    'salle_name': session.salle_id.name if session.salle_id else None,
                    'start_datetime': session.start_datetime.isoformat(),
                    'end_datetime': session.end_datetime.isoformat(),
                    'timing_id': [session.timing_id.id, session.timing_id.name],
                    'state': session.state
                }
                result.append(session_data)
            
            return Response(json.dumps({"sessions": result, "error": False}),
                           content_type='application/json')
            
        except Exception as e:
            return Response(json.dumps({"error": str(e), "sessions": []}),
                         content_type='application/json')
        
        
        