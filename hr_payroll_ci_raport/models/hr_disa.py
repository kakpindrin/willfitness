# -*- coding:utf-8 -*-

from __future__ import division

import time
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import datetime


class HrDisa(models.TransientModel):
    _name = "hr.disa"
    _description = "Gestion de la DISA"

    date_from = fields.Date('Debut Disa', default=lambda *a: time.strftime('%Y-01-01'))
    date_to = fields.Date('Fin Disa', default=lambda *a: time.strftime('%Y-12-31'))
    total_salaire_brut_annuel = fields.Float('Total brut annuel')
    total_montant_pf_at = fields.Float('Total montant PF/AT')
    total_montant_retraite = fields.Float('Total montant retraite')
    line_ids = fields.One2many('hr.disa.line','disa_id','Ligne de la disa')
    company_id = fields.Many2one('res.company','Company', default=lambda self: self.env.user.company_id)
    year = fields.Char()

    def get_amount_by_code(self, slips, code):
        result = []
        amount = 0
        for slip in slips :
            tmp= slip.line_ids.filtered(lambda r: r.code==code)
            if tmp :
                result+= tmp
        if result :
            amount = sum([line.total for line in result])
        return amount

    def _get_compute_amount(self):
        year = datetime.datetime.now().year
        self.year = year
        payslip_obj = self.env['hr.payslip']
        slip_ids = payslip_obj.search([('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)])
        emp_id_double = slip_ids.mapped(lambda r: r.employee_id.id)
        emp_ids = list(set(emp_id_double))
        emp_res = {}
        for e in emp_ids:
            payslips = slip_ids.search([('employee_id', '=', e)])
            emp_res[e] = payslips
        i = 0
        lines = []
        total_salaire_brut_annuel = 0
        total_montant_pf_at = 0
        total_montant_retraite = 0
        for e in emp_res.keys():
            i += 1
            employee = self.env['hr.employee'].search([('id', '=', e)])
            schedule_pay = employee.contract_id.schedule_pay
            type_salarie = ''
            if schedule_pay == 'monthly':
                type_salarie = 'Mensuel'
            if schedule_pay == 'quarterly':
                type_salarie = 'Trimestriel'
            if schedule_pay == 'semi-annually':
                type_salarie = 'Semestriel'
            if schedule_pay == 'annually':
                type_salarie = 'Annuel'
            if schedule_pay == 'weekly':
                type_salarie = 'Hebdomadaire'
            if schedule_pay == 'bi-weekly':
                type_salarie = 'Bi-hebdomadaire'
            if schedule_pay == 'bi-monthly':
                type_salarie = 'Bi-mensuel'
            payslips = emp_res[e]
            pf_at = self.get_amount_by_code(payslips, 'BASE_IMP_2')
            # at = self.get_amount_by_code(payslips, 'BASE_IMP_2')
            data = {
                'num_order': i,
                'nom': employee.name,
                'num_cnps': employee.matricule_cnps,
                'date_naiss': employee.birthday,
                'date_embauche': employee.contract_id.date_start,
                'date_depart': employee.contract_id.date_end,
                'type_salarie': type_salarie,
                'salaire_brute': self.get_amount_by_code(payslips, 'BASE_CNPS'),
                'duree_activite': len(payslips),
                'montant_pf_at': pf_at,
                'montant_retraite': self.get_amount_by_code(payslips, 'BASE_CNPS'),
                'regime': '',
                'observation': '',
            }
            total_salaire_brut_annuel += data['salaire_brute']
            total_montant_pf_at += data['montant_pf_at']
            total_montant_retraite += data['montant_retraite']
            #lines += [data]
            lines.append((0, 0, data))
        self.total_salaire_brut_annuel = total_salaire_brut_annuel
        self.total_montant_pf_at = total_montant_pf_at
        self.total_montant_retraite = total_montant_retraite
        self.line_ids = lines

    def print_disa(self):
        print('ok ok')
        #data = {'form': self.read(['date_from', 'date_to'])[0]}
        data = {'ids': self.id, 'form': self.read(['date_from', 'date_to'])[0], 'model': 'hr.disa'}
        self._get_compute_amount()
        return self.env.ref('hr_payroll_ci_raport.hr_disa_report_id').with_context(landscape=True).report_action(self, data=data)


class HrDisaLine(models.TransientModel):
    _name = "hr.disa.line"

    num_order = fields.Integer('NUMERO D’ORDRE', default=0)
    nom = fields.Char()
    num_cnps = fields.Char()
    date_naiss = fields.Date()
    date_embauche = fields.Date()
    date_depart = fields.Date()
    type_salarie = fields.Char()
    salaire_brute = fields.Float(digits_compute=dp.get_precision('Account'))
    duree_activite = fields.Integer()
    montant_pf_at = fields.Float(digits_compute=dp.get_precision('Account'))
    montant_retraite = fields.Float(digits_compute=dp.get_precision('Account'))
    regime = fields.Integer()
    observation = fields.Text('Observation')
    disa_id = fields.Many2one('hr.disa', 'DISA')
