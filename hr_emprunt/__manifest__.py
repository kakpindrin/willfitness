##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_emprunt
# ##############################################################################
{
    "name" : "Emprunt",
    "version" : "1.0",
    "author" : "Parfait ALLA (https://www.linkedin.com/in/yoboue-alla-19906a154) / Franck AMAN (https://www.linkedin.com/in/franck-aman-92320a67)",
    'sequence': 1,
    "website" : "https://www.linkedin.com/in/franck-aman-92320a67",
    "category" : "Generic Modules/Human Resources",
    "depends" : ['hr', 'mail', 'hr_contract_extension'],
    "description": """ Module permettant de gérer les emprunts des employés 
(Echeanciers, Remboursement, interfaçage avec le module de paie)
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
        'email/notification_email.xml',
    ],
    "update_xml" : [
            "security/groups.xml",
            "security/ir.model.access.csv",
            "views/hr_emprunt_view.xml",
            "views/report_hr_emprunt.xml",
            'report/report.xml',
            "views/hr_demande_emprunt_view.xml",
       ],
    "installable": True
}
