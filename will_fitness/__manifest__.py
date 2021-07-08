# -*- coding: utf-8 -*-
{
    'name': "Will Fitness",

    'summary': """Gestion salle Sport""",

    'description': """
        Gestion de la salle par:
        - Les Présences (coaches, élèves)
        - Le Planning de travail
        - La Paie des coaches et autres employés
        - La Comptabilité Will Fitness
        - Les Abonnements (Rappels réguliers de paiements 3 jours avant échéance)
        - Les Ventes de Services ou autres produits
        - Les Achats de services ou autres produits 
    """,

    'author': "ADISA DIGITAL",
    'website': "http://adisa.digital",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'planning', 'sale_subscription', 'account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/will_this_week_print_coach_planning.xml',
        'report/will_next_week_print_coach_planning.xml',
        'report/will_specific_print_coach_planning.xml',
        'report/will_print_partner_contract.xml',
        'report/res_partner_badge.xml',
        'data/ir_sequence_data.xml',
        'views/menu.xml',
        'views/res_partner.xml',
        'views/presences.xml',
        'views/impression_planning.xml',
        'views/planning_slot.xml',
        'views/classes.xml',
        'views/sale_subscription.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
