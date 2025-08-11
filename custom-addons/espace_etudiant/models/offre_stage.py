from odoo import models, fields

class InternshipOffer(models.Model):
    _name = 'student.internship.offer'
    _description = 'Offre de stage'
    
    title = fields.Char('Titre', required=True)
    company = fields.Char('Company')
    duration = fields.Char('Durée')
    description = fields.Html('Description')
    requirements = fields.Html('Exigences')
    remuneration = fields.Char('Rémunération')
    deadline = fields.Date('Date limite')
    contact_email = fields.Char('Email de contact')
    lien = fields.Char('lien')
    is_active = fields.Boolean('Active', default=True)