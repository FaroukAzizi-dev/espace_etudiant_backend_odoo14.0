from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EvaluationType(models.Model):
    _name = 'student.evaluation.type'
    _description = 'Type d\'évaluation pour une matière'

    matiere_id = fields.Many2one('student.matiere', required=True, ondelete='cascade', string="Matière")
    type = fields.Selection([
        ('cc', 'Contrôle Continu'),
        ('ds', 'Devoir Surveillé'),
        ('examen', 'Examen Final'),
        ('tp', 'Travaux Pratiques')
    ], required=True, string="Type d'évaluation")
    coefficient = fields.Float(string="Coefficient (%)", required=True)

    @api.constrains('coefficient')
    def _check_coefficient(self):
        for record in self:
            if record.coefficient <= 0 or record.coefficient > 8:
                raise ValidationError("Le coefficient doit être entre 1 et 8.")
