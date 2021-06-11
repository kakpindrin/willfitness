# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons import decimal_precision as dp

class HrPayrollStructure(models.Model):
    """
    Salary structure used to defined
    - Basic
    - Allowances
    - Deductions
    """
    _inherit = 'hr.payroll.structure'
    _description = 'Salary Structure'

    # @api.model
    # def _get_default_rule_ids(self):
    #     return [
    #         (0, 0, {
    #             'name': 'Basic Salary',
    #             'sequence': 1,
    #             'code': 'BASIC',
    #             'category_id': self.env.ref('hr_payroll.BASIC').id,
    #             'condition_select': 'none',
    #             'amount_select': 'code',
    #             'amount_python_compute': 'result = payslip.paid_amount',
    #         }),
    #         (0, 0, {
    #             'name': 'Gross',
    #             'sequence': 100,
    #             'code': 'GROSS',
    #             'category_id': self.env.ref('hr_payroll.GROSS').id,
    #             'condition_select': 'none',
    #             'amount_select': 'code',
    #             'amount_python_compute': 'result = categories.BASIC + categories.ALW',
    #         }),
    #         (0, 0, {
    #             'name': 'Net Salary',
    #             'sequence': 200,
    #             'code': 'NET',
    #             'category_id': self.env.ref('hr_payroll.NET').id,
    #             'condition_select': 'none',
    #             'amount_select': 'code',
    #             'amount_python_compute': 'result = categories.BASIC + categories.ALW + categories.DED',
    #         })
    #     ]

    rule_ids = fields.Many2many('hr.salary.rule', 'struct_id',string='Salary Rules')

    # @api.model
    # def _get_parent(self):
    #     return self.env.ref('hr_payroll_community.structure_base', False)
    #
    # parent_id = fields.Many2one('hr.payroll.structure', string='Parent', default=_get_parent)
    # children_ids = fields.One2many('hr.payroll.structure', 'parent_id', string='Children', copy=True)
    # rule_ids = fields.Many2many('hr.salary.rule', 'hr_structure_salary_rule_rel', 'struct_id', 'rule_id', string='Salary Rules')
    #
    #
    # def get_all_rules(self):
    #     """
    #     @return: returns a list of tuple (id, sequence) of rules that are maybe to apply
    #     """
    #     all_rules = []
    #     for struct in self:
    #         all_rules += struct.rule_ids._recursive_search_of_rules()
    #     return all_rules
    #
    # def _get_parent_structure(self):
    #     parent = self.mapped('parent_id')
    #     if parent:
    #         parent = parent._get_parent_structure()
    #     return parent + self