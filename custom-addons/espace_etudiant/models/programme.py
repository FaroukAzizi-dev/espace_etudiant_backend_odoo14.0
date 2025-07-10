from odoo import models, fields

class Programme(models.Model):
    _name = 'student.programme'
    _description = 'Programme'

    name = fields.Char(string="Nom du programme", required=True)  # Licence, Mastère, Mini MBA
    type = fields.Selection([
        ('licence', 'Licence'),
        ('mastere', 'Mastère'),
        ('mba', 'Mini MBA')
    ], string="Type", required=True)
    filiere_ids = fields.One2many('student.filiere', 'programme_id', string="Filières")

