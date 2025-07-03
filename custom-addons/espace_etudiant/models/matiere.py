from odoo import models, fields

class Matiere(models.Model):
    _name = 'student.matiere'
    _description = 'Matière'

    name = fields.Char()
    admin_id = fields.Many2one('student.admin')
    enseignant_id = fields.Many2one('student.enseignant')
    niveau = fields.Char()
    semestre = fields.Char()
