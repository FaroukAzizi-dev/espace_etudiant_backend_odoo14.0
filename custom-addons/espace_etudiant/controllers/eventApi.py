# controllers/student_event_api.py
from odoo import http
from odoo.http import request, Response
import json
from datetime import datetime

class StudentEventAPI(http.Controller):
    
    @http.route('/api/student/events', 
            type='http', 
            auth='public', 
            methods=['GET'], 
            csrf=False,
            cors='*')
    def get_events(self, **kwargs):
        try:
            domain = [('active', '=', True)]
            
            # Filtre pour les événements à venir
            if kwargs.get('upcoming'):
                domain.append(('start_date', '>=', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            # Filtre pour les événements passés
            if kwargs.get('past'):
                domain.append(('start_date', '<', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            events = request.env['student.event'].search(domain, order='start_date')
            
            result = []
            for event in events:
                event_data = {
                    'id': event.id,
                    'name': event.name,
                    'description': event.description,
                    'start_date': event.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'end_date': event.end_date.strftime('%Y-%m-%d %H:%M:%S') if event.end_date else None,
                    'location': event.location,
                    'lien' : event.lien
                }
                
                # Ajouter l'image si elle existe
                if event.image:
                    event_data['image'] = event.image.decode('utf-8')
                
                result.append(event_data)
            
            return Response(
                json.dumps({'events': result}),
                content_type='application/json',
                status=200
            )
            
        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                content_type='application/json',
                status=500
            )