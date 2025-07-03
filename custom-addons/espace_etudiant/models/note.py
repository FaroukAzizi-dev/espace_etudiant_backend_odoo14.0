from odoo import models, fields

class Note(models.Model):
    _name = 'student.note'
    _description = 'Note'

    enseignant_id = fields.Many2one('student.enseignant')
    matiere_id = fields.Many2one('student.matiere')
    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant")
    valeur = fields.Float()
    pourcentage = fields.Float()
    type = fields.Selection([
        ('ds', 'ds'),
        ('examen', 'Examen'),
        ('tp', 'TP'),
    ])
