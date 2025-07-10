from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Matiere(models.Model):
    _name = 'student.matiere'
    _description = 'Matière'
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Le code de la matière doit être unique.')
    ]

    name = fields.Char(string="Nom de la matière", required=True)
    code = fields.Char(string="Code", required=True, help="Code unique de la matière")
    description = fields.Text(string="Description", help="Description de la matière")

    semestre = fields.Selection([
        ('1', 'Semestre 1'),
        ('2', 'Semestre 2')
    ], string="Semestre", required=True)

    volume_horaire = fields.Integer(string="Volume horaire", help="Nombre d'heures totales")
    coefficient = fields.Float(string="Coefficient", required=True, help="Coefficient utilisé dans le calcul des moyennes")

    # Champ principal pour la compatibilité (optionnel maintenant)
    enseignant_id = fields.Many2one('student.enseignant', string="Enseignant principal")
    
    # Champ principal pour les enseignants (Many2many)
    enseignant_ids = fields.Many2many(
        'student.enseignant',
        'matiere_enseignant_rel',
        'matiere_id',
        'enseignant_id',
        string="Enseignants",
        required=True,
        help="Sélectionnez tous les enseignants qui vont enseigner cette matière"
    )
    
    classe_id = fields.Many2one('student.classe', string="Classe", required=True)
    active = fields.Boolean(string="Actif", default=True)
    
       # AJOUTE CE CHAMP :
    evaluation_type_ids = fields.One2many(
        'student.evaluation.type',
        'matiere_id',
        string="Types d'évaluation"
    )


    @api.constrains('enseignant_ids')
    def _check_enseignants(self):
        """Vérifier qu'au moins un enseignant est sélectionné"""
        for matiere in self:
            if not matiere.enseignant_ids:
                raise ValidationError("Vous devez sélectionner au moins un enseignant pour cette matière.")

    @api.onchange('enseignant_ids')
    def _onchange_enseignant_ids(self):
        """Définir automatiquement l'enseignant principal"""
        if self.enseignant_ids:
            # Définir le premier enseignant comme principal s'il n'y en a pas
            if not self.enseignant_id or self.enseignant_id not in self.enseignant_ids:
                self.enseignant_id = self.enseignant_ids[0]

    @api.onchange('enseignant_id')
    def _onchange_enseignant_id(self):
        """Ajouter l'enseignant principal aux enseignants si pas déjà présent"""
        if self.enseignant_id and self.enseignant_id not in self.enseignant_ids:
            self.enseignant_ids = [(4, self.enseignant_id.id)]

    def get_all_enseignants(self):
        """Retourne tous les enseignants de la matière"""
        return self.enseignant_ids

    def name_get(self):
        """Personnaliser l'affichage du nom avec les enseignants"""
        result = []
        for record in self:
            enseignants_names = ', '.join(record.enseignant_ids.mapped('nom'))
            if enseignants_names:
                name = f"{record.name} ({enseignants_names})"
            else:
                name = record.name
            result.append((record.id, name))
        return result