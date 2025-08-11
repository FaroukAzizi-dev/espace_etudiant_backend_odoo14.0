
from odoo import http
from odoo.http import request
import json
import base64
import logging

_logger = logging.getLogger(__name__)

class ReclamationController(http.Controller):

    def _get_current_student(self):
        """Helper method to get current student"""
        if not request.env.user or request.env.user._is_public():
            return None
        
        Etudiant = request.env['student.etudiant']
        return Etudiant.search([('user_id', '=', request.env.user.id)], limit=1)

    def _error_response(self, data, status_code=500):
        """Helper method for error responses"""
        headers = [('Content-Type', 'application/json'), ('Status', str(status_code))]
        return request.make_response(json.dumps(data), headers)

    def _success_response(self, data):
        """Helper method for success responses"""
        return request.make_response(
            json.dumps(data, default=str),
            [('Content-Type', 'application/json')]
        )

    @http.route('/api/etudiant/reclamations', auth='user', type='http', methods=['GET'], website=True, cors='*')
    def list_reclamations(self, **kwargs):
        try:
            etudiant = self._get_current_student()
            if not etudiant:
                return self._error_response({'error': 'Student not found'}, 404)
            
            # Use sudo() only for accessing related admin user info
            reclamations = request.env['student.reclamation'].search([
                ('etudiant_id', '=', etudiant.id)
            ], order='date_creation desc')
            
            result = []
            for rec in reclamations:
                admin_name = rec.admin_id.sudo().name if rec.admin_id else ''
                result.append({
                    'id': rec.id,
                    'titre': rec.titre,
                    'description': rec.description,
                    'etat': rec.etat,
                    'date_creation': rec.date_creation.isoformat() if rec.date_creation else '',
                    'reponse_admin': rec.reponse_admin or '',
                    'date_traitement': rec.date_traitement.isoformat() if rec.date_traitement else '',
                    'admin': admin_name,  # Only expose the name, not full user record
                    'nom_fichier': rec.nom_fichier or ''
                })
            
            return self._success_response(result)
            
        except Exception as e:
            _logger.error("Error fetching reclamations: %s", str(e))
            return self._error_response({'error': str(e)}, 500)

    @http.route('/api/etudiant/reclamations/create', 
               auth='user', 
               type='http', 
               methods=['POST'], 
               website=True, 
               csrf=False,
               cors='*')
    def create_reclamation(self, **kwargs):
        try:
            # Récupération sécurisée des champs depuis le formulaire
            titre = request.httprequest.form.get('titre')
            description = request.httprequest.form.get('description')

            if not titre or not description:
                return self._error_response({
                    'error': 'Le titre et la description sont requis'
                }, 400)

            etudiant = self._get_current_student()
            if not etudiant:
                return self._error_response({'error': 'Étudiant non trouvé'}, 404)

            # Gestion du fichier
            piece_jointe = None
            nom_fichier = None
            if 'piece_jointe' in request.httprequest.files:
                file = request.httprequest.files['piece_jointe']
                if file.filename:
                    piece_jointe = base64.b64encode(file.read())
                    nom_fichier = file.filename

            # Création de la réclamation
            reclamation = request.env['student.reclamation'].create({
                'etudiant_id': etudiant.id,
                'titre': titre,
                'description': description,
                'piece_jointe': piece_jointe,
                'nom_fichier': nom_fichier,
                'etat': 'nouvelle'
            })

            _logger.info("Réclamation créée avec ID: %s par l'étudiant: %s",
                         reclamation.id, etudiant.name)

            return self._success_response({
                'success': True,
                'reclamation_id': reclamation.id,
                'message': 'Réclamation créée avec succès'
            })

        except Exception as e:
            _logger.error("Erreur lors de la création de la réclamation: %s", str(e))
            return self._error_response({'error': 'Erreur lors de la création'}, 500)



