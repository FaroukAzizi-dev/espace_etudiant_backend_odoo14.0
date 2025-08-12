from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime

class StudentAbsenceAPI(http.Controller):
    
    @http.route('/api/student/absences/list', 
            type='http', 
            auth='user', 
            methods=['GET'], 
            csrf=False,
            cors='*')
    def get_absences(self, **kwargs):
        try:
            # Vérifier si l'utilisateur est un étudiant
            student = request.env['student.etudiant'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
            
            if not student:
                return Response(
                    json.dumps({'error': 'Accès non autorisé - Utilisateur non étudiant'}),
                    content_type='application/json',
                    status=403
                )
            
            domain = [('etudiant_id', '=', student.id)]
            
            # Filtre pour les absences à venir
            if kwargs.get('upcoming'):
                domain.append(('heure_debut', '>=', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Filtre pour les absences passées
            if kwargs.get('past'):
                domain.append(('heure_debut', '<', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Filtre par statut de justification
            if kwargs.get('justifiee'):
                domain.append(('justifiee', '=', kwargs.get('justifiee')))
            
            absences = request.env['student.absence'].sudo().search(domain, order='heure_debut DESC')
            
            result = []
            for absence in absences:
                absence_data = {
                    'id': absence.id,
                    'etudiant': absence.etudiant_id.name,
                    'enseignant': absence.enseignant_id.name if absence.enseignant_id else None,
                    'heure_debut': absence.heure_debut.strftime('%Y-%m-%d %H:%M:%S') if absence.heure_debut else None,
                    'heure_fin': absence.heure_fin.strftime('%Y-%m-%d %H:%M:%S') if absence.heure_fin else None,
                    'statut': absence.justifiee,
                    'motif': absence.motif
                }
                result.append(absence_data)
            
            return Response(
                json.dumps({'absences': result}),
                content_type='application/json',
                status=200
            )
            
        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                status=500
            )