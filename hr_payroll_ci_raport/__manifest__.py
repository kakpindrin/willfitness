# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Les Rapports  de paie",
    "version": "1.0",
    "author" : "Parfait ALLA (https://www.linkedin.com/in/yoboue-alla-19906a154) / Franck AMAN (https://www.linkedin.com/in/franck-aman-92320a67)",
    'sequence': 1,
    "website" : "https://www.linkedin.com/in/franck-aman-92320a67",
    "depends": ["hr_payroll_ci"],
    "category": "hr",
    "description": """
    This module provide :
    """,
    'data': [
        "security/ir.model.access.csv",
        "data/report_paperformat.xml",
        "rapports/report.xml",
        "rapports/report_disa.xml",
        "views/hr_payroll_view.xml",
        "views/cotisation_mensuelle_report.xml",
        "views/report_payroll.xml",
        "views/hr_disa_view.xml",
        "rapports/cotisation_mensuelle_report.xml",
    ],
    'installable': True,
    'active': False,
}