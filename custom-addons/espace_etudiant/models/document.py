from odoo import models, fields

class Document(models.Model):
    _name = 'student.document'
    _description = 'Document généré'

    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant")
    modele_id = fields.Many2one('student.document_modele')
    date_generation = fields.Datetime()
    type = fields.Selection([
        ('lettre_affectation', 'Lettre Affectation'),
        ('demande_stage', 'Demande de Stage'),
        ('journal_stage', 'Journal de Stage')
    ])
