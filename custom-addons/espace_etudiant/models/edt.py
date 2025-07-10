from odoo import models, fields, api
from datetime import date

class StudentEDT(models.Model):
    _name = 'student.edt'
    _description = "Emploi du Temps"

    semaine = fields.Char(string="Semaine", required=True, help="Exemple : Semaine 1 ou 2025-W27")
    chemin_fichier = fields.Binary(string="Fichier Emploi du Temps", required=True, attachment=True)
    date_upload = fields.Date(string="Date d'ajout", default=fields.Date.today)
    uploaded_by = fields.Many2one('res.users', string="Ajouté par", default=lambda self: self.env.user)
    classe_id = fields.Many2one('student.classe', string="Classe concernée", required=True)
