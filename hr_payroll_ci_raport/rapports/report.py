# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2020 yoboue.alla@gmail.com
##############################################################################
from odoo import api, models, _
from ..tools import format_amount


class ReportPayroll(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.report_payroll'

    def get_total_line_by_code(self,object,code):
        sql = "SELECT sum(%s) FROM hr_payroll_line WHERE hr_payroll_id=%s"%(code,object.id)
        self._cr.execute(sql)
        result = self._cr.fetchone()
        if result:
            return result[0]
        return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env['hr.payroll'].browse(data['ids'])
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payroll',
            'docs': model,
            'data': data,
            'get_total_line_by_code': self.get_total_line_by_code,
            'format_amount': format_amount.manageSeparator,
        }


class ReportCnpsMensuel(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.cotisation_mensuelle_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env['hr.etat.cotisation.mensuelle'].browse(data['ids'])
        return {
            'doc_ids': docids,
            'doc_model': 'hr.etat.cotisation.mensuelle',
            'docs': model,
            'data': data,
            'format_amount': format_amount.manageSeparator,
        }


class ReportHrDisa(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.report_disa'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env['hr.disa'].browse(data['ids'])
        return {
            'doc_ids': docids,
            'doc_model': model,
            'docs': model,
            'data': data,
            'format_amount': format_amount.manageSeparator,
        }
 

