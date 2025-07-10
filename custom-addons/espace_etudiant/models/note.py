# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Note(models.Model):
    _name = 'student.note'
    _description = 'Gestion des Notes par Étudiant et par Matière'
    _rec_name = 'display_name'

    # Champ de nommage pour une meilleure lisibilité
    display_name = fields.Char(string="Description", compute='_compute_display_name', store=True)

    # --- Champs de saisie ---
    etudiant_identifiant = fields.Char(string="Identifiant Étudiant", required=True)
    matiere_code = fields.Char(string="Code Matière", required=True)

    # --- Champs techniques et relationnels ---
    etudiant_id = fields.Many2one('student.etudiant', string="Étudiant", required=True, ondelete='cascade')
    matiere_id = fields.Many2one('student.matiere', string="Matière", required=True, ondelete='cascade')
    enseignant_id = fields.Many2one('student.enseignant', string="Enseignant", compute='_compute_enseignant', store=True)

    # --- Champs affichés automatiquement (readonly) ---
    etudiant_nom = fields.Char(string="Nom Étudiant", related='etudiant_id.name', readonly=True)
    matiere_nom = fields.Char(string="Nom Matière", related='matiere_id.name', readonly=True)
    enseignant_nom = fields.Char(string="Enseignant", related='enseignant_id.name', readonly=True)

    # --- Champs pour chaque type de note (sans DS) ---
    note_cc = fields.Float(string="Note Contrôle Continu")
    note_tp = fields.Float(string="Note Travaux Pratiques")
    note_examen = fields.Float(string="Note Examen Final")

    # --- Champs booléens pour contrôler la visibilité des champs de note (sans DS) ---
    has_cc_eval = fields.Boolean(compute='_compute_evaluation_visibility')
    has_tp_eval = fields.Boolean(compute='_compute_evaluation_visibility')
    has_examen_eval = fields.Boolean(compute='_compute_evaluation_visibility')

    # --- Champ pour la moyenne générale calculée ---
    moyenne_generale = fields.Float(string="Moyenne Générale", compute='_compute_moyenne_generale', store=True, digits=(4, 2))

    # Contrainte SQL pour garantir un seul relevé par étudiant et par matière
    _sql_constraints = [
        ('etudiant_matiere_uniq', 'unique (etudiant_id, matiere_id)',
         'Un relevé de notes existe déjà pour cet étudiant et cette matière !')
    ]

    @api.depends('etudiant_id.name', 'matiere_id.name')
    def _compute_display_name(self):
        for record in self:
            if record.etudiant_nom and record.matiere_nom:
                record.display_name = f"Notes de {record.etudiant_nom} en {record.matiere_nom}"
            else:
                record.display_name = "Nouveau Relevé de Notes"

    @api.depends('matiere_id')
    def _compute_evaluation_visibility(self):
        """ Détermine quels champs de note afficher en fonction de la formule de la matière. """
        for record in self:
            record.has_cc_eval = record.has_tp_eval = record.has_examen_eval = False
            if record.matiere_id:
                eval_types = record.matiere_id.evaluation_type_ids.mapped('type')
                record.has_cc_eval = 'cc' in eval_types
                record.has_tp_eval = 'tp' in eval_types
                record.has_examen_eval = 'examen' in eval_types

    @api.depends('matiere_id', 'note_cc', 'note_tp', 'note_examen')
    def _compute_moyenne_generale(self):
        """ Calcule la moyenne générale pondérée en fonction des notes saisies et de la formule. """
        for record in self:
            if not record.matiere_id or not record.matiere_id.evaluation_type_ids:
                record.moyenne_generale = 0.0
                continue
            
            notes_map = {
                'cc': record.note_cc, 
                'tp': record.note_tp,
                'examen': record.note_examen
            }

            somme_ponderee = 0.0
            for formule in record.matiere_id.evaluation_type_ids:
                grade = notes_map.get(formule.type)
                if grade is not None and grade >= 0:
                    somme_ponderee += grade * (formule.pourcentage / 100.0)
            
            record.moyenne_generale = somme_ponderee

    @api.depends('etudiant_id', 'matiere_id')
    def _compute_enseignant(self):
        """ Met à jour l'enseignant basé sur l'étudiant et la matière. """
        for record in self:
            if record.etudiant_id and record.matiere_id and record.etudiant_id.classe_id:
                enseignant = record.etudiant_id.classe_id.enseignant_ids.filtered(
                    lambda e: record.matiere_id in e.matiere_ids
                )
                record.enseignant_id = enseignant[0] if enseignant else False
            else:
                record.enseignant_id = False

    @api.onchange('etudiant_identifiant')
    def _onchange_etudiant_identifiant(self):
        if self.etudiant_identifiant:
            etudiant = self.env['student.etudiant'].search([('identifiant', '=', self.etudiant_identifiant)], limit=1)
            self.etudiant_id = etudiant.id if etudiant else False
            if not etudiant:
                return {'warning': {'title': 'Attention', 'message': f"Aucun étudiant trouvé avec l'identifiant : {self.etudiant_identifiant}"}}

    @api.onchange('matiere_code')
    def _onchange_matiere_code(self):
        if self.matiere_code:
            matiere = self.env['student.matiere'].search([('code', '=', self.matiere_code)], limit=1)
            if matiere:
                self.matiere_id = matiere.id
                self.note_cc = self.note_tp = self.note_examen = 0.0
            else:
                self.matiere_id = False
                return {'warning': {'title': 'Attention', 'message': f"Aucune matière trouvée avec le code : {self.matiere_code}"}}