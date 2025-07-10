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
    description = fields.Text(string="Description")

    semestre = fields.Selection([
        ('1', 'Semestre 1'),
        ('2', 'Semestre 2')
    ], string="Semestre", required=True)

    volume_horaire = fields.Integer(string="Volume horaire")
    coefficient = fields.Float(string="Coefficient", required=True)

    classe_id = fields.Many2one('student.classe', string="Classe", required=True)

    enseignant_id = fields.Many2one('student.enseignant', string="Enseignant principal")
    enseignant_ids = fields.Many2many(
        'student.enseignant',
        'matiere_enseignant_rel',
        'matiere_id',
        'enseignant_id',
        string="Enseignants",
        required=True
    )

    # Champs de formule de calcul avec valeur par défaut 0
    poids_cc = fields.Float(string="Poids Contrôle Continu (%)", default=0.0)
    poids_tp = fields.Float(string="Poids TP (%)", default=0.0)
    poids_examen = fields.Float(string="Poids Examen (%)", default=0.0)

    active = fields.Boolean(string="Actif", default=True)

    # Champ calculé pour afficher la formule active
    formule_active = fields.Char(string="Formule d'évaluation", compute='_compute_formule_active', store=True)

    @api.depends('poids_cc', 'poids_tp', 'poids_examen')
    def _compute_formule_active(self):
        for matiere in self:
            formule_parts = []
            if matiere.poids_cc > 0:
                formule_parts.append(f"CC {matiere.poids_cc}%")
            if matiere.poids_tp > 0:
                formule_parts.append(f"TP {matiere.poids_tp}%")
            if matiere.poids_examen > 0:
                formule_parts.append(f"Examen {matiere.poids_examen}%")
            
            matiere.formule_active = " + ".join(formule_parts) if formule_parts else "Aucune formule définie"

    @api.constrains('enseignant_ids')
    def _check_enseignants(self):
        for matiere in self:
            if not matiere.enseignant_ids:
                raise ValidationError("Vous devez sélectionner au moins un enseignant.")

    @api.constrains('poids_cc', 'poids_tp', 'poids_examen')
    def _check_total_poids(self):
        for matiere in self:
            total = matiere.poids_cc + matiere.poids_tp + matiere.poids_examen
            
            # Vérifier qu'au moins un poids est défini
            if total == 0:
                raise ValidationError("Vous devez définir au moins un type d'évaluation (CC, TP ou Examen).")
            
            # Vérifier que la somme fait 100%
            if round(total, 2) != 100.0:
                raise ValidationError(f"La somme des poids doit être égale à 100%. Actuellement: {total}%")
            
            # Vérifier que les poids sont positifs ou nuls
            if matiere.poids_cc < 0 or matiere.poids_tp < 0 or matiere.poids_examen < 0:
                raise ValidationError("Les poids ne peuvent pas être négatifs.")

    @api.onchange('enseignant_ids')
    def _onchange_enseignant_ids(self):
        if self.enseignant_ids:
            if not self.enseignant_id or self.enseignant_id not in self.enseignant_ids:
                self.enseignant_id = self.enseignant_ids[0]

    @api.onchange('enseignant_id')
    def _onchange_enseignant_id(self):
        if self.enseignant_id and self.enseignant_id not in self.enseignant_ids:
            self.enseignant_ids = [(4, self.enseignant_id.id)]

    def name_get(self):
        result = []
        for record in self:
            enseignants_names = ', '.join(record.enseignant_ids.mapped('nom'))
            if enseignants_names:
                name = f"{record.name} ({enseignants_names})"
            else:
                name = record.name
            result.append((record.id, name))
        return result

    def get_formule_evaluation(self):
        """Retourne un dictionnaire avec les composants de la formule d'évaluation"""
        return {
            'cc': self.poids_cc if self.poids_cc > 0 else None,
            'tp': self.poids_tp if self.poids_tp > 0 else None,
            'examen': self.poids_examen if self.poids_examen > 0 else None,
            'total': self.poids_cc + self.poids_tp + self.poids_examen
        }