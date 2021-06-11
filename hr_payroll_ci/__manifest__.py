##############################################################################
#
# Copyright (c) 2012 Veone - jonathan.arra@gmail.com
# Author: Jean Jonathan ARRA
#
# Fichier du module hr_synthese
# ##############################################################################
{
    "name" : "Payroll Côte d'Ivoire",
    "version" : "1.0",
    "author" : "Parfait ALLA (https://www.linkedin.com/in/yoboue-alla-19906a154) / Franck AMAN (https://www.linkedin.com/in/franck-aman-92320a67)",
    'sequence': 1,
    "website" : "https://www.linkedin.com/in/franck-aman-92320a67",
    "depends" : ["hr", "hr_emprunt", "hr_payroll", "hr_contract_extension", 'web', "hr_holidays"],
    "description": """ Synthèse de la paie
    - livre de paie mensuelle et périodique
    - Synthèse de paie des employés
    - interfaçage avec la gestion des contrats des employés
    """,
     "data": [
        "data/hr_salary_rule_category.xml",
        "data/hr_salary_rule.xml",
        #"data/hr_rule_input.xml",
        "data/hr_payroll_structure.xml",
        "data/service_cron.xml",
        "data/hr_leave_type.xml",
        "wizard/hr_payslip_prorata.xml",
        "views/hr_payroll_report.xml",
        "security/hr_security.xml",
        "security/ir.model.access.csv",
        'report/templates/layout_view.xml',
        "views/hr_leaves_extension.xml",
        "views/hr_employee.xml",
        "views/res_company_view.xml",
        "views/report_payslip.xml",
        "views/hr_payroll_ci.xml",
        "views/hr_contract_views.xml",
            ],
    "installable": True
}
