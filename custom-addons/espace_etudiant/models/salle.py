from odoo import models, fields, api

class Salle(models.Model):
    _name = 'student.salle'
    _description = 'Classroom'

    name = fields.Char(string='Room Name', required=True)
    capacity = fields.Integer(string='Capacity')
    building = fields.Char(string='Building')
    floor = fields.Integer(string='Floor')
    description = fields.Text(string='Description')