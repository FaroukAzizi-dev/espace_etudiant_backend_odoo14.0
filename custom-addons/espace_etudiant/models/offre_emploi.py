from odoo import models, fields

class JobOffer(models.Model):
    _name = 'student.job.offer'
    _description = 'Offre d\'emploi'
    
    title = fields.Char('Titre', required=True)
    company = fields.Char('Company')
    description = fields.Html('Description')
    requirements = fields.Html('Exigences')
    contract_type = fields.Selection([
        ('cdi', 'CDI'),
        ('stage', 'Stage'),
        ('alternance', 'Alternance')
    ], 'Type de contrat', required=True)
    salary = fields.Char('Salaire')
    deadline = fields.Date('Date limite')
    contact_email = fields.Char('Email de contact')
    is_active = fields.Boolean('Active', default=True)