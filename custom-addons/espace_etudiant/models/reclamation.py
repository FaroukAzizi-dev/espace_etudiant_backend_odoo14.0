from odoo import models, fields

class Reclamation(models.Model):
    _name = 'student.reclamation'
    _description = 'Réclamation Étudiant'

    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant")
    admin_id = fields.Many2one('student.admin')
    titre = fields.Char()
    description = fields.Text()
    date_creation = fields.Datetime()
    etat = fields.Selection([
        ('traitee', 'Traitée'),
        ('en_cours', 'En Cours'),
        ('rejetee', 'Rejetée')
    ])
    reponse_admin = fields.Text()
    date_traitement = fields.Date()
