# -*- encoding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class Hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    base_prorata = fields.Integer()
    sursa_prorata = fields.Integer()
    panc_prorata = fields.Integer()
    repr_prorata = fields.Integer()
    pres_prorata = fields.Integer()
    indml_prorata = fields.Integer()
    carbu_prorata = fields.Integer()
    trsp_imp_prorata = fields.Integer()
    trsp_prorata = fields.Integer()
    is_prorata = fields.Boolean('Bulletin calcule au prorata')


class Hhpayslip_Prorata(models.TransientModel):
    _name = 'hr.payslip.prorata'

    prorata_number = fields.Integer('Nombre de jour')

    def get_prorato_amount(self, line, code, prorata_number):
        if prorata_number <= 0:
            raise Warning(_('Veullez mettre une bonne valeur'))
        for l in line:
            if l.code == code:
                temp = (prorata_number * l.total) / 30
                amount = round(temp)
                return amount

    def compute_prorata(self):
        payslip = self.env['hr.payslip'].browse(self._context.get('active_id'))
        hr_payslip_line = payslip.line_ids
        #details_by_salary_rule_category = payslip.details_by_salary_rule_category

        base_prorata = self.get_prorato_amount(hr_payslip_line, 'BASE', self.prorata_number)
        payslip.write({'base_prorata': base_prorata})

        sursa_prorata = self.get_prorato_amount(hr_payslip_line, 'SURSA', self.prorata_number)
        payslip.write({'sursa_prorata': sursa_prorata})

        pres_prorata = self.get_prorato_amount(hr_payslip_line, 'PRES', self.prorata_number)
        payslip.write({'pres_prorata': pres_prorata})

        panc_prorata = self.get_prorato_amount(hr_payslip_line, 'PANC', self.prorata_number)
        payslip.write({'panc_prorata': panc_prorata})

        indml_prorata = self.get_prorato_amount(hr_payslip_line, 'INDML', self.prorata_number)
        payslip.write({'indml_prorata': indml_prorata})

        carbu_prorata = self.get_prorato_amount(hr_payslip_line, 'CARBU', self.prorata_number)
        payslip.write({'carbu_prorata': carbu_prorata})

        trsp_prorata = self.get_prorato_amount(hr_payslip_line, 'TRSP', self.prorata_number)
        payslip.write({'trsp_prorata': trsp_prorata})

        repr_prorata = self.get_prorato_amount(hr_payslip_line, 'REPR', self.prorata_number)
        payslip.write({'repr_prorata': repr_prorata})

        trsp_imp_prorata = self.get_prorato_amount(hr_payslip_line, 'TRSP_IMP', self.prorata_number)
        payslip.write({'trsp_imp_prorata': trsp_imp_prorata})

        if payslip.is_prorata is False:
            raise Warning(_('Veullez cocher la case Bulletin calcule au prorata'))
        prorata = float(self.prorata_number)
        work_day_obj = self.env['hr.work.entry.type'].search([('code', '=', 'PRORATA')])
        work_day_id = None
        for work in work_day_obj:
            work_day_id = work.id
        payslip.write({'worked_days_line_ids':
                           [(0, 0, {
                                'work_entry_type_id': work_day_id,
                                'name': _("Prorata de jours travaillés"),
                                'sequence': 1,
                                'code': 'PRORATA',
                                'number_of_days': prorata,
                                'number_of_hours': (prorata * 173.33) / 30,
                                'contract_id': payslip.contract_id.id,
                                    }
                             )
                            ]})
        payslip.compute_sheet()
