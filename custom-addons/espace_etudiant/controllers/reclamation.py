from odoo import http
from odoo.http import request
import json
import base64
import logging

_logger = logging.getLogger(__name__)

class ReclamationController(http.Controller):

    @http.route('/web/api/etudiant/reclamations', auth='user', type='http', methods=['GET'], website=True, cors='*')
    def list_reclamations(self, **kwargs):
        try:
            Etudiant = request.env['student.etudiant']
            etudiant = Etudiant.search([('user_id', '=', request.env.user.id)], limit=1)
            
            if not etudiant:
                headers = [('Content-Type', 'application/json'), ('Status', '404')]
                return request.make_response(json.dumps({'error': 'Student not found'}), headers)
            
            reclamations = request.env['student.reclamation'].search([('etudiant_id', '=', etudiant.id)])
            
            result = []
            for rec in reclamations:
                result.append({
                    'id': rec.id,
                    'titre': rec.titre,
                    'description': rec.description,
                    'etat': rec.etat,  # Fixed typo from 'etat' (was 'etat')
                    'date_creation': rec.date_creation,
                    'reponse_admin': rec.reponse_admin or '',
                    'date_traitement': rec.date_traitement or '',
                    'admin': rec.admin_id.name if rec.admin_id else ''
                })
            
            return request.make_response(
                json.dumps(result),
                [('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error("Error fetching reclamations: %s", str(e))
            headers = [('Content-Type', 'application/json'), ('Status', '500')]
            return request.make_response(json.dumps({'error': str(e)}), headers)

    @http.route('/web/api/etudiant/reclamations/create', 
               auth='user', 
               type='http', 
               methods=['POST'], 
               website=True, 
               csrf=False, 
               cors='*')
    def create_reclamation(self, **post):
        try:
            _logger.info("Received reclamation creation request with data: %s", post)
            
            Etudiant = request.env['student.etudiant']
            etudiant = Etudiant.search([('user_id', '=', request.env.user.id)], limit=1)
            
            if not etudiant:
                headers = [('Content-Type', 'application/json'), ('Status', '404')]
                return request.make_response(json.dumps({'error': 'Student not found'}), headers)
            
            # Handle file upload
            piece_jointe = None
            nom_fichier = None
            if 'piece_jointe' in request.httprequest.files:
                file = request.httprequest.files['piece_jointe']
                piece_jointe = base64.b64encode(file.read())
                nom_fichier = file.filename
            
            reclamation = request.env['student.reclamation'].create({
                'etudiant_id': etudiant.id,
                'titre': post.get('titre'),
                'description': post.get('description'),
                'piece_jointe': piece_jointe,
                'nom_fichier': nom_fichier,
                'etat': 'nouvelle'
            })
            
            _logger.info("Created reclamation with ID: %s", reclamation.id)
            
            return request.make_response(
                json.dumps({
                    'success': True, 
                    'reclamation_id': reclamation.id,
                    'message': 'Reclamation created successfully'
                }),
                [('Content-Type', 'application/json')]
            )
        except Exception as e:
            _logger.error("Error creating reclamation: %s", str(e))
            headers = [('Content-Type', 'application/json'), ('Status', '500')]
            return request.make_response(json.dumps({'error': str(e)}), headers)