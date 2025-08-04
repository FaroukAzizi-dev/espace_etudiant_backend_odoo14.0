# controllers/student_api.py
from odoo import http
from odoo.http import request
import json
from datetime import datetime

class StudentAPI(http.Controller):
    
    @http.route('/api/student/academic_info', type='json', auth='user', methods=['POST'])
    def get_academic_info(self):
        try:
            student = request.env['student.etudiant'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not student:
                return {'error': 'Étudiant non trouvé'}
            
            if not student.programme_id or not student.niveau_id or not student.filiere_id:
                return {'error': 'Informations académiques incomplètes'}
            
            return {
                'programme': student.programme_id.name,
                'niveau': student.niveau_id.name,
                'filiere': student.filiere_id.name,
                'date': datetime.now().strftime('%d/%m/%Y')
            }
            
        except Exception as e:
            return {'error': f'Erreur serveur: {str(e)}'}