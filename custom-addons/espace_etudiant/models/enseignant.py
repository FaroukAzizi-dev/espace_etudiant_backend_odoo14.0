from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Enseignant(models.Model):
    _name = 'student.enseignant'
    _description = 'Enseignant'
    _inherits = {'res.partner': 'partner_id'}
    
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade', string="Contact")
    user_id = fields.Many2one('res.users', string="Utilisateur lié", readonly=True)
    
    # Image directement sur l'enseignant
    image_128 = fields.Image("Image", max_width=128, max_height=128)
    
    # Champs personnels
    nom = fields.Char(string="Nom", related='partner_id.name', store=True, readonly=False)
    prenom = fields.Char(string="Prénom")
    email = fields.Char(string="Email", related='partner_id.email', store=True, readonly=False)
    identifiant = fields.Char(string="Identifiant", required=True, unique=True)
    telephone = fields.Char(string="Téléphone", related='partner_id.phone', store=True, readonly=False)
    adresse = fields.Char(string="Adresse", related='partner_id.street', store=True, readonly=False)
    cin = fields.Char(string="CIN")
    date_naissance = fields.Date(string="Date de naissance")
    
    # Champs professionnels
    grade = fields.Char(string="Grade")
    departement = fields.Char(string="Département")
    specialite = fields.Char(string="Spécialité")
    date_recrutement = fields.Date(string="Date de recrutement")
    
    # Relations
    note_ids = fields.One2many('student.note', 'enseignant_id', string="Notes")
    absence_ids = fields.One2many('student.absence', 'enseignant_id', string="Absences")
    reclamation_prof_ids = fields.One2many('student.reclamation_prof', 'enseignant_id', string="Réclamations")
    matiere_ids = fields.Many2many(
    'student.matiere',
    'matiere_enseignant_rel',  # table relationnelle
    'enseignant_id',                   # champ pour ce modèle
    'matiere_id',                      # champ pour l'autre modèle
    string="Matières enseignées"
)

    
    @api.constrains('image_128')
    def _check_image_required(self):
        for rec in self:
            if not rec.image_128:
                raise ValidationError("Chaque enseignant doit avoir une image.")
    
    @api.model
    def create(self, vals):
        if 'partner_id' not in vals:
            partner_vals = {
                'name': vals.get('nom') or 'Nouveau Enseignant',
                'email': vals.get('email'),
                'phone': vals.get('telephone'),
                'street': vals.get('adresse'),
                'is_company': False,
            }
            partner = self.env['res.partner'].create(partner_vals)
            vals['partner_id'] = partner.id
        
        enseignant = super().create(vals)
        enseignant._create_user_account()
        return enseignant
    
    def write(self, vals):
        # Synchroniser l'image avec le partner si nécessaire
        if 'image_128' in vals and vals['image_128']:
            for record in self:
                if record.partner_id:
                    record.partner_id.write({'image_128': vals['image_128']})
        return super().write(vals)
    
    def _create_user_account(self):
        User = self.env['res.users']
        teacher_group = self.env.ref('base.group_user')
        for teacher in self:
            if not teacher.user_id:
                login = teacher.identifiant or teacher.email or f'teacher{teacher.id}@example.com'
                password = teacher.cin or 'changeme123'
                user_vals = {
                    'name': teacher.partner_id.name,
                    'login': login,
                    'partner_id': teacher.partner_id.id,
                    'groups_id': [(6, 0, [teacher_group.id])],
                    'password': password,
                }
                user = User.create(user_vals)
                teacher.user_id = user.id
    
    def unlink(self):
        for teacher in self:
            if teacher.partner_id:
                teacher.partner_id.unlink()
        return super().unlink()