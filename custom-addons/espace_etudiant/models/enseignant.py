from odoo import models, fields

class Enseignant(models.Model):
    _name = 'student.enseignant'
    _description = 'Enseignant'

    user_id = fields.Many2one('res.users', string="Utilisateur")
    grade = fields.Char()
    departement = fields.Char()
    specialite = fields.Char()
    date_recrutement = fields.Date()
    note_ids = fields.One2many('student.note', 'enseignant_id')
    absence_ids = fields.One2many('student.absence', 'enseignant_id')
    reclamation_ids = fields.One2many('student.reclamation_enseignant', 'enseignant_id')
    matieres_ids = fields.One2many('student.matiere', 'enseignant_id')