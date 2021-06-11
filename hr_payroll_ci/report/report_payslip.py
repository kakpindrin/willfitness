#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

#from openerp.osv import osv
#from ..tools import format_amount
#from openerp.report import report_sxw
import dateutil
import time
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import api, models
from ..tools import format_amount


class PayslipCustomReport(models.AbstractModel):
    _name = 'report.hr_payroll_ci.report_payslip'

    def get_payslip_lines(self, obj):
        payslip_line = self.env['hr.payslip.line'].search([])
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].appears_on_payslip is True:
                ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(ids)
        return res

    def get_somme_rubrique(self, obj=None, code=''):

        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', obj.employee_id.id)])
        #payslip_obj = self.env['hr.payslip'].browse(payslip_ids)

        cpt = 0
        #annee = obj.date_to[2:4]
        d = str(obj.date_to)
        date_compare = d[2:4]
        for payslip in payslip_obj:
            d = str(payslip.date_to)
            date_to = d[2:4]
            for line in payslip.line_ids:
                if line.salary_rule_id.code == code and obj.date_to >= payslip.date_to and date_to == date_compare:
                    cpt += line.total
        return cpt

    # def get_lines_by_contribution_register(self):
    #     res = {'net': 450}
    #     return res

    def get_amount_rubrique(self, obj, rubrique=''):
        for id in range(len(obj)):
            line_ids = obj[id].line_ids
            total = 0
            for line in line_ids:
                if line.code == rubrique:
                    total = line.total
            return total

    # def _get_payslip_lines(self, date_from, date_to):
    #     result = {}
    #     result.setdefault('net', 0)
    #     self.env.cr.execute("""
    #         SELECT pl.id from hr_payslip_line as pl
    #         LEFT JOIN hr_payslip AS hp on (pl.slip_id = hp.id)
    #         WHERE (hp.date_from >= %s) AND (hp.date_to <= %s)
    #         ORDER BY pl.slip_id, pl.sequence""", (date_from, date_to))
    #     line_ids = [x[0] for x in self.env.cr.fetchall()]
    #     cpt = 0
    #     for line in self.env['hr.payslip.line'].browse(line_ids):
    #         #result.setdefault(line.register_id.id, self.env['hr.payslip.line'])
    #         if line.salary_rule_id.code == 'NET':
    #             #cpt += line.total
    #             result['net'] += line.total
    #
    #     #result.setdefault(line.register_id.id, self.env['hr.payslip.line'])
    #     #result['net'] = cpt
    #     return result

    @api.model
    def _get_report_values(self, docids, data=None):
        print(docids)
        payslips = self.env['hr.payslip'].browse(docids)
        print(payslips)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'data': data,
            'get_payslip_lines': self.get_payslip_lines,
            'get_somme_rubrique': self.get_somme_rubrique,
            'get_amount_rubrique': self.get_amount_rubrique,
            'format_amount': format_amount.manageSeparator,
        }

