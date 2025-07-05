from odoo import models, fields

class Enseignant(models.Model):
    _name = 'student.enseignant'
    _description = 'Enseignant'

    user_id = fields.Many2one('res.users', string="Utilisateur")
    grade = fields.Char()
    departement = fields.Char()
    specialite = fields.Char()
    date_recrutement = fields.Date()
    classe_ids = fields.Many2many(
    'student.classe',              # vers quel modèle on fait la relation
    'enseignant_classe_rel',       # nom de la table relationnelle
    'enseignant_id',               # colonne qui pointe vers l’enseignant
    'classe_id',                   # colonne qui pointe vers la classe
    string="Classes"
    )
    note_ids = fields.One2many('student.note', 'enseignant_id')
    absence_ids = fields.One2many('student.absence', 'enseignant_id')
    reclamation_ids = fields.One2many('student.reclamation_prof', 'enseignant_id')
    matieres_ids = fields.One2many('student.matiere', 'enseignant_id')