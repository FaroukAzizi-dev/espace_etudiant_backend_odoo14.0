from odoo import http, fields
from odoo.http import request
import json
from datetime import datetime, timedelta

class TeacherSubjectController(http.Controller):

    @http.route('/api/teacher/subjects', type='json', auth='user', methods=['POST'], csrf=False)
    def get_teacher_subjects(self, **kw):
        try:
            teacher = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not teacher:
                return {"error": "Teacher not found"}

            subjects = request.env['student.matiere'].sudo().search([
                ('enseignant_ids', 'in', [teacher.id])
            ])

            result = []
            for subject in subjects:
                classe_info = None
                if subject.classe_id:
                    classe_info = {
                        'id': subject.classe_id.id,
                        'name': subject.classe_id.name,
                        'filiere': subject.classe_id.filiere_id.name if subject.classe_id.filiere_id else None,
                        'niveau': subject.classe_id.niveau_id.name if subject.classe_id.niveau_id else None,
                    }

                result.append({
                    'id': subject.id,
                    'name': subject.name,
                    'code': subject.code,
                    'description': subject.description,
                    'semestre': subject.semestre,
                    'volume_horaire': subject.volume_horaire,
                    'coefficient': subject.coefficient,
                    'classe': subject.classe_id.name if subject.classe_id else None,
                    'classe_info': classe_info
                })

            return result

        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/subjects/<int:subject_id>', type='json', auth='user', methods=['GET'], csrf=False)
    def get_subject_details(self, subject_id, **kw):
        try:
            subject = request.env['student.matiere'].sudo().browse(subject_id)
            if not subject.exists():
                return {"error": "Subject not found"}

            evaluation_types = []
            for eval_type in subject.evaluation_type_ids:
                evaluation_types.append({
                    'type': eval_type.type,
                    'pourcentage': eval_type.pourcentage
                })

            classe_info = None
            if subject.classe_id:
                classe_info = {
                    'id': subject.classe_id.id,
                    'name': subject.classe_id.name,
                    'filiere': subject.classe_id.filiere_id.name if subject.classe_id.filiere_id else None,
                    'niveau': subject.classe_id.niveau_id.name if subject.classe_id.niveau_id else None,
                }

            return {
                'id': subject.id,
                'name': subject.name,
                'code': subject.code,
                'description': subject.description,
                'semestre': subject.semestre,
                'volume_horaire': subject.volume_horaire,
                'coefficient': subject.coefficient,
                'classe': subject.classe_id.name if subject.classe_id else None,
                'classe_info': classe_info,
                'evaluation_types': evaluation_types,
                'enseignants': [{
                    'name': teacher.name,
                    'email': teacher.email
                } for teacher in subject.enseignant_ids]
            }

        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/subjects/<int:subject_id>/schedule', type='json', auth='user', methods=['GET'], csrf=False)
    def get_subject_schedule(self, subject_id, **kw):
        try:
            schedule = [
                {
                    'day': 'Lundi',
                    'start_time': '08:00',
                    'end_time': '10:00',
                    'classroom': 'Salle A12'
                },
                {
                    'day': 'Jeudi',
                    'start_time': '14:00',
                    'end_time': '16:00',
                    'classroom': 'Salle B07'
                }
            ]
            return schedule

        except Exception as e:
            return {"error": str(e)}
    
    @http.route('/api/teacher/classes', type='json', auth='user', methods=['POST'], csrf=False)
    def get_teacher_classes(self, **kw):
        try:
            teacher = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not teacher:
                return {"error": "Teacher not found"}

            subjects = request.env['student.matiere'].sudo().search([
                ('enseignant_ids', 'in', [teacher.id])
            ])

            classes_dict = {}
            for subject in subjects:
                if subject.classe_id:
                    classe_key = subject.classe_id.id
                    if classe_key not in classes_dict:
                        classes_dict[classe_key] = {
                            'id': subject.classe_id.id,
                            'name': subject.classe_id.name,
                            'filiere': subject.classe_id.filiere_id.name if subject.classe_id.filiere_id else None,
                            'niveau': subject.classe_id.niveau_id.name if subject.classe_id.niveau_id else None,
                            'subjects': []
                        }
                    
                    classes_dict[classe_key]['subjects'].append({
                        'id': subject.id,
                        'name': subject.name,
                        'code': subject.code,
                        'coefficient': subject.coefficient,
                        'volume_horaire': subject.volume_horaire
                    })

            return list(classes_dict.values())

        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/teacher/schedule', type='json', auth='user', methods=['GET'], csrf=False)
    def get_teacher_schedule(self, **kw):
        try:
            teacher = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not teacher:
                return {"error": "Teacher not found"}

            # Récupérer les sessions des 2 prochaines semaines
            today = fields.Date.today()
            end_date = today + timedelta(days=14)
            
            sessions = request.env['student.session'].sudo().search([
                ('enseignant_id', '=', teacher.id),
                ('start_datetime', '>=', today.strftime('%Y-%m-%d 00:00:00')),
                ('start_datetime', '<=', end_date.strftime('%Y-%m-%d 23:59:59')),
                ('state', '=', 'confirm')
            ], order='start_datetime')

            result = []
            for session in sessions:
                result.append({
                    'id': session.id,
                    'title': session.matiere_id.name,
                    'start_datetime': session.start_datetime,
                    'end_datetime': session.end_datetime,
                    'matiere': session.matiere_id.name,
                    'classe': session.classe_id.name,
                    'salle': session.classroom or 'Non spécifiée',
                    'enseignant': session.enseignant_id.name
                })

            return result
            
        except Exception as e:
            return {"error": str(e)}