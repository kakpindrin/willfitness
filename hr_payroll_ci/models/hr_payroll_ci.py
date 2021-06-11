# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2014 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_payroll_ci
# ##############################################################################  -->


import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import netsvc
from odoo import fields, osv, api, models
from odoo import tools
from odoo.tools import date_utils
from odoo.tools.translate import _
from odoo.exceptions import Warning

from odoo.tools.safe_eval import safe_eval as eval
from decimal import Decimal
from collections import namedtuple
from math import fabs, ceil
from ..tools import format_amount
from odoo.tools.misc import format_date
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips

import babel

import odoo.addons.decimal_precision as dp

class hr_payslip(models.Model):
    _inherit="hr.payslip"

    def get_days_periode(self,start, end):
        r = (end + timedelta(days=1) - start).days
        return [start+timedelta(days=i) for i in range(r)]

    def write(self, vals):
        emp_obj = self.env['hr.employee']
        trouver = False
        for payslip in self:
            employee = payslip.employee_id
            list_payslips = employee.slip_ids
            date_from = datetime.strptime(str(payslip.date_from), '%Y-%m-%d')
            date_to = datetime.strptime(str(payslip.date_to), '%Y-%m-%d')
            Range = namedtuple('Range', ['start', 'end'])
            r1 = Range(start=date_from, end=date_to)
            new_list = []
            if len(list_payslips) != 1:
                for slip in list_payslips:
                    if slip.id != payslip.id:
                        new_list.append(slip)
                for slip in new_list:
                    old_date_from = datetime.strptime(str(slip.date_from), '%Y-%m-%d')
                    old_date_to = datetime.strptime(str(slip.date_to), '%Y-%m-%d')
                    r2 = Range(start=old_date_from, end=old_date_to)
                    result = (min(r1.end, r2.end) - max(r1.start, r2.start)).days + 1
                    if result > 0 and slip.contract_id.categorie_id == payslip.contract_id.categorie_id:
                        trouver = True
            if trouver is True:
                raise Warning(_("L'employé possède déjà un bulletin pour cette période"))
            else:
                super(hr_payslip, self).write(vals)
        return True

    # def get_test(self,cr, uid,ids,employee_id, context=None):
    #     res = {}
    #     obj_payslip = self.pool.get('hr.payslip')
    #     for emp in self.browse(cr, uid, ids, context=context):
    #         contract_ids = obj_payslip.search(cr, uid, [('employee_id','=',emp.id),], context=context)
    #         if contract_ids:
    #             raise osv.except_osv(_("test"),_("test"))

    # @api.onchange('employee_id', 'date_from', 'date_to')
    # def onchange_employee(self):
    #
    #     if (not self.employee_id) or (not self.date_from) or (not self.date_to):
    #         self.input_line_ids = []
    #         self.worked_days_line_ids = []
    #         self.contract_id = False
    #         self.struct_id = False
    #         self.name = False
    #         return
    #
    #     employee = self.employee_id
    #     date_from = self.date_from
    #     date_to = self.date_to
    #     contract_ids = []
    #
    #     ttyme = datetime.fromtimestamp(time.mktime(time.strptime(str(date_from), "%Y-%m-%d")))
    #     locale = self.env.context.get('lang') or 'en_US'
    #     self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
    #     self.company_id = employee.company_id
    #
    #     if not self.env.context.get('contract') or not self.contract_id:
    #         contract_ids = employee._get_contracts(date_from, date_to)
    #         if not contract_ids:
    #             return
    #         self.contract_id = self.env['hr.contract'].browse(contract_ids[0])
    #
    #     if not self.contract_id.struct_id:
    #         return
    #     self.struct_id = self.contract_id.struct_id
    #     if self.contract_id:
    #         contract_ids = self.contract_id.ids
    #     #computation of the salary input
    #     contracts = self.env['hr.contract'].browse(contract_ids)
    #     worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
    #     worked_days_lines = self.worked_days_line_ids.browse([])
    #     for r in worked_days_line_ids:
    #         worked_days_lines += worked_days_lines.new(r)
    #     self.worked_days_line_ids = worked_days_lines
    #
    #     input_line_ids = self.get_inputs(contracts, date_from, date_to)
    #     input_lines = self.input_line_ids.browse([])
    #     for r in input_line_ids:
    #         input_lines += input_lines.new(r)
    #     self.input_line_ids = input_lines
    #     return
    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        res = []

        # structure_ids = contracts.get_all_structures()
        # rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        # inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')

        for contract in contracts:
            primes = contract.hr_payroll_prime_ids
            # for input in inputs:
            #     input_data = {
            #         'name': input.name,
            #         'code': input.code,
            #         'contract_id': contract.id,
            #     }
            #     res += [input_data]
            for prime in primes:
                if prime.input_type_id.code == "TRSP":
                    if prime.montant_prime > 30000:
                        montant_imp = prime.montant_prime - 30000
                        input_type_obj = self.env['hr.payslip.input.type'].search([('code', '=', 'TRSP_IMP')])
                        input_type_id = None
                        if input_type_obj:
                            for input_type in input_type_obj:
                                input_type_id = input_type.id
                                print(input_type_id)
                            if input_type_id:
                                inputs = {
                                    'input_type_id': input_type_id,
                                    'code': "TRSP_IMP",
                                    'contract_id': contract.id,
                                    'amount': montant_imp,
                                }
                                res += [inputs]
                        inputs = {
                            'input_type_id': prime.input_type_id.id,
                            'code': prime.code,
                            'contract_id': contract.id,
                            'amount': 30000,
                        }
                        res += [inputs]
                    else:
                        inputs = {
                            'input_type_id': prime.input_type_id.id,
                            'code': prime.code,
                            'contract_id': contract.id,
                            'amount': prime.montant_prime,
                        }
                        res += [inputs]
                else:
                    # input_type_obj = self.env['hr.payslip.input.type'].search([('code', '=', 'TRSP_IMP')])
                    # input_type_id = None
                    # if input_type_obj:
                    #     for input_type in input_type_obj:
                    #         input_type_id = input_type.id
                    #     if input_type_id:
                    #         inputs = {
                    #             'input_type_id': input_type_id,
                    #             'code': "TRSP_IMP",
                    #             'contract_id': contract.id,
                    #             'amount': 0,
                    #         }
                    #         res += [inputs]
                    inputs = {
                        'input_type_id': prime.input_type_id.id,
                        'code': prime.code,
                        'contract_id': contract.id,
                        'amount': prime.montant_prime,
                    }
                    res += [inputs]
            emprunt = self.get_emprunt_montant_monthly(self.employee_id, date_from, date_to)
            if emprunt:
                input_type_obj = self.env['hr.payslip.input.type'].search([('code', '=', 'EMPRUNT')])
                input_type_id = None
                if input_type_obj:
                    for input_type in input_type_obj:
                        input_type_id = input_type.id
                inputs = {
                    'input_type_id': input_type_id,
                    'code': 'EMP',
                    'contract_id': contract.id,
                    'amount': emprunt.montant,
                }
                res += [inputs]
            return res
        return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        self.company_id = employee.company_id
        if not self.contract_id or self.employee_id != self.contract_id.employee_id:  # Add a default contract if not already defined
            contracts = employee._get_contracts(date_from, date_to)

            if not contracts or not contracts[0].structure_type_id.default_struct_id:
                self.contract_id = False
                self.struct_id = False
                return
            self.contract_id = contracts[0]
            self.struct_id = contracts[0].structure_type_id.default_struct_id

        payslip_name = self.struct_id.payslip_name or _('Salary Slip')
        self.name = '%s - %s - %s' % (
        payslip_name, self.employee_id.name or '', format_date(self.env, self.date_from, date_format="MMMM y"))

        if date_to > date_utils.end_of(fields.Date.today(), 'month'):
            self.warning_message = _(
                "This payslip can be erroneous! Work entries may not be generated for the period from %s to %s." %
                (date_utils.add(date_utils.end_of(fields.Date.today(), 'month'), days=1), date_to))
        else:
            self.warning_message = False

        #self.worked_days_line_ids = self._get_new_worked_days_lines()
        contract_ids = self.contract_id.ids
        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            print(r)
            # input_type = self.env['hr.payslip.input.type']
            # input_type.new(r)
            input_lines += input_lines.new(r)
        print(input_lines)
        self.input_line_ids = input_lines
        print(self.input_line_ids)

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day):
            day = fields.Date.to_string(datetime_day)
            return self.env['hr.leave'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('date_from', '<=', day),
                ('date_to', '>=', day)
            ], limit=1).holiday_status_id.name

        holidays_Obj = self.env['hr.leave']
        res = []
        attendances = {}
        leaves = []
        # fill only if the contract as a working schedule linked
        for contract in contracts:
            attendances = contract.employee_id.getWorkedDays(date_from, date_to, contract)
        #     day_from = fields.Datetime.from_string(date_from)
        #     day_to = fields.Datetime.from_string(date_to)
        #     leaves = holidays_Obj.computeHoldaysByType(day_from, day_to, contract)
        #     # print(leaves)
        # if leaves:
        #     total_leaves = 0
        #     for leave in leaves:
        #         total_leaves += leave['number_of_days']
        #     attendances['number_of_days'] -= total_leaves
        #     res += [attendances] + leaves
        # else:
            res += [attendances]
        return res

    def get_emprunt_montant_monthly(self, employee_id, date_from, date_to):
        ech_obj = self.env['hr.emprunt.loaning.line']
        if employee_id and date_from and date_to:
            lines = ech_obj.search([]).filtered(lambda l: l.loaning_id.employee_id == employee_id and l.statut_echeance == False)
            #print lines
            true_line = lines.filtered(lambda t: t.date_prevu >= date_from and t.date_prevu <= date_to)
            return true_line
        return False

    # @api.model
    # def _get_payslip_lines(self, contract_ids, payslip_id):
    #     def _sum_salary_rule_category(localdict, category, amount):
    #         if category.parent_id:
    #             localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
    #         localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
    #         return localdict
    #
    #     class BrowsableObject(object):
    #         def __init__(self, employee_id, dict, env):
    #             self.employee_id = employee_id
    #             self.dict = dict
    #             self.env = env
    #
    #         def __getattr__(self, attr):
    #             return attr in self.dict and self.dict.__getitem__(attr) or 0.0
    #
    #     class InputLine(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #         def sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""
    #                 SELECT sum(amount) as sum
    #                 FROM hr_payslip as hp, hr_payslip_input as pi
    #                 WHERE hp.employee_id = %s AND hp.state = 'done'
    #                 AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
    #                 (self.employee_id, from_date, to_date, code))
    #             return self.env.cr.fetchone()[0] or 0.0
    #
    #     class WorkedDays(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #         def _sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""
    #                 SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
    #                 FROM hr_payslip as hp, hr_payslip_worked_days as pi
    #                 WHERE hp.employee_id = %s AND hp.state = 'done'
    #                 AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
    #                 (self.employee_id, from_date, to_date, code))
    #             return self.env.cr.fetchone()
    #
    #         def sum(self, code, from_date, to_date=None):
    #             res = self._sum(code, from_date, to_date)
    #             return res and res[0] or 0.0
    #
    #         def sum_hours(self, code, from_date, to_date=None):
    #             res = self._sum(code, from_date, to_date)
    #             return res and res[1] or 0.0
    #
    #     class Payslips(BrowsableObject):
    #         """a class that will be used into the python code, mainly for usability purposes"""
    #
    #         def sum(self, code, from_date, to_date=None):
    #             if to_date is None:
    #                 to_date = fields.Date.today()
    #             self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
    #                         FROM hr_payslip as hp, hr_payslip_line as pl
    #                         WHERE hp.employee_id = %s AND hp.state = 'done'
    #                         AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
    #                         (self.employee_id, from_date, to_date, code))
    #             res = self.env.cr.fetchone()
    #             return res and res[0] or 0.0
    #
    #         def arrondi(self,montant):
    #             montant = Decimal(str(round(montant,0)))
    #             return float(montant)
    #
    #     #we keep a dict with the result because a value can be overwritten by another rule with the same code
    #     result_dict = {}
    #     rules_dict = {}
    #     worked_days_dict = {}
    #     inputs_dict = {}
    #     blacklist = []
    #     employee = self.employee_id
    #     contract = self.contract_id
    #     payslip = self.env['hr.payslip'].browse(payslip_id)
    #     for worked_days_line in payslip.worked_days_line_ids:
    #         worked_days_dict[worked_days_line.code] = worked_days_line
    #     for input_line in payslip.input_line_ids:
    #         inputs_dict[input_line.code] = input_line
    #
    #     categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
    #     inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
    #     worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
    #     payslips = Payslips(payslip.employee_id.id, payslip, self.env)
    #     rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
    #
    #     baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
    #     #get the ids of the structures on the contracts and their parent id as well
    #     contracts = self.env['hr.contract'].browse(contract_ids)
    #     structure_ids = contracts.get_all_structures()
    #     #get the rules of the structure and thier children
    #     rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
    #     #run the rules by sequence
    #     sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
    #     sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)
    #
    #     for contract in contracts:
    #         employee = contract.employee_id
    #         localdict = dict(baselocaldict, employee=employee, contract=contract)
    #         for rule in sorted_rules:
    #             key = rule.code + '-' + str(contract.id)
    #             localdict['result'] = None
    #             localdict['result_qty'] = 1.0
    #             localdict['result_rate'] = 100
    #             #check if the rule can be applied
    #             if rule._satisfy_condition(localdict) and rule.id not in blacklist:
    #                 #compute the amount of the rule
    #                 amount, qty, rate = rule._compute_rule(localdict)
    #                 #check if there is already a rule computed with that code
    #                 previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
    #                 #set/overwrite the amount computed for this rule in the localdict
    #                 tot_rule = amount * qty * rate / 100.0
    #                 localdict[rule.code] = tot_rule
    #                 rules_dict[rule.code] = rule
    #                 #sum the amount for its salary category
    #                 localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
    #                 #create/overwrite the rule in the temporary results
    #                 result_dict[key] = {
    #                     'salary_rule_id': rule.id,
    #                     'contract_id': contract.id,
    #                     'name': rule.name,
    #                     'code': rule.code,
    #                     'category_id': rule.category_id.id,
    #                     'sequence': rule.sequence,
    #                     'appears_on_payslip': rule.appears_on_payslip,
    #                     'condition_select': rule.condition_select,
    #                     'condition_python': rule.condition_python,
    #                     'condition_range': rule.condition_range,
    #                     'condition_range_min': rule.condition_range_min,
    #                     'condition_range_max': rule.condition_range_max,
    #                     'amount_select': rule.amount_select,
    #                     'amount_fix': rule.amount_fix,
    #                     'amount_python_compute': rule.amount_python_compute,
    #                     'amount_percentage': rule.amount_percentage,
    #                     'amount_percentage_base': rule.amount_percentage_base,
    #                     'register_id': rule.register_id.id,
    #                     'amount': amount,
    #                     'employee_id': contract.employee_id.id,
    #                     'quantity': qty,
    #                     'rate': rate,
    #                 }
    #             else:
    #                 #blacklist this rule and its children
    #                 blacklist += [id for id, seq in rule._recursive_search_of_rules()]
    #
    #     return list(result_dict.values())

    def _get_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(amount) as sum
                    FROM hr_payslip as hp, hr_payslip_input as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                    SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                    FROM hr_payslip as hp, hr_payslip_worked_days as pi
                    WHERE hp.employee_id = %s AND hp.state = 'done'
                    AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note IS NOT TRUE then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

            def rule_parameter(self, code):
                return self.env['hr.rule.parameter']._get_parameter_from_code(code, self.dict.date_to)

            def sum_category(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()

                self.env['hr.payslip'].flush(['credit_note', 'employee_id', 'state', 'date_from', 'date_to'])
                self.env['hr.payslip.line'].flush(['total', 'slip_id', 'category_id'])
                self.env['hr.salary.rule.category'].flush(['code'])

                self.env.cr.execute("""SELECT sum(case when hp.credit_note is not True then (pl.total) else (-pl.total) end)
                            FROM hr_payslip as hp, hr_payslip_line as pl, hr_salary_rule_category as rc
                            WHERE hp.employee_id = %s AND hp.state = 'done'
                            AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id
                            AND rc.id = pl.category_id AND rc.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

            @property
            def paid_amount(self):
                return self.dict._get_paid_amount()

            def arrondi(self, montant):
                montant = Decimal(str(round(montant, 0)))
                return float(montant)

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()

    @api.depends('contract_id')
    def _get_anciennete(self):
        anciennete={}
        #print self
        for payslip in self:
            if payslip.contract_id:
                d = payslip.contract_id.date_start
                print(type(d))
                date_debut = datetime.strptime(str(d), '%Y-%m-%d')
                today = datetime.now()
                nbre_year = 0
                nbre_mois= 0
                while date_debut <= today:
                    date_debut = date_debut + relativedelta.relativedelta(years=+1)
                    if date_debut > today:
                        date_debut = date_debut + relativedelta.relativedelta(years=-1)
                        break

                    nbre_year += 1
                while date_debut < today:
                    date_debut = date_debut + relativedelta.relativedelta(months=+1)
                    if date_debut > today:
                        break
                    nbre_mois += 1
                nbre_mois += payslip.contract_id.mois_report
                temp = nbre_mois - 12
                if temp >= 0:
                    nbre_year += 1
                    nbre_mois = temp
                payslip.update({
                        'payslip_an_anciennete':nbre_year + payslip.contract_id.an_report,
                        'payslip_mois_anciennete':nbre_mois,
                    })
            else:
                payslip.update({
                        'payslip_an_anciennete':0,
                        'payslip_mois_anciennete':0,
                    })

    @api.onchange('employee_id', 'contract_id')
    def getAnciennete(self):
        for payslip in self:
            print(payslip.date_from)

    def _get_last_payslip(self):
        dic = {}
        res = []
        slips = self.employee_id.slip_ids
        if len(slips) == 1:
            self.last_payslip = False
        else:
            for slip in slips:
                if slip.id < self.id:
                    res.append(slip)
                    if len(res) >= 1:
                        dernier = res[len(res)-1]
                        payslip = self.self.env['hr.payslip'].search([('id','=',dernier.id)])
                        self.last_payslip = payslip.id

    def _get_total_gain(self):
        res = {}
        for line in self.line_ids:
            if line.code == 'BRUT':
                self.total_gain = line.total
        return res

    def _get_retenues(self):
        for line in self.line_ids:
            if line.code == 'RET':
                self.total_retenues =line.total

    @api.depends('line_ids.total')
    def _get_net_paye(self):
        for slip in self:
            for line in slip.line_ids:
                if line.code == "NET":
                    slip.update({'net_paie': line.total})

    def get_amountbycode(self, code, line_ids):
        amount = 0
        if line_ids:
            for line in line_ids:
                if line.code == code:
                    return line.amount
        return 0
        # for payslip in self :
        #     if code :
        #         line = payslip.
        #         if line :
        #             print line
        #             amount = line.amount
        #     return amount

    def cumulBYCode(self, employee_id, code, date_from, date_to):
        slip_obj = self.env['hr.payslip']
        payslips = slip_obj.search([('date_from', '>=', date_from),
                                    ('date_to', '<', date_to),
                                    ('employee_id', '=', employee_id)])
        #print payslips
        total_amount = 0
        for slip in payslips:
            result = slip.get_amountbycode(code, slip.line_ids)
            total_amount += result
        return total_amount

    def get_cumul_base_impot(self):
        year = datetime.now().year
        d = self.date_from
        date_temp = datetime.strptime(str(d), '%Y-%m-%d')
        first_day = str(date_temp + relativedelta.relativedelta(month=1, day=1))[:10]
        for payslip in self:
            total = payslip.cumulBYCode(payslip.employee_id.id, 'BASE_IMP', first_day, payslip.date_from)
            # total = payslip.cumulBYCode('BASE_IMP', first_day, self.date_from)[0]
            # total_cn= payslip.cumulBYCode('CN', first_day, self.date_from)[0]
            # print total
            payslip.update({
                'cumul_base_impot': payslip.cumulBYCode(payslip.employee_id.id, 'BASE_IMP', first_day, payslip.date_from),
                'cumul_cn': payslip.cumulBYCode(payslip.employee_id.id, 'CN', first_day, payslip.date_from),
                'cumul_worked_days': payslip.cumulBYCode(payslip.employee_id.id, 'TWDAYS', first_day, payslip.date_from),
                'cumul_igr':payslip.cumulBYCode(payslip.employee_id.id, 'IGR', first_day, payslip.date_from)
            })

    def get_somme_rubrique(self, code):
        annee = self.date_to[2:4]
        for payslip in self:
            cpt = 0
            for line in self.line_ids:
                if line.salary_rule_id.code == code and self.date_to >= self.date_to and payslip.date_to[2:4] == annee:
                    cpt += line.total
            result = format_amount.manageSeparator(cpt)
            return result

    def get_amount_rubrique(self, rubrique):
        line_ids = self.line_ids
        total = 0
        for line in line_ids:
            if line.code == rubrique:
                total = line.total
        result = format_amount.manageSeparator(total)
        return result

    def getTauxByCode(self,rubrique):
        taux = 0.0
        lines = self.line_ids
        for line in lines:
            if line.code == rubrique:
                taux = line.rate
        return taux

    def getLineByCode(self, code):
        lines = self.line_ids
        for line in lines:
            if line.code == code:
                return line

    def _get_total(self):
        self.worked_days= 0.0

    option_salaire = fields.Selection([('mois','Mensuel'),('jour','Journalier'),('heure','horaire')],
                         'Option salaire', select=True, readonly=False)
    reference_reglement = fields.Char('Reférence',size=60,required=False)
    payslip_an_anciennete = fields.Integer("Nombre d'année", compute=_get_anciennete)
    payslip_mois_anciennete = fields.Integer("Nombre de mois", compute=_get_anciennete)
    payment_method = fields.Selection([('espece','Espèces'),('virement','Virement bancaire'),('cheque','Chèques')],
                      string='Moyens de paiement',required=False,deafult='espece')
    last_payslip = fields.Many2one("hr.payslip",compute=_get_last_payslip,store=True,string="Dernier bulletin")
    total_gain = fields.Integer(compute=_get_total_gain,store=True)
    total_retenues = fields.Integer(compute=_get_retenues,store=True)
    net_paie = fields.Integer(compute=_get_net_paye,store=True)
    cumul_base_impot = fields.Float('Cumul base impôt', compute=get_cumul_base_impot)
    cumul_cn = fields.Float('Cumul CN payé', compute=get_cumul_base_impot)
    cumul_igr = fields.Float('Cumul IGR payé', compute=get_cumul_base_impot)
    cumul_worked_days = fields.Float('Cumul jours travaillés', compute=get_cumul_base_impot)
    worked_days = fields.Float('Total jours travaillés', compute=_get_total)
    allocation = fields.Boolean('Allocation', help="Cocher pour faire apparaître l'allocation sur le bulletin de l'employé")
    retraite = fields.Boolean('Retraité', help="Cocher pour faire apparaître l'indemnité de retraite sur le bulletin de l'employé")
    fin_ccd = fields.Boolean('Fin CDD', help="Cocher pour faire apparaître l'indemnité de fin de CDD sur le bulletin de l'employé")

    def get_list_employee(self):
        list_employees = []
        hc_obj = self.env['hr.contract']
        hcontract_ids = hc_obj.search([('state', '=', 'in_progress')])
        self.cr.execute("SELECT employee_id FROM hr_contract WHERE id=ANY(%s)", (hcontract_ids,))
        results = self.cr.fetchall()
        if results:
            list_employees = [res[0] for res in results]
            return {'domain': {'employee_id': [('id', 'in', list_employees)]}}

    def get_net_paye(self):
        montant = 0
        for line in self.line_ids:
            if line.code == "NET":
                montant = line.total
        return montant


class hr_payslip_line(models.Model):
    '''
    Payslip Line
    '''

    _name = 'hr.payslip.line'
    _inherit = 'hr.payslip.line'

    def _calculate_total(self):
        if not self:
            return {}
        res = {}
        for line in self:
            self.total = float(line.quantity) * line.amount * line.rate / 100

    amount = fields.Float('Amount',digits=(16, 0))
    quantity = fields.Float('Quantity', digits=(16, 0))
    rate = fields.Float(string='Rate (%)', digits=(16,2), default=100.0)
    total = fields.Float(compute='_compute_total', string='Total', digits=(16,0), store=True)


class hr_salary_rule(models.Model):
    _inherit='hr.salary.rule'
    _order='sequence'

    struct_id = fields.Many2one('hr.payroll.structure', string="Salary Structure", required=False)


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    work_entry_type_id = fields.Many2one('hr.work.entry.type', string='Type', required=False,
                                         help="The code that can be used in the salary rules")





