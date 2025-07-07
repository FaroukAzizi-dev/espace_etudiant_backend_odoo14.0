from odoo import models, fields

class Filiere(models.Model):
    _name = 'student.filiere'
    _description = 'Filière'

    name = fields.Char(string="Nom de la filière", required=True)
    programme_id = fields.Many2one('student.programme', string="Programme", required=True)
    niveau_ids = fields.One2many('student.niveau', 'filiere_id', string="Niveaux")
