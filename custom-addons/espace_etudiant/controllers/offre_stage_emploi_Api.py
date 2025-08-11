from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class OfferController(http.Controller):

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

    def _serialize_offer(self, offer):
        """Helper method to serialize offer data including date handling"""
        serialized = {}
        for field, value in offer.items():
            if isinstance(value, datetime):
                serialized[field] = value.isoformat()
            elif isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], int):
                # Handle Many2one fields (id, name)
                serialized[field] = value[1] if field == 'company' else value[0]
            else:
                serialized[field] = value
        return serialized

    @http.route('/api/internship-offers', auth='public', methods=['GET'], type='http', website=True, cors='*')
    def get_internship_offers(self, **kw):
        try:
            domain = [('is_active', '=', True)]
            fields = ['id', 'title', 'company', 'duration', 'description', 
                     'requirements', 'remuneration', 'deadline', 'contact_email','lien']
            
            offers = request.env['student.internship.offer'].search_read(domain, fields)
            serialized_offers = [self._serialize_offer(offer) for offer in offers]
            
            return self._success_response(serialized_offers)
            
        except Exception as e:
            _logger.error("Error fetching internship offers: %s", str(e))
            return self._error_response({'error': str(e)}, 500)

    @http.route('/api/job-offers', auth='public', methods=['GET'], type='http', website=True, cors='*')
    def get_job_offers(self, **kw):
        try:
            domain = [('is_active', '=', True)]
            fields = ['id', 'title', 'company', 'contract_type', 'description',
                     'requirements', 'salary', 'deadline', 'contact_email','lien']
            
            if 'contract_type' in kw:
                domain.append(('contract_type', '=', kw['contract_type']))
            
            offers = request.env['student.job.offer'].search_read(domain, fields)
            serialized_offers = [self._serialize_offer(offer) for offer in offers]
            
            return self._success_response(serialized_offers)
            
        except Exception as e:
            _logger.error("Error fetching job offers: %s", str(e))
            return self._error_response({'error': str(e)}, 500)