from odoo import models, fields

class Etudiant(models.Model):
    _name = 'student.etudiant'
    _description = 'Etudiant'

    user_id = fields.Many2one('res.users', string="Utilisateur")
    nb_credits = fields.Integer()
    moyenne = fields.Float()
    rang = fields.Integer()
    classe_id = fields.Many2one('student.classe', string="Classe")
    document_ids = fields.One2many('student.document', 'etudiant_id')
    absence_ids = fields.One2many('student.absence', 'etudiant_id')
    note_ids = fields.One2many('student.note', 'etudiant_id')
    reclamation_ids = fields.One2many('student.reclamation_etudiant', 'etudiant_id')
