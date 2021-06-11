# -*- coding: utf-8 -*-
##############################################################################
#
# Fichier du module hr_contract_model
# ##############################################################################
{
    "name" : "Contracts Models",
    "version" : "1.0",
    'sequence': 1,
    'category': 'Human Resources',
    "author" : "Parfait ALLA (https://www.linkedin.com/in/yoboue-alla-19906a154) / Franck AMAN (https://www.linkedin.com/in/franck-aman-92320a67)",
    "website" : "https://www.linkedin.com/in/franck-aman-92320a67",
    "depends" : ["hr_contract", 'hr_contract_extension'],
    "description": """ 
        estion des modèles de contracts
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
            "security/ir.model.access.csv",
            "views/hr_contract_model_view.xml",
        ],
    "data":[
           
            ],
    "installable": True
}
