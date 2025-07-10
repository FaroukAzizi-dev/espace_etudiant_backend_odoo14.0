from odoo import models, fields


class Niveau(models.Model):
    _name = 'student.niveau'
    _description = 'Niveau'

    name = fields.Char(string="Nom du niveau", required=True)  # L1, L2, L3, M1, etc.
    filiere_id = fields.Many2one('student.filiere', string="Filière", required=True)