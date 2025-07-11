from odoo import models, fields, api

class Classe(models.Model):
    _name = 'student.classe'
    _description = 'Classe'

    name = fields.Char()
    filiere_id = fields.Many2one('student.filiere', string="Filière")
    niveau_id = fields.Many2one('student.niveau', string="Niveau")
    edt_id = fields.Many2one('student.edt', string="Emploi du temps")
    enseignant_ids = fields.Many2many(
        'student.enseignant',
        'enseignant_classe_rel',
        'classe_id',
        'enseignant_id',
        string="Enseignants"
    )
    classe_id = fields.Many2one('student.classe', string="Classe")


    