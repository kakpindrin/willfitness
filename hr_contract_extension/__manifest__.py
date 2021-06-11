# -*- coding: utf-8 -*-
##############################################################################
# Fichier du module hr_synthese
# ##############################################################################
{
    "name" : "Extension du contrats",
    "version" : "1.0",
    "author" : "Parfait ALLA (https://www.linkedin.com/in/yoboue-alla-19906a154) / Franck AMAN (https://www.linkedin.com/in/franck-aman-92320a67)",
    'sequence': 1,
    "website" : "https://www.linkedin.com/in/franck-aman-92320a67",
    'category': 'Human Resources',
    "depends" : ['base','hr', "hr_contract",'hr_contract_types','hr_payroll'],
    "description": """ Extension du contrats de travail des employés
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [

        ],
    "data":[
       "security/ir.model.access.csv",
        "data/primes_data.xml",
        "data/primes_non_imposable_data.xml",
       #  "wizard/hr_contract_closed.xml",
       #  "wizard/hr_reverse_contract.xml",
        "wizard/hr_compute_inverse_view.xml",
       #  # "views/res_country_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_convention_view.xml",
        "views/hr_contract_view.xml",
        ],
    "installable": True
}
