from odoo import http
from odoo.http import request
import json

class NoteController(http.Controller):
    
    @http.route('/api/notes/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_note(self, **params):
        try:
            print("Données reçues:", params)
            
            required_fields = ['etudiant_id', 'matiere_id']
            for field in required_fields:
                if not params.get(field):
                    print(f"Champ manquant: {field}")
                    return {"error": f"Champ obligatoire manquant: {field}"}
            
            etudiant_id = params.get('etudiant_id')
            matiere_id = params.get('matiere_id')
            
            if not isinstance(etudiant_id, int) or etudiant_id <= 0:
                return {"error": f"ID étudiant invalide: {etudiant_id}"}
            
            if not isinstance(matiere_id, int) or matiere_id <= 0:
                return {"error": f"ID matière invalide: {matiere_id}"}
            
            etudiant = request.env['student.etudiant'].sudo().browse(etudiant_id)
            if not etudiant.exists():
                return {"error": f"Étudiant avec ID {etudiant_id} non trouvé"}
            
            matiere = request.env['student.matiere'].sudo().browse(matiere_id)
            if not matiere.exists():
                return {"error": f"Matière avec ID {matiere_id} non trouvée"}
            
            note_vals = {
                'etudiant_id': etudiant_id,
                'matiere_id': matiere_id,
                'etudiant_identifiant': etudiant.identifiant,
                'matiere_code': matiere.code,
                'note_cc': float(params.get('note_cc', 0)),
                'note_tp': float(params.get('note_tp', 0)),
                'note_examen': float(params.get('note_examen', 0)),
            }
            
            note = request.env['student.note'].sudo().create(note_vals)
            
            return {
                "status": "success",
                "note_id": note.id,
                "message": "Note créée avec succès"
            }
            
        except Exception as e:
            print("Erreur dans create_note:", str(e))
            return {"error": str(e)}

    @http.route('/api/students/search', type='json', auth='user', methods=['POST'], csrf=False)
    def search_students(self, **params):
        try:
            query = params.get('query', '')
            if len(query) < 2:
                return []
            
            domain = [
                '|',
                ('identifiant', 'ilike', query),
                ('name', 'ilike', query)
            ]
            
            students = request.env['student.etudiant'].sudo().search(domain, limit=10)
            
            result = []
            for student in students:
                result.append({
                    'id': student.id,
                    'identifiant': student.identifiant,
                    'name': student.name,
                })
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/subjects/search', type='json', auth='user', methods=['POST'], csrf=False)
    def search_subjects(self, **params):
        try:
            query = params.get('query', '')
            if len(query) < 2:
                return []
            
            domain = [
                '|',
                ('code', 'ilike', query),
                ('name', 'ilike', query)
            ]
            
            subjects = request.env['student.matiere'].sudo().search(domain, limit=10)
            
            result = []
            for subject in subjects:
                evaluation_types = []
                for eval_type in subject.evaluation_type_ids:
                    evaluation_types.append({
                        'id': eval_type.id,
                        'type': eval_type.type,
                        'pourcentage': eval_type.pourcentage
                    })
                
                result.append({
                    'id': subject.id,
                    'code': subject.code,
                    'name': subject.name,
                    'evaluation_type_ids': evaluation_types
                })
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/students/get', type='json', auth='user', methods=['POST'], csrf=False)
    def get_student(self, **params):
        try:
            identifiant = params.get('identifiant')
            if not identifiant:
                return {"error": "Identifiant requis"}
            
            student = request.env['student.etudiant'].sudo().search([
                ('identifiant', '=', identifiant)
            ], limit=1)
            
            if not student:
                return {"error": "Étudiant non trouvé"}
            
            return {
                'id': student.id,
                'identifiant': student.identifiant,
                'name': student.name,
            }
            
        except Exception as e:
            return {"error": str(e)}

    @http.route('/api/subjects/get', type='json', auth='user', methods=['POST'], csrf=False)
    def get_subject(self, **params):
        try:
            code = params.get('code')
            if not code:
                return {"error": "Code matière requis"}
            
            subject = request.env['student.matiere'].sudo().search([
                ('code', '=', code)
            ], limit=1)
            
            if not subject:
                return {"error": "Matière non trouvée"}
            
            evaluation_types = []
            for eval_type in subject.evaluation_type_ids:
                evaluation_types.append({
                    'id': eval_type.id,
                    'type': eval_type.type,
                    'pourcentage': eval_type.pourcentage
                })
            
            return {
                'id': subject.id,
                'code': subject.code,
                'name': subject.name,
                'evaluation_type_ids': evaluation_types
            }
            
        except Exception as e:
            return {"error": str(e)}