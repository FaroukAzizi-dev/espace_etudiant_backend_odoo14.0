from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import re

class Student(models.Model):
    _name = 'student.etudiant'
    _description = 'Étudiant'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Add tracking capabilities

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Utilisateur lié")
    cin = fields.Char(string="CIN", required=True)
    identifiant = fields.Char(string="Identifiant", required=True, help="Identifiant unique de l'étudiant")
    first_name = fields.Char('First Name', size=128, translate=True, required=True)
    last_name = fields.Char('Last Name', size=128, translate=True, required=True)
    birth_date = fields.Date(string="Date de naissance")
    gender = fields.Selection([
        ('m', 'Masculin'),
        ('f', 'Féminin')
    ], string="Genre", default='m')
    nationality_id = fields.Many2one('res.country', string="Nationalité")
    adresse_domicile = fields.Char(string="Adresse domicile")
    telephone = fields.Char(string="Téléphone")
    email_personnel = fields.Char(string="Email personnel")
    
    # Attributs académiques
    nb_credits = fields.Integer(string="Nombre de crédits")
    moyenne = fields.Float(string="Moyenne")
    rang = fields.Integer(string="Rang")
    classe_id = fields.Many2one('student.classe', string="Classe")
    date_inscription = fields.Date(string="Date d'inscription", default=fields.Date.today)
    statut = fields.Selection([
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('graduated', 'Diplômé'),
        ('dropout', 'Abandonné')
    ], string="Statut", default='active')
    
    programme_id = fields.Many2one('student.programme', string="Programme")
    filiere_id = fields.Many2one('student.filiere', string="Filière")
    niveau_id = fields.Many2one('student.niveau', string="Niveau")

    # Documents et relations
    document_ids = fields.One2many('student.document', 'etudiant_id', string="Documents")
    absence_ids = fields.One2many('student.absence', 'etudiant_id', string="Absences")
    note_ids = fields.One2many('student.note', 'etudiant_id', string="Notes")
    reclamation_ids = fields.One2many('student.reclamation', 'etudiant_id', string="Réclamations")
    
    # Academic records
    academic_records_ids = fields.One2many('student.academic.record', 'etudiant_id', string="Historique Académique")
    
    active = fields.Boolean(default=True)
    
    # --- Contraintes SQL pour l'unicité ---
    _sql_constraints = [
        ('cin_unique', 'unique(cin)', "Le CIN doit être unique."),
        ('identifiant_unique', 'unique(identifiant)', "L'identifiant doit être unique."),
    ]

    @api.constrains('cin')
    def _check_cin(self):
        for record in self:
            if record.cin:
                # Vérifier que le CIN contient exactement 8 chiffres
                if not (record.cin.isdigit() and len(record.cin) == 8):
                    raise ValidationError("Le CIN doit contenir exactement 8 chiffres.")

    @api.constrains('email_personnel')
    def _check_email(self):
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        for record in self:
            if record.email_personnel:
                if not re.match(email_regex, record.email_personnel):
                    raise ValidationError("L'email personnel n'a pas un format valide.")

    @api.constrains('identifiant')
    def _check_identifiant(self):
        for record in self:
            if not record.identifiant:
                raise ValidationError("L'identifiant est obligatoire.")

    @api.model
    def create(self, vals):
        if 'partner_id' not in vals:
            full_name = f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip()
            partner = self.env['res.partner'].create({
                'name': full_name or 'Nouveau Étudiant',
                'email': vals.get('email_personnel'),
                'is_company': False,
            })
            vals['partner_id'] = partner.id
        
        return super().create(vals)

    def create_user_account(self):
        """Créer un compte utilisateur lié au partenaire s'il n'existe pas"""
        User = self.env['res.users']
        portal_group = self.env.ref('base.group_portal')
        for student in self:
            if not student.user_id:

                login = student.email_personnel
                password = student.cin  # Utiliser le CIN comme mot de passe par défaut
                user = User.create({
                    'name': student.partner_id.name,
                    'login': login,
                    'password': password,
                    'partner_id': student.partner_id.id,
                    'groups_id': [(6, 0, [portal_group.id])],
                })
                student.user_id = user.id

class AcademicRecord(models.Model):
    _name = 'student.academic.record'
    _description = 'Historique academique de etudiant'
    
    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant", required=True, ondelete='cascade')
    moyenne = fields.Float(string="Moyenne")
    rang = fields.Integer(string="Rang")
    nb_credits = fields.Integer(string="Nombre de crédits")
    annee_universitaire = fields.Char(string="Année universitaire")