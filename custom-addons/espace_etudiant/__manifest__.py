# -*- coding: utf-8 -*-
{
    'name': 'Student Portal',
    'version': '1.0',
    'summary': 'Portail étudiant pour gestion des utilisateurs (étudiants, enseignants, parents, admins)',
    'description': """
        Module de portail étudiant avec espaces et rôles : 
        Étudiants, Enseignants, Administrateurs, Parents.
        Permet la gestion des utilisateurs liés à res.users, des classes, notes, emplois du temps, réclamations, etc.
    """,
    'author': 'Farouk Azizi , Said Laffet',
    'website': 'https://example.com',
    'category': 'Education',
    'depends': ['base' ,
                'mail',
                'website'],
    'data': [
    # Sécurité
    'security/ir.model.access.csv',
    'security/student_security.xml',

    # Modèles de base
    'views/programme_action.xml',
    'views/filiere_action.xml',
    'views/niveau_action.xml',
    'views/matiere_views.xml',
    'views/note.xml',

    # Modèles dépendants
    'views/enseignant.xml',
    'views/student_action.xml',
    'views/classe_action.xml',
    'views/timetable.xml',
    'views/timing.xml',

    # Réclamations
    'views/reclamation.xml',

    # Menus
    'views/student_menu.xml',
    ],

    'cors_enabled': True,

    'installable': True,
    'auto_install': False,
    'application': True,
}
