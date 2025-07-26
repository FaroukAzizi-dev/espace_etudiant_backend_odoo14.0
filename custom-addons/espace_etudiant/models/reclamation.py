from odoo import models, fields, api
from datetime import datetime

class Reclamation(models.Model):
    _name = 'student.reclamation'
    _description = 'Réclamation Étudiant'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Recommended for tracking
    
    etudiant_id = fields.Many2one(
        'student.etudiant',
        string="Étudiant",
        default=lambda self: self.env['student.etudiant'].search([('user_id', '=', self.env.user.id)], limit=1),
        required=True
    )
    admin_id = fields.Many2one(
        'res.users',  # Changed to built-in users model
        string="Administrateur",
        readonly=True,
        tracking=True  # Track changes to this field
    )
    titre = fields.Char(
        string="Titre",
        required=True
    )
    description = fields.Text(
        string="Description",
        required=True
    )
    date_creation = fields.Datetime(
        string="Date de création",
        default=lambda self: fields.Datetime.now(),
        readonly=True
    )
    etat = fields.Selection([
        ('nouvelle', 'Nouvelle'),
        ('en_cours', 'En Cours'),
        ('traitee', 'Traitée'),
        ('rejetee', 'Rejetée')
    ], string="État", default='nouvelle', tracking=True)
    reponse_admin = fields.Text(
        string="Réponse de l'administration",
        readonly=True
    )
    date_traitement = fields.Datetime(
        string="Date de traitement",
        readonly=True
    )
    piece_jointe = fields.Binary(
        string="Pièce jointe"
    )
    nom_fichier = fields.Char(
        string="Nom du fichier"
    )

    def action_prendre_en_charge(self):
        self.write({
            'etat': 'en_cours',
            'admin_id': self.env.user.id  # Assign current user directly
        })

    def action_traiter(self, reponse):
        self.write({
            'etat': 'traitee',
            'reponse_admin': reponse,
            'date_traitement': fields.Datetime.now()
        })

    def action_rejeter(self, raison):
        self.write({
            'etat': 'rejetee',
            'reponse_admin': raison,
            'date_traitement': fields.Datetime.now()
        })