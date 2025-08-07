# models/student_event.py
from odoo import models, fields

class StudentEvent(models.Model):
    _name = 'student.event'
    _description = 'Événement estudiantin'
    
    name = fields.Char('Titre', required=True)
    description = fields.Text('Description')
    start_date = fields.Datetime('Date de début', required=True)
    end_date = fields.Datetime('Date de fin', required=True)
    location = fields.Char('Lieu')
    image = fields.Binary('Image')
    active = fields.Boolean('Actif', default=True)