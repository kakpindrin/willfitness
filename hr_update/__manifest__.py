##############################################################################
#
# Copyright (c) 2012 Veone - jonathan.arra@gmail.com
# Author: Jean Jonathan ARRA
#
# Fichier du module hr_synthese
# ##############################################################################
{
    "name" : "Mise à jour HR de Odoo",
    "version" : "1.0",
    "author" : "Parfait ALLA (https://www.linkedin.com/in/yoboue-alla-19906a154) / Franck AMAN (https://www.linkedin.com/in/franck-aman-92320a67)",
    'sequence': 1,
    "website" : "https://www.linkedin.com/in/franck-aman-92320a67",
    'category': 'Localization',
    "depends" : ["base", 'hr', 'hr_contract', 'hr_contract_extension'],
    "description": """
    """,
    "init_xml" : [],
    "demo_xml" : [],
    # "update_xml" : [
    #         "views/hr_category_employee_view.xml",
    #         "views/hr_category_salaire_view.xml",
    #         "views/res_company_view.xml",
    #         "views/res_partner_view.xml",
    #         "views/hr_employee_view.xml",
    #     ],
    "data":[
            "security/ir.model.access.csv",
            "data/abatements_data.xml",
            "data/categories_employee_data.xml",
            "views/hr_category_employee_view.xml",
            "views/hr_category_salaire_view.xml",
            "views/res_company_view.xml",
            "views/res_partner_view.xml",
            "views/hr_employee_view.xml"
        ],
    "installable": True
}
