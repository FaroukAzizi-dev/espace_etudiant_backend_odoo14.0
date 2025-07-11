from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Student(models.Model):
    _name = 'student.etudiant'
    _description = 'Étudiant'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string="Utilisateur lié")
    cin = fields.Char(string="CIN", required=True)
    identifiant = fields.Char(string="Identifiant", required=True, help="Identifiant unique de l'étudiant")
    first_name = fields.Char('First Name', size=128, translate=True)
    last_name = fields.Char('Last Name', size=128, translate=True)
    birth_date = fields.Date(string="Date de naissance")
    gender = fields.Selection([
        ('m', 'Masculin'),
        ('f', 'Féminin')
    ], string="Genre", default='m')
    nationality_id = fields.Many2one('res.country', string="Nationalité")
    adresse_domicile = fields.Char(string="Adresse domicile")
    telephone = fields.Char(string="Téléphone")
    email_personnel = fields.Char(string="Email personnel")
    user_id = fields.Many2one('res.users', string="Utilisateur lié")

    # Attributs académiques
    nb_credits = fields.Integer(string="Nombre de crédits")
    moyenne = fields.Float(string="Moyenne")
    rang = fields.Integer(string="Rang")
    classe_id = fields.Many2one('student.classe', string="Classe")
    date_inscription = fields.Date(string="Date d'inscription")
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
    academic_record_ids = fields.One2many('student.academic.record', 'etudiant_id', string="Historique académique")
    
    


    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        # Créer automatiquement un res.partner si non fourni
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

    def unlink(self):
        # Supprimer aussi le partenaire lié
        for student in self:
            if student.partner_id:
                student.partner_id.unlink()
        return super().unlink()
    
    @api.onchange('programme_id')
    def _onchange_programme_id(self):
        # Quand on change de programme, on vide la filière et le niveau
        self.filiere_id = False
        self.niveau_id = False

    @api.onchange('filiere_id')
    def _onchange_filiere_id(self):
        # Quand on change de filière, on vide le niveau
        self.niveau_id = False
        
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.identifiant}] {record.name}"
            result.append((record.id, name))
        return result



class AcademicRecord(models.Model):
    _name = 'student.academic.record'
    _description = "Fiche académique annuelle"

    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant", required=True, ondelete="cascade")
    annee = fields.Char(string="Année universitaire", required=True)
    moyenne = fields.Float(string="Moyenne", digits=(4, 2))
    nombre_credits = fields.Integer(string="Nombre de crédits")
    rang = fields.Integer(string="Rang")

    # Champ lié stocké pour date d'inscription
    date_inscription = fields.Date(related='etudiant_id.date_inscription', store=True, string="Date d'inscription Étudiant")

    classe = fields.Char(string="Année universitaire liée", compute="_compute_classe", store=True)

    programme_id = fields.Many2one('student.programme', string="Programme")
    filiere_id = fields.Many2one('student.filiere', string="Filière")
    niveau_id = fields.Many2one('student.niveau', string="Niveau")

    @api.depends('date_inscription')
    def _compute_classe(self):
        for record in self:
            if record.date_inscription:
                year = record.date_inscription.year
                record.classe = f"{year}/{year + 1}"
            else:
                record.classe = "N/A"


