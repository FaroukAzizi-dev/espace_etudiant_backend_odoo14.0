# controllers/student_api.py
from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime

class StudentAPI(http.Controller):
    
    @http.route('/api/student/academic_info', 
            type='http', 
            auth='user', 
            methods=['GET'], 
            csrf=False,
            cors='*',
            website=True)
    def get_academic_info(self, **kwargs):
        try:
            student = request.env['student.etudiant'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not student:
                return Response(
                    json.dumps({'error': 'Étudiant non trouvé'}),
                    content_type='application/json',
                    status=404
                )
            
            # Safely get related records
            result = {
                'programme': student.programme_id.name if student.programme_id else None,
                'niveau': student.niveau_id.name if student.niveau_id else None,
                'filiere': student.filiere_id.name if student.filiere_id else None,
                'date': datetime.now().strftime('%d/%m/%Y')
            }
            
            return Response(
                json.dumps(result),
                content_type='application/json',
                status=200
            )
            
        except Exception as e:
            return Response(
                json.dumps({'error': f'Erreur serveur: {str(e)}'}),
                content_type='application/json',
                status=500
            )