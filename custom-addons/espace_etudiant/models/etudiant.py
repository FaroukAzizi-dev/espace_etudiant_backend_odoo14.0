from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = 'student.etudiant'
    _description = 'Étudiant'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', string="Contact")
    user_id = fields.Many2one('res.users', string="Utilisateur lié")

    # Attributs académiques
    nb_credits = fields.Integer(string="Nombre de crédits")
    moyenne = fields.Float(string="Moyenne")
    rang = fields.Integer(string="Rang")
    classe_id = fields.Many2one('student.classe', string="Classe")
    category_id = fields.Many2one('student.category', string="Catégorie")  # ex: Régulier, Redoublant, etc.
    matricule = fields.Char(string="Matricule", required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('student.etudiant') or 'New')
    date_inscription = fields.Date(string="Date d'inscription")
    statut = fields.Selection([
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('graduated', 'Diplômé'),
        ('dropout', 'Abandonné')
    ], string="Statut", default='active')
    
    # Informations personnelles supplémentaires
    birth_date = fields.Date(string="Date de naissance")
    gender = fields.Selection([
        ('m', 'Masculin'),
        ('f', 'Féminin'),
        ('o', 'Autre')
    ], string="Genre", default='m')
    blood_group = fields.Selection([
        ('A+', 'A+'),
        ('B+', 'B+'),
        ('O+', 'O+'),
        ('AB+', 'AB+'),
        ('A-', 'A-'),
        ('B-', 'B-'),
        ('O-', 'O-'),
        ('AB-', 'AB-')
    ], string="Groupe sanguin")
    nationality_id = fields.Many2one('res.country', string="Nationalité")
    adresse_domicile = fields.Char(string="Adresse domicile")
    telephone = fields.Char(string="Téléphone")
    email_personnel = fields.Char(string="Email personnel")

    # Contact d'urgence
    emergency_contact_name = fields.Char(string="Nom du contact d'urgence")
    emergency_contact_phone = fields.Char(string="Téléphone du contact d'urgence")

    # Documents et relations
    document_ids = fields.One2many('student.document', 'etudiant_id', string="Documents")
    absence_ids = fields.One2many('student.absence', 'etudiant_id', string="Absences")
    note_ids = fields.One2many('student.note', 'etudiant_id', string="Notes")
    reclamation_ids = fields.One2many('student.reclamation', 'etudiant_id', string="Réclamations")

    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        # Créer automatiquement un res.partner si non fourni
        if 'partner_id' not in vals:
            partner = self.env['res.partner'].create({
                'name': vals.get('name') or 'Nouveau Étudiant',
                'email': vals.get('email'),
                'is_student': True,
            })
            vals['partner_id'] = partner.id
        student = super().create(vals)
        return student

    def create_user_account(self):
        """Créer un compte utilisateur lié au partenaire s'il n'existe pas"""
        User = self.env['res.users']
        portal_group = self.env.ref('base.group_portal')
        for student in self:
            if not student.user_id:
                user = User.create({
                    'name': student.partner_id.name,
                    'login': student.partner_id.email or f'student{student.id}@example.com',
                    'partner_id': student.partner_id.id,
                    'groups_id': [(6, 0, [portal_group.id])],
                })
                student.user_id = user.id

    def unlink(self):
        # Supprimer aussi le partenaire lié
        for student in self:
            if student.partner_id:
                student.partner_id.unlink()
        return super().unlink()
