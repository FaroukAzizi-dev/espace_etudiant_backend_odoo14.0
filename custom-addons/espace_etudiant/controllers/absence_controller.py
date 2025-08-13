from odoo import http
from odoo.http import request
import json
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class AbsenceController(http.Controller):
    
    @http.route('/api/absences/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_absence(self, **params):
        try:
            _logger.info("Données d'absence reçues: %s", params)
            
            # Validation des champs requis
            required_fields = ['etudiant_id', 'heure_debut', 'heure_fin']
            for field in required_fields:
                if not params.get(field):
                    _logger.error("Champ manquant: %s", field)
                    return {"error": f"Champ obligatoire manquant: {field}"}
            
            etudiant_id = params.get('etudiant_id')
            
            # Validation de l'ID étudiant
            try:
                etudiant_id = int(etudiant_id)
                if etudiant_id <= 0:
                    return {"error": f"ID étudiant invalide: {etudiant_id}"}
            except (ValueError, TypeError):
                return {"error": f"ID étudiant doit être un nombre: {etudiant_id}"}
            
            # Vérification de l'existence de l'étudiant
            etudiant = request.env['student.etudiant'].sudo().browse(etudiant_id)
            if not etudiant.exists():
                return {"error": f"Étudiant avec ID {etudiant_id} non trouvé"}
            
            # Gestion de l'enseignant
            current_user = request.env.user
            _logger.info("Utilisateur connecté: ID=%s, Name=%s", current_user.id, current_user.name)
            
            # Recherche de l'enseignant correspondant à l'utilisateur connecté
            enseignant = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', current_user.id)
            ], limit=1)
            
            if not enseignant:
                # Créer automatiquement l'enregistrement enseignant s'il n'existe pas
                _logger.info("Création d'un enregistrement enseignant pour l'utilisateur %s", current_user.id)
                enseignant = request.env['student.enseignant'].sudo().create({
                    'name': current_user.name,
                    'user_id': current_user.id,
                    # Ajoutez d'autres champs requis selon votre modèle
                })
                _logger.info("Enseignant créé avec ID: %s", enseignant.id)
            
            # Formatage des dates
            try:
                heure_debut = params.get('heure_debut')
                heure_fin = params.get('heure_fin')
                
                _logger.info("Formats de dates reçus - Début: %s, Fin: %s", heure_debut, heure_fin)
                
                # Conversion du format datetime vers datetime object
                if isinstance(heure_debut, str):
                    heure_debut = self._parse_datetime(heure_debut)
                if isinstance(heure_fin, str):
                    heure_fin = self._parse_datetime(heure_fin)
                    
            except ValueError as e:
                _logger.error("Erreur format date: %s", str(e))
                return {"error": f"Format de date invalide: {str(e)}"}
            
            # Préparation des données pour la création
            absence_vals = {
                'etudiant_id': etudiant_id,
                'enseignant_id': enseignant.id,  # Utilisation de l'ID de l'enseignant, pas de l'utilisateur
                'heure_debut': heure_debut,
                'heure_fin': heure_fin,
                'justifiee': params.get('justifiee', 'non_justifiee'),
                'motif': params.get('motif', '')
            }
            
            _logger.info("Création absence avec valeurs: %s", absence_vals)
            
            # Création de l'absence
            absence = request.env['student.absence'].sudo().create(absence_vals)
            
            # Commit explicite de la transaction
            request.env.cr.commit()
            
            _logger.info("Absence créée avec succès - ID: %s", absence.id)
            
            return {
                "status": "success",
                "absence_id": absence.id,
                "message": "Absence enregistrée avec succès",
                "enseignant_id": enseignant.id,
                "enseignant_name": enseignant.name
            }
            
        except Exception as e:
            _logger.error("Erreur dans create_absence: %s", str(e), exc_info=True)
            # Rollback en cas d'erreur
            request.env.cr.rollback()
            return {"error": f"Erreur serveur: {str(e)}"}

    @http.route('/api/absences/student', type='json', auth='user', methods=['POST'], csrf=False)
    def get_student_absences(self, **params):
        try:
            student_id = params.get('student_id')
            if not student_id:
                return {"error": "ID étudiant requis"}
            
            absences = request.env['student.absence'].sudo().search([
                ('etudiant_id', '=', int(student_id))
            ], order="heure_debut desc")
            
            result = []
            for absence in absences:
                result.append({
                    'id': absence.id,
                    'date': absence.heure_debut.strftime('%Y-%m-%d') if absence.heure_debut else '',
                    'heure_debut': absence.heure_debut.strftime('%H:%M') if absence.heure_debut else '',
                    'heure_fin': absence.heure_fin.strftime('%H:%M') if absence.heure_fin else '',
                    'justifiee': absence.justifiee,
                    'motif': absence.motif or '',
                    'enseignant': absence.enseignant_id.name if absence.enseignant_id else ''
                })
            
            return result
            
        except Exception as e:
            _logger.error("Erreur dans get_student_absences: %s", str(e))
            return {"error": str(e)}
    
    def _parse_datetime(self, date_string):
        """Parse datetime string in multiple formats"""
        formats_to_try = [
            '%Y-%m-%dT%H:%M',           # 2025-02-11T11:00
            '%Y-%m-%d %H:%M:%S',        # 2025-02-11 10:00:00
            '%Y-%m-%d %H:%M',           # 2025-02-11 10:00
            '%Y-%m-%dT%H:%M:%S',        # 2025-02-11T11:00:00
        ]
        
        for fmt in formats_to_try:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Impossible de parser la date: {date_string}")
    
    @http.route('/api/enseignant/check', type='json', auth='user', methods=['POST'], csrf=False)
    def check_enseignant(self, **params):
        """Route pour vérifier/créer l'enregistrement enseignant"""
        try:
            current_user = request.env.user
            
            enseignant = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', current_user.id)
            ], limit=1)
            
            if not enseignant:
                return {
                    "status": "not_found",
                    "message": f"Aucun enregistrement enseignant trouvé pour l'utilisateur {current_user.name}",
                    "user_id": current_user.id,
                    "user_name": current_user.name
                }
            
            return {
                "status": "found",
                "enseignant_id": enseignant.id,
                "enseignant_name": enseignant.name,
                "user_id": current_user.id
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    
    @http.route('/api/enseignant/etudiants', type='json', auth='user', methods=['POST'], csrf=False)
    def get_etudiants_by_enseignant(self, **params):
        try:
            current_user = request.env.user
            
            # Trouver l'enseignant connecté
            enseignant = request.env['student.enseignant'].sudo().search([
                ('user_id', '=', current_user.id)
            ], limit=1)
            
            if not enseignant:
                return {"error": "Enseignant non trouvé pour cet utilisateur"}
            
            # Récupérer les classes de l'enseignant
            classes = request.env['student.classe'].sudo().search([
                ('enseignant_ids', 'in', [enseignant.id])
            ])
            
            if not classes:
                return {"error": "Aucune classe assignée à cet enseignant"}
            
            # Récupérer les étudiants de ces classes
            etudiants = request.env['student.etudiant'].sudo().search([
                ('classe_id', 'in', classes.ids)
            ])
            
            result = []
            for etudiant in etudiants:
                result.append({
                    'id': etudiant.id,
                    'name': etudiant.first_name,
                    'classe': etudiant.classe_id.name if etudiant.classe_id else '',
                })
            
            return {
                "status": "success",
                "etudiants": result,
                "enseignant_id": enseignant.id,
                "enseignant_name": enseignant.name
            }
        
        except Exception as e:
            _logger.error("Erreur dans get_etudiants_by_enseignant: %s", str(e), exc_info=True)
            return {"error": str(e)}
    

    
    @http.route('/api/absences/bulk_create', type='json', auth='user', methods=['POST'], csrf=False)
    def bulk_create_absences(self, **params):
        try:
            _logger.info("Absences reçues: %s", params)

            absences_list = params.get('absences', [])
            if not absences_list:
                return {"error": "Aucune absence à enregistrer"}

            current_user = request.env.user
            enseignant = request.env['student.enseignant'].sudo().search([('user_id', '=', current_user.id)], limit=1)
            if not enseignant:
                enseignant = request.env['student.enseignant'].sudo().create({
                    'name': current_user.name,
                    'user_id': current_user.id
                })

            created_ids = []
            for absence in absences_list:
                etudiant_id = absence.get('etudiant_id')
                heure_debut = self._parse_datetime(absence.get('heure_debut'))
                heure_fin = self._parse_datetime(absence.get('heure_fin'))
                justifiee = absence.get('justifiee', 'non_justifiee')
                motif = absence.get('motif', '')

                absence_rec = request.env['student.absence'].sudo().create({
                    'etudiant_id': etudiant_id,
                    'enseignant_id': enseignant.id,
                    'heure_debut': heure_debut,
                    'heure_fin': heure_fin,
                    'justifiee': justifiee,
                    'motif': motif
                })
                created_ids.append(absence_rec.id)

            request.env.cr.commit()
            return {"status": "success", "created_ids": created_ids}

        except Exception as e:
            request.env.cr.rollback()
            _logger.error("Erreur bulk_create_absences: %s", str(e), exc_info=True)
            return {"error": str(e)}
    
    @http.route('/api/enseignant/classes', type='http', auth='user', methods=['GET'], csrf=False)
    def get_teacher_classes(self, **kwargs):
            """
            Retourne la liste des classes (id, name).
            — Version simple: toutes les classes.
            — Pour filtrer par enseignant: adaptez le domain si votre modèle le permet.
            """
            try:
                Classe = request.env['student.classe'].sudo()

                # 🔁 Version simple: toutes les classes
                classes = Classe.search([])

                # 🛠 Si vous avez un lien vers l'enseignant, vous pouvez filtrer:
                # current_user = request.env.user
                # enseignant = request.env['student.enseignant'].sudo().search([('user_id','=', current_user.id)], limit=1)
                # if 'enseignant_id' in Classe._fields:
                #     classes = Classe.search([('enseignant_id', '=', enseignant.id)])
                # elif 'enseignant_ids' in Classe._fields:
                #     classes = Classe.search([('enseignant_ids', 'in', [enseignant.id])])

                data = [{'id': c.id, 'name': c.name} for c in classes]
                return request.make_response(
                    json.dumps(data),
                    headers=[('Content-Type', 'application/json')]
                )
            except Exception as e:
                _logger.error("Erreur get_teacher_classes: %s", str(e), exc_info=True)
                return request.make_response(
                    json.dumps({'error': str(e)}),
                    headers=[('Content-Type', 'application/json')],
                    status=500
                )

    @http.route('/api/classes/<int:classe_id>/students', 
                type='http', auth='user', methods=['GET'], csrf=False)
    def get_students_by_class(self, classe_id, **kwargs):
        students = request.env['student.etudiant'].sudo().search([
            ('classe_id', '=', classe_id),
        ])

        data = [{'id': s.id, 'name': s.partner_id.name} for s in students]

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )
