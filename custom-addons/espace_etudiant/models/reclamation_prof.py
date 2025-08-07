from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ReclamationProf(models.Model):
    _name = 'student.reclamation_prof'
    _description = 'Réclamation Enseignant'
    _order = 'date_creation desc'

    enseignant_id = fields.Many2one('student.enseignant', string="Enseignant", required=True, ondelete='cascade')    
    admin_id = fields.Many2one('student.admin', string="Administrateur concerné")

    type_reclamation = fields.Selection([
        ('systeme', "Erreur dans le système"),
        ('etudiant', "Problème avec un étudiant"),
        ('administratif', "Problème administratif"),
        ('correction', "Demande de correction"),
        ('communication', "Problème de communication"),
        ('proposition', "Proposition de modification"),
    ], string="Type de réclamation", required=True)

    titre = fields.Char(string="Titre", required=True)
    description = fields.Text(string="Description détaillée", required=True)

    date_creation = fields.Datetime(string="Date de création", default=lambda self: fields.Datetime.now(), readonly=True)
    etat = fields.Selection([
        ('en_cours', 'En cours'),
        ('traitee', 'Traitée'),
        ('rejetee', 'Rejetée')
    ], string="État", default='en_cours', required=True)

    reponse_admin = fields.Text(string="Réponse de l'administration")

    @api.constrains('description')
    def _check_description_length(self):
        for rec in self:
            if rec.description and len(rec.description.strip()) < 10:
                raise ValidationError("La description doit contenir au moins 10 caractères.")

    @api.model
    def create(self, vals):
        vals['etat'] = 'en_cours'  # Toujours à l'état initial
        return super().create(vals)
