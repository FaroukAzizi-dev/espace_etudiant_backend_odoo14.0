from odoo import models, fields

class Absence(models.Model):
    _name = 'student.absence'
    _description = 'Absence'

    etudiant_id = fields.Many2one('student.etudiant')
    enseignant_id = fields.Many2one('student.enseignant')
    heure_debut = fields.Datetime()
    heure_fin = fields.Datetime()
    justifiee = fields.Selection([
        ('justifiee', 'Justifiée'),
        ('non_justifiee', 'Non Justifiée')
    ])
    motif = fields.Text()
