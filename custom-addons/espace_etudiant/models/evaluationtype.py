from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EvaluationType(models.Model):
    _name = 'student.evaluation.type'
    _description = "Type d'évaluation pour une matière"
    _order = 'matiere_id, type'

    matiere_id = fields.Many2one('student.matiere', required=True, ondelete='cascade', string="Matière")
    type = fields.Selection([
        ('cc', 'Contrôle Continu'),
        ('tp', 'Travaux Pratiques'),
        ('examen', 'Examen Final')
    ], required=True, string="Type d'évaluation")
    
    pourcentage = fields.Float(string="Pourcentage (%)", required=True)

    _sql_constraints = [
        ('unique_type_per_matiere', 'unique(matiere_id, type)', 'Chaque type d\'évaluation doit être unique pour une matière.'),
        ('pourcentage_positive', 'CHECK(pourcentage > 0 AND pourcentage <= 100)', 'Le pourcentage doit être entre 1 et 100.')
    ]

    def name_get(self):
        """Personnaliser l'affichage du nom"""
        result = []
        for record in self:
            type_dict = dict(record._fields['type'].selection)
            type_label = type_dict.get(record.type, record.type)
            name = f"{type_label} ({record.pourcentage}%)"
            result.append((record.id, name))
        return result

    @api.constrains('pourcentage')
    def _check_pourcentage_value(self):
        """Vérifier que le pourcentage est valide"""
        for record in self:
            if record.pourcentage <= 0 or record.pourcentage > 100:
                raise ValidationError("Le pourcentage doit être entre 1 et 100.")

    @api.constrains('matiere_id', 'pourcentage')
    def _check_total_pourcentage(self):
        """Vérifier que la somme des pourcentages ne dépasse pas 100%"""
        for record in self:
            if record.matiere_id:
                # Calculer le total des pourcentages pour cette matière
                total_pourcentage = sum(
                    self.search([('matiere_id', '=', record.matiere_id.id)]).mapped('pourcentage')
                )
                
                if total_pourcentage > 100:
                    raise ValidationError(
                        f"La somme des pourcentages pour la matière '{record.matiere_id.name}' "
                        f"ne peut pas dépasser 100%. Actuellement: {total_pourcentage}%"
                    )

    @api.model
    def create(self, vals):
        """Créer un nouveau type d'évaluation avec validation"""
        result = super(EvaluationType, self).create(vals)
        # Déclencher la validation du total
        result._check_total_pourcentage()
        return result

    def write(self, vals):
        """Modifier un type d'évaluation avec validation"""
        result = super(EvaluationType, self).write(vals)
        # Déclencher la validation du total après modification
        self._check_total_pourcentage()
        return result