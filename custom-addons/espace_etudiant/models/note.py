from odoo import models, fields, api

class Note(models.Model):
    _name = 'student.note'
    _description = 'Note'

    enseignant_id = fields.Many2one('student.enseignant')
    matiere_id = fields.Many2one('student.matiere', required=True)
    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant", required=True)
    valeur = fields.Float()
    type = fields.Selection([], string="Type d'évaluation", required=True)  # vide au départ
    pourcentage = fields.Float(string="Coefficient (%)", readonly=True)

    @api.onchange('matiere_id')
    def _onchange_matiere_id(self):
        if self.matiere_id:
            types = [(et.type, dict(self.env['student.evaluation.type'].fields_get()['type']['selection'])[et.type])
                     for et in self.matiere_id.evaluation_type_ids]
            self._fields['type'].selection = types
            self.type = False  # reset si matière change

    @api.onchange('type')
    def _onchange_type(self):
        if self.type and self.matiere_id:
            eval_type = self.matiere_id.evaluation_type_ids.filtered(lambda et: et.type == self.type)
            if eval_type:
                self.pourcentage = eval_type.coefficient
