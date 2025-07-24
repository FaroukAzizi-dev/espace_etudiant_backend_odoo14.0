from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError
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
        # Check creation rights
        if not self.env.su and not self.check_access_rights('create', raise_exception=False):
            raise AccessError("You are not allowed to create students")
            
        if 'partner_id' not in vals:
            full_name = f"{vals.get('first_name', '')} {vals.get('last_name', '')}".strip()
            partner = self.env['res.partner'].create({
                'name': full_name or 'Nouveau Étudiant',
                'email': vals.get('email_personnel'),
                'is_company': False,
            })
            vals['partner_id'] = partner.id
        
        return super().create(vals)

    def write(self, vals):
        # Check write rights
        if not self.env.su and not self.check_access_rights('write', raise_exception=False):
            raise AccessError("You are not allowed to modify students")
        return super().write(vals)

    def unlink(self):
        # Check deletion rights
        if not self.env.su and not self.check_access_rights('unlink', raise_exception=False):
            raise AccessError("You are not allowed to delete students")
            
        partners = self.mapped('partner_id')
        res = super().unlink()
        partners.unlink()
        return res

class Reclamation(models.Model):
    _name = 'student.reclamation'
    _description = 'Réclamations des Étudiants'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant", required=True)
    titre = fields.Char(string="Titre", required=True)
    description = fields.Text(string="Description", required=True)
    date_creation = fields.Datetime(string="Date de création", default=fields.Datetime.now)
    etat = fields.Selection([
        ('nouvelle', 'Nouvelle'),
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('rejetee', 'Rejetée')
    ], string="État", default='nouvelle')
    piece_jointe = fields.Binary(string="Pièce jointe")
    nom_fichier = fields.Char(string="Nom du fichier")
    reponse_admin = fields.Text(string="Réponse de l'administration")
    admin_id = fields.Many2one('res.users', string="Traité par")
    date_traitement = fields.Datetime(string="Date de traitement")

    @api.model
    def create(self, vals):
        # Auto-set student if not specified (for authenticated student users)
        if 'etudiant_id' not in vals:
            student = self.env['student.etudiant'].search([
                ('user_id', '=', self.env.user.id)
            ], limit=1)
            if student:
                vals['etudiant_id'] = student.id
            else:
                raise AccessError("No student profile found for this user")
                
        return super().create(vals)

class AcademicRecord(models.Model):
    _name = 'student.academic.record'
    _description = 'Historique academique de etudiant'
    
    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant", required=True, ondelete='cascade')
    moyenne = fields.Float(string="Moyenne")
    rang = fields.Integer(string="Rang")
    nb_credits = fields.Integer(string="Nombre de crédits")
    annee_universitaire = fields.Char(string="Année universitaire")