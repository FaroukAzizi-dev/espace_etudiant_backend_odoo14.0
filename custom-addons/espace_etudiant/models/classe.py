from odoo import models, fields

class Classe(models.Model):
    _name = 'student.classe'
    _description = 'Classe'

    name = fields.Char()
    filiere = fields.Char()
    niveau = fields.Char()
    edt_id = fields.Many2one('student.edt', string="Emploi du temps")
    