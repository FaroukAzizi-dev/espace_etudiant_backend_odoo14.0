from odoo import http
from odoo.http import request
import base64

class AuthController(http.Controller):
    
    @http.route('/api/auth', type='json', auth='none', methods=['POST'], csrf=False)
    def auth(self, **params):
        try:
            db = params.get('db')
            login = params.get('login')
            password = params.get('password')
            
            if not all([db, login, password]):
                return {"error": "Missing parameters"}

            request.session.authenticate(db, login, password)
            uid = request.session.uid
            
            if not uid:
                return {"error": "Authentication failed"}

            user = request.env['res.users'].sudo().browse(uid)
            
            # Récupération de l'image de profil
            image_url = None
            
            # Détermination du rôle et récupération de l'image spécifique
            role = 'student'  # valeur par défaut
            
            if user.has_group('base.group_system'):
                role = 'admin'
                # Pour admin, utiliser l'image du user
                if user.image_1920:
                    image_url = "data:image/png;base64," + user.image_1920.decode('utf-8')
                    
            else:
                # Vérifier si c'est un enseignant
                enseignant = request.env['student.enseignant'].sudo().search([('user_id', '=', uid)], limit=1)
                if enseignant:
                    role = 'teacher'
                    # Utiliser l'image de l'enseignant (image_128)
                    if enseignant.image_128:
                        image_url = "data:image/png;base64," + enseignant.image_128.decode('utf-8')
                    # Sinon utiliser l'image du partner lié
                    elif enseignant.partner_id and enseignant.partner_id.image_1920:
                        image_url = "data:image/png;base64," + enseignant.partner_id.image_1920.decode('utf-8')
                else:
                    # C'est un étudiant
                    role = 'student'
                    # Vérifier s'il y a un modèle étudiant et récupérer son image
                    etudiant = request.env['student.etudiant'].sudo().search([('user_id', '=', uid)], limit=1)
                    if etudiant and etudiant.image_128:
                        image_url = "data:image/png;base64," + etudiant.image_128.decode('utf-8')
                    elif user.image_1920:
                        image_url = "data:image/png;base64," + user.image_1920.decode('utf-8')

            return {
                "status": "success",
                "uid": uid,
                "role": role,
                "name": user.name,
                "image": image_url,  # URL complète de l'image
                "session_id": request.session.sid
            }

        except Exception as e:
            return {"error": str(e)}
        