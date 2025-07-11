# -*- coding: utf-8 -*-

import calendar
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

week_days = [(calendar.day_name[0], _(calendar.day_name[0])),
             (calendar.day_name[1], _(calendar.day_name[1])),
             (calendar.day_name[2], _(calendar.day_name[2])),
             (calendar.day_name[3], _(calendar.day_name[3])),
             (calendar.day_name[4], _(calendar.day_name[4])),
             (calendar.day_name[5], _(calendar.day_name[5])),
             (calendar.day_name[6], _(calendar.day_name[6]))]


class OpSession(models.Model):
    _name = "student.session"
    _inherit = ["mail.thread"]
    _description = "Sessions"

    name = fields.Char(compute='_compute_name', string='Name', store=True)
    timing_id = fields.Many2one('student.timing', 'Timing', required=True, tracking=True)
    start_datetime = fields.Datetime('Start Time', required=True, default=lambda self: fields.Datetime.now())
    end_datetime = fields.Datetime('End Time', required=True)
    matiere_id = fields.Many2one('student.matiere', 'Course', required=True)
    enseignant_id = fields.Many2one('student.enseignant', 'Faculty', required=True)
    classe_id = fields.Many2one('student.classe', 'Class', required=True)
    color = fields.Integer('Color Index')
    type = fields.Char(compute='_compute_day', string='Day', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Canceled')],
        string='Status', default='draft')
    active = fields.Boolean(default=True)

    @api.depends('start_datetime')
    def _compute_day(self):
        for rec in self:
            rec.type = fields.Datetime.from_string(rec.start_datetime).strftime("%A")

    @api.depends('enseignant_id', 'matiere_id', 'start_datetime', 'timing_id')
    def _compute_name(self):
        for session in self:
            if session.enseignant_id and session.matiere_id and session.start_datetime and session.timing_id:
                session.name = (
                    f"{session.enseignant_id.name}:"
                    f"{session.matiere_id.name}:"
                    f"{session.timing_id.name}"
                )
            else:
                session.name = "Session"

    # State helper methods
    def lecture_draft(self):   self.state = 'draft'
    def lecture_confirm(self): self.state = 'confirm'
    def lecture_done(self):    self.state = 'done'
    def lecture_cancel(self):  self.state = 'cancel'

    # Constraints
    @api.constrains('start_datetime', 'end_datetime')
    def _check_date_time(self):
        for rec in self:
            if rec.start_datetime > rec.end_datetime:
                raise ValidationError(_('End Time cannot be before Start Time.'))

    @api.constrains('enseignant_id', 'timing_id', 'start_datetime', 'classe_id', 'matiere_id')
    def check_timetable_conflicts(self):
        ICP = self.env['ir.config_parameter'].sudo()
        faculty_constraint = ICP.get_param('timetable.is_faculty_constraint')
        class_subject_constraint = ICP.get_param('timetable.is_batch_and_subject_constraint')
        class_only_constraint = ICP.get_param('timetable.is_batch_constraint')

        for rec in self:
            conflicts = self.search([
                ('id', '!=', rec.id),
                ('start_datetime', '>=', rec.start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)),
                ('start_datetime', '<', rec.start_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)),
                ('timing_id', '=', rec.timing_id.id),
            ])

            for ses in conflicts:
                if faculty_constraint and rec.enseignant_id == ses.enseignant_id:
                    raise ValidationError(_("A teacher can't have two sessions at the same time."))

                if class_subject_constraint and rec.classe_id == ses.classe_id and rec.matiere_id == ses.matiere_id:
                    raise ValidationError(_("This class already has that subject at that time."))

                if class_only_constraint and rec.classe_id == ses.classe_id:
                    raise ValidationError(_("This class already has a session at that time."))