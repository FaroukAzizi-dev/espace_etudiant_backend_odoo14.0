from odoo import models, fields


class ReclamationProf(models.Model):
    _name = 'student.reclamation_prof'
    _description = 'Réclamation Enseignant'

    enseignant_id = fields.Many2one('student.enseignant')
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
