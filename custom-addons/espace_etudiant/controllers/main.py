# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class StudentAPI(http.Controller):

    @http.route('/api/students', type='http', auth='none', methods=['GET'], cors='*')
    def get_students(self):
        """Récupérer la liste des étudiants"""
        try:
            # Se connecter avec l'utilisateur admin (pour test)
            students = request.env['student.etudiant'].sudo().search([])
            
            students_data = []
            for student in students:
                students_data.append({
                    'id': student.id,
                    'name': student.name or 'Sans nom',
                    'email': student.email or 'Sans email',
                    'telephone': student.telephone or 'Sans téléphone',
                })
            
            return request.make_response(
                json.dumps({
                    'success': True,
                    'data': students_data,
                    'count': len(students_data)
                }),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*'),
                    ('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'),
                    ('Access-Control-Allow-Headers', 'Content-Type')
                ]
            )
            
        except Exception as e:  
            return request.make_response(
                json.dumps({
                    'success': False,
                    'error': str(e)
                }),
                headers=[
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ]
            )