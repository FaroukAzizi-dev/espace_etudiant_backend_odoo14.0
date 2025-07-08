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
    'depends': [],
    'data': [
    # 1. Charger d'abord les dépendances (modèles nécessaires)
    'views/programme_action.xml',
    'views/filiere_action.xml',
    'views/niveau_action.xml',
    'views/enseignant.xml',

    # 2. Ensuite les vues qui en dépendent
    'views/classe_action.xml',
    'views/matiere_views.xml',
    'views/student_action.xml',

    # 3. Enfin le menu
    'views/student_menu.xml',
    ],


    'installable': True,
    'auto_install': False,
    'application': True,
}
