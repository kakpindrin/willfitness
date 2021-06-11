# -*- coding:utf-8 -*-
import logging

from odoo import models, api, fields, exceptions, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def getWorkedDays(self, date_from, date_to, contract):
        #att_obj= self.env['hr.attendance']
        hours = 0
        # if self.type in ('j', 'h'):
        #     self.env.cr.execute("SELECT id, check_in, check_out FROM hr_attendance WHERE (check_in"
        #            " between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND"
        #             "(check_out between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))"
        #                " AND employee_id=%s",(date_from,date_to,date_from,date_to,self.id))
        #     for x in self.env.cr.dictfetchall():
        #         date_start = fields.Datetime.from_string(x['check_in'])
        #         date_end = fields.Datetime.from_string(x['check_out'])
        #         tmp = relativedelta(date_end, date_start)
        #         hours += tmp.hours
        #     days = hours/8
        #     return {
        #         'name': _("Nombre de jours travaillés"),
        #         'sequence': 1,
        #         'code': 'WORK100',
        #         'number_of_days': days,
        #         'number_of_hours': hours,
        #         'contract_id': contract.id,
        #     }
        # else:
        work_day_obj = self.env['hr.work.entry.type'].search([('code', '=', 'WORK100')])
        work_day_id = None
        for work in work_day_obj:
            work_day_id = work.id
        attendances = {
         'work_entry_type_id': work_day_id,
         'name': _("Normal Working Days paid at 100%"),
         'sequence': 1,
         'code': 'WORK100',
         'number_of_days': 30,
         'number_of_hours': 173.33,
         'contract_id': contract.id,
        }
        return attendances

    date_retour_conge = fields.Date(string="Date de rétour congé")
    date_depart_conge = fields.Date(string="Date de départ congé")
    allocation_conge = fields.Integer(store=True, readonly=True, compute='_get_allocation_conge', digits_compute=dp.get_precision('Account'),
                                      string='Allocation congé')
    allocation_conge2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Allocation congé 2')
    jour_conge = fields.Float(store=True, readonly=True, compute='_get_jour_conge', string='Jour congé')
    indemnite_licencement = fields.Integer(store=True, readonly=True, string='Indemnite licencement', compute='_get_indemnite_licencement')
    indemnite_licencement2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Indemnite licencement2')
    indemnite_fin_cdd = fields.Integer(string='Indemnite fin CDD', store=True, readonly=True, compute='_get_indemnite_fin_cdd')
    indemnite_fin_cdd2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Indemnite fin cdd')
    indemnite_retraite = fields.Integer(string='Indemnite retraite', store=True, readonly=True, compute='_get_indemnite_licencement')
    indemnite_retraite2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Indemnite retraite')
    indemnite_deces = fields.Integer(string='Indemnite décès', store=True, readonly=True, compute='_get_indemnite_deces')
    indemnite_deces2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Indemnite décès')
    conge_paye = fields.Boolean('Congé payé')
    debut_rupture = fields.Date('Date rupture')
    debut_decompte = fields.Date('Début décompte')
    is_retraite = fields.Boolean('Retraité')
    is_deces = fields.Boolean('Décès')
    notification_date = fields.Date(compute='_get_end_contract')
    contract_id = fields.Many2one('hr.contract')
    contracts = fields.Many2one('hr.contract', default=lambda self: self.env['hr.contract'].search([('employee_id', '=', self.id)]))
    date_end = fields.Date(related='contract_id.date_end', store=True, domain=[('type_id.code', '=', 'CDD')])
    contract_type = fields.Char(related='contract_id.type_id.code', store=True, domain=[('type_id.code', '=', 'CDD')])
    nombre_jour_attribue = fields.Integer(store=True, readonly=True, compute='_compute_number_of_days_allocated', string='Nombre de jour(s) attribué(s)')
    taken_days_number = fields.Integer(store=True, readonly=True, compute='_get_taken_days', string='Nombre de jour(s) pris')
    taken_days_number_year = fields.Integer(string='Nombre de jour(s) pris par an')
    conge_exceptionnel = fields.Integer(store=True, readonly=True, compute='_compute_conge_exceptionnel', string='Nombre Congés Exceptionnels pris')
    conge_non_exceptionnel = fields.Integer(store=True, readonly=True, compute='_compute_conge_non_exceptionnel',string='Nombre Congés Non Exceptionnels pris')
    montant_alloue = fields.Integer(store=True, readonly=True, compute='_get_taken_days', digits_compute=dp.get_precision('Account'),string='Montant congé payé')
    ecart_conge = fields.Integer(store=True, readonly=True, compute='_get_taken_days', digits_compute=dp.get_precision('Account'),string='Ecart de congé')
    ecart_conge2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Ecart de congé')
    cmu_employe = fields.Integer(string='CMU employé', store=True, readonly=True, compute='_compute_cmu_amount', digits_compute=dp.get_precision('Account'))
    cmu_employe2 = fields.Integer(readonly=True, digits_compute=dp.get_precision('Account'), string='CMU employé')
    cmu_employeur = fields.Integer(store=True, readonly=True, compute='_compute_cmu_amount', digits_compute=dp.get_precision('Account'),string='CMU employeur')
    cmu_employeur2 = fields.Integer(readonly=True, digits_compute=dp.get_precision('Account'), string='CMU employeur')
    prime_gratification = fields.Integer(store=True, readonly=True, compute='_compute_prime_gratification',
                                       digits_compute=dp.get_precision('Account'), string='Prime gratification')
    prime_gratification2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Prime gratification')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    #prime_trsp = fields.Integer(compute='_get_prime_trsp', digits_compute=dp.get_precision('Account'),
    #                             string='Prime de transport')
    prime_trsp2 = fields.Integer(digits_compute=dp.get_precision('Account'), string='Prime de transport')
    prime_idml = fields.Integer(digits_compute=dp.get_precision('Account'), string='Prime indemnité de logement')
    prime_assur = fields.Integer(digits_compute=dp.get_precision('Account'), string="Prime d'assurance")
    prime_fonct = fields.Integer(digits_compute=dp.get_precision('Account'), string="Prime de fonction")
    prime_resp = fields.Integer(digits_compute=dp.get_precision('Account'), string="Prime de responsabilité")
    prime_carbu = fields.Integer(digits_compute=dp.get_precision('Account'), string="Prime de caburant")
    prime_gratif = fields.Integer(digits_compute=dp.get_precision('Account'), string="Prime de gratification")
    prime_avtgn = fields.Integer(digits_compute=dp.get_precision('Account'), string="Prime avantage en nature")
    is_prime_trsp = fields.Boolean('Is prime', default=False)
    is_prime_avtgn = fields.Boolean('Is avtn', default=False)
    is_prime_idml = fields.Boolean('Is idml', default=False)
    is_prime_assur = fields.Boolean('Is assur', default=False)
    is_prime_fonct = fields.Boolean('Is fonct', default=False)
    is_prime_resp = fields.Boolean('Is resp', default=False)
    is_prime_carbu = fields.Boolean('Is carbu', default=False)
    is_prime_gratif = fields.Boolean('Is gratif', default=False)
    montant_moyen_mensuel = fields.Float(store=True, readonly=True, compute='_get_montant_by_periode_reference', digits_compute=dp.get_precision('Account'), string="Montant mensuel moyen")
    montant_moyen_journalier = fields.Float(store=True, readonly=True, compute='_get_montant_moyen_journalier', digits_compute=dp.get_precision('Account'), string="Montant journalier")

    demission_by_dibi = fields.Boolean(string="Démission", default=False)
    montant_preavis_by_dibi = fields.Float(string='Montant Préavis', default=0.0)
    # @api.onchange('date_embauche')
    # def on_change_date_embauche(self):
    #     if self.date_retour_conge:
    #         if self.date_retour_conge < self.date_embauche:
    #             self.date_retour_conge = self.date_embauche
    #     else:
    #         self.date_retour_conge = self.date_embauche

    def main_function(self):
        _logger.info("Fonction principale pour le calcul des paramètres")
        employee_ids = self.env['hr.employee'].search([])
        print(employee_ids)
        for emp in employee_ids:
            print(emp.id)
            emp.compute_all_function(emp)

    def compute_all_function(self, emp):
        _logger.info("Fonction après chaque employé")
        emp._get_allocation_conge()
        emp._compute_number_of_days_allocated()
        emp._compute_conge_exceptionnel()
        emp._compute_conge_non_exceptionnel()
        emp._get_taken_days()
        emp._get_jour_conge()
        emp._get_indemnite_licencement()
        emp._get_indemnite_fin_cdd()
        emp._get_indemnite_deces()
        emp._get_end_contract()
        emp._compute_cmu_amount()
        emp._compute_prime_gratification()
        emp._get_montant_by_periode_reference()
        emp._get_montant_moyen_journalier()

    def _est_em_funct(self):
        print('la fonction pour chaque emplye')

    def get_montant_by_periode_reference(self):
        slip_obj = self.env['hr.payslip']
        montant = 0
        for emp in self:
            if emp.contract_id.date_start and not emp.date_retour_conge:
                payslip = slip_obj.search([('employee_id', '=', emp.id), ('date_from', '>=', emp.contract_id.date_start)])
                # payslip = slip_obj.browse(slip_ids)
                number = len(payslip)
                print(number)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    SMM = round(montant)
                    return SMM
            elif emp.date_retour_conge and emp.contract_id.date_start and not emp.debut_rupture:
                print(emp.date_retour_conge)
                payslips = slip_obj.search([('employee_id', '=', emp.id), ('date_from', '>=', emp.date_retour_conge)])
                payslip = slip_obj.browse(payslips)
                number = len(payslip)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    SMM = round(montant)
                    return SMM
            elif emp.contract_id.date_start and emp.contract_id.date_end:
                print(emp.date_retour_conge)
                payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                   ('date_from', '>=', emp.contract_id.date_start),
                                                   ('date_from', '<=', emp.contract_id.date_end)])
                payslip = slip_obj.browse(payslips)
                number = len(payslip)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    SMM = round(montant)
                    return SMM
            elif emp.date_retour_conge and emp.debut_rupture:
                payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                    ('date_from', '>=', emp.date_retour_conge),
                                                    ('date_from', '<=', emp.debut_rupture)])
                payslip = slip_obj.browse(payslips)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    SMM = round(montant)
                    return SMM

    def _get_montant_by_periode_reference(self):
        for emp in self:
            res = emp.get_montant_by_periode_reference()
            emp.montant_moyen_mensuel = res
            return res

    def get_montant_moyen_journalier(self):
        slip_obj = self.env['hr.payslip']
        montant = 0
        for emp in self:
            emp_id = emp.ids[0]
            if emp.contract_id.date_start and not emp.date_retour_conge:
                payslip = slip_obj.search([('employee_id', '=', emp_id), ('date_from', '>=', emp.contract_id.date_start)])
                # payslip = slip_obj.browse(slip_ids)
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ
            elif emp.date_retour_conge and emp.contract_id.date_start and not emp.debut_rupture:
                payslips = slip_obj.search([('employee_id', '=', emp_id), ('date_from', '>=', emp.date_retour_conge)])
                payslip = slip_obj.browse(payslips)
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ
            elif emp.contract_id.date_start and emp.contract_id.date_end:
                print(emp.date_retour_conge)
                payslips = slip_obj.search([('employee_id', '=', emp_id),
                                                   ('date_from', '>=', emp.contract_id.date_start),
                                                   ('date_from', '<=', emp.contract_id.date_end)])
                payslip = slip_obj.browse(payslips)
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ
            elif emp.date_retour_conge and emp.debut_rupture:
                payslips = slip_obj.search([('employee_id', '=', emp_id),
                                                    ('date_from', '>=', emp.date_retour_conge),
                                                    ('date_from', '<=', emp.debut_rupture)])
                # payslip = slip_obj.browse(payslips)
                if payslips != 0:
                    worked_days_number = list()
                    for slip in payslips:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslips:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ

    def _get_montant_moyen_journalier(self):
        res = 0
        for emp in self:
            res = emp.get_montant_moyen_journalier()
            emp.montant_moyen_journalier = res
        return res

    def _compute_prime_gratification(self):
        for rec in self:
            emp_id = rec.ids[0]
            employee = rec.env['hr.employee'].search([('id', '=', emp_id)])
            res = float(rec.contract_id.taux)
            t = float(res / 100)
            if rec.contract_id.date_start and rec.contract_id.date_end:
                payslip = rec.env['hr.payslip'].search([('employee_id', '=', rec.id),
                                                        ('date_from', '>=', rec.contract_id.date_start),
                                                        ('date_from', '<=', rec.contract_id.date_end)])
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    nwd = sum(worked_days_number)
                    rec.prime_gratification = t * nwd / 360
                    prime = t * nwd / 360
                    employee.write({'prime_gratification2': prime})
            if rec.contract_id.date_start and not rec.contract_id.date_end:
                payslip = rec.env['hr.payslip'].search([('employee_id', '=', rec.id),
                                                        ('date_from', '>=', rec.contract_id.date_start)])
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    nwd = sum(worked_days_number)
                    rec.prime_gratification = t * nwd / 360
                    prime = t * nwd / 360
                    employee.write({'prime_gratification2': prime})

    def _compute_cmu_amount(self):
        for rec in self:
            emp_id = rec.ids[0]
            employee = rec.env['hr.employee'].search([('id', '=', emp_id)])
            if employee:
                number_cmu = 1
                enfants_ids = employee.enfants_ids
                if len(enfants_ids) != 0:
                    for enfant in enfants_ids:
                        date_ref = datetime.now().strftime('%Y-%m-%d')
                        date_naiss = enfant.date_naissance
                        temp1 = datetime.strptime(date_ref, '%Y-%m-%d')
                        temp2 = datetime.strptime(str(date_naiss), '%Y-%m-%d')
                        age = abs(relativedelta(temp2, temp1).years)
                        if 0 < age <= 21:
                            number_cmu += 1
                    cmu = 1000 * number_cmu
                    cmu_employe2 = (cmu * 50) / 100
                    cmu_employeur2 = (cmu * 50) / 100
                    rec.cmu_employe = cmu_employe2
                    rec.cmu_employeur = cmu_employeur2
                    employee.write({'cmu_employe2': cmu_employe2})
                    employee.write({'cmu_employeur2': cmu_employeur2})
                else:
                    cmu = 1000 * number_cmu
                    cmu_employe2 = (cmu * 50) / 100
                    cmu_employeur2 = (cmu * 50) / 100
                    rec.cmu_employe = cmu_employe2
                    rec.cmu_employeur = cmu_employeur2
                    employee.write({'cmu_employe2': cmu_employe2})
                    employee.write({'cmu_employeur2': cmu_employeur2})
            else:
                rec.cmu_employe = 0

    def _compute_conge_exceptionnel(self):
        for rec in self:
            hr_holidays = rec.env['hr.leave'].search([('employee_id', '=', rec.id), ('state', '=', 'validate'),
                                                         ('conge_non_exceptionne', '=', False)]).filtered(
                lambda r: r.holiday_status_id.code != 'CONG')
            if hr_holidays:
                days = 0
                for holy in hr_holidays:
                    days += holy.number_of_days
                rec.conge_exceptionnel = days
            else:
                rec.conge_exceptionnel = 0

    def _compute_conge_non_exceptionnel(self):
        for rec in self:
            hr_holidays = rec.env['hr.leave'].search(
                [('employee_id', '=', rec.ids[0]), ('state', '=', 'validate'), ('conge_non_exceptionne', '=', True)]).filtered(
                lambda r: r.holiday_status_id.code == 'CONG_NON_EXCEPTIONNEL')
            if hr_holidays:
                days = 0
                for holy in hr_holidays:
                    days += holy.number_of_days
                rec.conge_non_exceptionnel = days
            else:
                rec.conge_non_exceptionnel = 0

    def _compute_number_of_days_allocated(self):
        for data in self:
            hr_holidays = data.env['hr.leave.allocation'].search([('employee_id', '=', data.ids[0]), ('state', '=', 'validate')]).filtered(
                lambda r: r.holiday_status_id.code == 'CONG')
            print('hr_holidays', hr_holidays)
            #hr_holidays = data.env['hr.leave.allocation'].search([('employee_id', '=', data.id)])
            if hr_holidays:
                number_of_days_temp = 0
                for holy in hr_holidays:
                    number_of_days_temp += holy.number_of_days
                data.nombre_jour_attribue = number_of_days_temp
            else:
                data.nombre_jour_attribue = 0

    def _get_taken_days(self):
        for rec in self:
            employee = rec.env['hr.employee'].search([('id', '=', rec.ids[0])])
            hr_holidays = rec.env['hr.leave'].search([('employee_id', '=', rec.ids[0]), ('state', '=', 'validate')]).filtered(
                lambda r: r.holiday_status_id.code == 'CONG')
            days = rec.conge_exceptionnel
            if hr_holidays:
                number_of_days_temp = 0
                montant_conge = 0
                for holy in hr_holidays:
                    montant_conge += holy.montant_conge
                    number_of_days_temp += holy.number_of_days
                rec.taken_days_number = number_of_days_temp + ((days - 10) if days > 10 else 0)
                rec.montant_alloue = montant_conge
                rec.ecart_conge = rec.allocation_conge - rec.montant_alloue
                ecart_conge2 = rec.allocation_conge - rec.montant_alloue
                employee.write({'ecart_conge2': ecart_conge2})
            else:
                rec.taken_days_number = 0
                rec.montant_alloue = 0
                rec.ecart_conge = 0

    def _get_end_contract(self):
        self.ensure_one()
        for emp in self:
            date_end = emp.env['hr.contract'].search(
                [('employee_id', '=', emp.id), ('type_id.code', '=', 'CDD')]).date_end
            if date_end is not False:
                emp.notification_date = date_end

    def _get_indemnite_licencement(self):
        for emp in self:
            print('oh oh oh', emp.id)
            emp_id = emp.ids[0]
            slip_obj = emp.env['hr.payslip'].search([])
            employee = emp.env['hr.employee'].search([('id', '=', emp_id)])
            
            #DÉBUT CODE DIBI À PLACER POUR LES DÉMISSIONS
            if not emp.demission_by_dibi:
                if emp.debut_decompte and emp.debut_rupture and not emp.is_retraite:
                    payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                ('date_from', '>=', emp.debut_decompte),
                                                ('date_from', '<=', emp.debut_rupture)])
                    payslips_number = len(payslips)
                    montant_net = 0.0
                    montant_avt = 0
                    for slip in payslips:
                        line_ids = slip.line_ids
                        input_line_ids = emp.env['hr.payslip.input'].search([('payslip_id', '=', slip.id)])
                        montant = sum(line.total for line in line_ids if line.code == 'BASE_IMP')
                        # avantage = sum(avt.amount for avt in input_line_ids if avt.code == 'AVTGN')
                        montant_net += montant
                        # montant_avt += avantage
                    SNMM = montant_net / payslips_number if payslips_number else 0
                    _logger.info("_get_indemnite_licencement %s", SNMM)
                    if emp.contract_id:
                        year = emp.contract_id.an_anciennete
                        print('year', year)
                        if 0 <= year <= 6:
                            amount = (SNMM * 30) / 100
                            emp.indemnite_licencement = amount
                            #emp.indemnite_licencement = 0
                            indemnite_licencement2 = (SNMM * 30) / 100
                            employee.write({'indemnite_licencement2': indemnite_licencement2})
                            employee.write({'indemnite_retraite2': 0.0})
                        elif 6 <= year <= 10:
                            #emp.indemnite_licencement = 0
                            emp.indemnite_licencement = ((SNMM * 30) / 100) + ((SNMM * 35) / 100)
                            indemnite_licencement2 = ((SNMM * 30) / 100) + ((SNMM * 35) / 100)
                            employee.write({'indemnite_licencement2': indemnite_licencement2})
                            employee.write({'indemnite_retraite2': 0.0})
                        elif 10 < year:
                            #emp.indemnite_licencement = 0
                            emp.indemnite_licencement = ((SNMM * 30) / 100) + ((SNMM * 35) / 100) + ((SNMM * 40) / 100)
                            indemnite_licencement2 = ((SNMM * 30) / 100) + ((SNMM * 35) / 100) + ((SNMM * 40) / 100)
                            employee.write({'indemnite_licencement2': indemnite_licencement2})
                            employee.write({'indemnite_retraite2': 0.0})
                if emp.debut_decompte and emp.debut_rupture and emp.is_retraite:
                    payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                ('date_from', '>=', emp.debut_decompte),
                                                ('date_from', '<=', emp.debut_rupture)])
                    payslips_number = len(payslips)
                    print('he he')
                    montant_net = 0
                    montant_avt = 0
                    for slip in payslips:
                        line_ids = slip.line_ids
                        input_line_ids = emp.env['hr.payslip.input'].search([('payslip_id', '=', slip.id)])
                        montant = sum(line.total for line in line_ids if line.code == 'BASE_IMP')
                        # avantage = sum(avt.amount for avt in input_line_ids if avt.code == 'AVTGN')
                        montant_net += montant
                        # montant_avt += avantage
                    SNMM = montant_net / payslips_number if payslips_number else 0
                    _logger.info("_get_indemnite_licencement %s", SNMM)
                    if emp.contract_id:
                        year = emp.contract_id.an_anciennete
                        if 0 <= year <= 6:
                            emp.indemnite_retraite = (SNMM * 30) / 100
                            indemnite_retraite2 = (SNMM * 30) / 100
                            employee.write({'indemnite_retraite2': indemnite_retraite2})
                            employee.write({'indemnite_licencement2': 0.0})
                        elif 6 <= year <= 10:
                            emp.indemnite_retraite = ((SNMM * 30) / 100) + ((SNMM * 35) / 100)
                            indemnite_retraite2 = ((SNMM * 30) / 100) + ((SNMM * 35) / 100)
                            employee.write({'indemnite_retraite2': indemnite_retraite2})
                            employee.write({'indemnite_licencement2': 0.0})
                        elif 10 < year:
                            emp.indemnite_retraite = ((SNMM * 30) / 100) + ((SNMM * 35) / 100) + ((SNMM * 40) / 100)
                            indemnite_retraite2 = ((SNMM * 30) / 100) + ((SNMM * 35) / 100) + ((SNMM * 40) / 100)
                            employee.write({'indemnite_retraite2': indemnite_retraite2})
                            employee.write({'indemnite_licencement2': 0.0})
                if not emp.debut_decompte and not emp.debut_rupture and not emp.is_retraite:
                    emp.indemnite_licencement = 0
                    emp.indemnite_retraite = 0
            #FIN CODE DIBI À PLACER POUR LES DÉMISSIONS

    def _get_indemnite_fin_cdd(self):
        montant = 0
        for emp in self:
            emp_id = emp.ids[0]
            employee = emp.env['hr.employee'].search([('id', '=', emp_id)])
            if emp.contract_id.date_start and emp.contract_id.date_end:
                smm = emp.env['hr.employee'].search([('id', '=', employee.id)]).montant_moyen_mensuel
                payslip = emp.env['hr.payslip'].search([('employee_id', '=', emp_id),
                                                        ('date_from', '>=', emp.contract_id.date_start),
                                                        ('date_from', '<=', emp.contract_id.date_end)
                                                        ])
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BASE_IMP':
                                montant += line.total
                    if montant:
                        indemnite_fin_cdd2 = round(montant * 3) / 100
                        emp.indemnite_fin_cdd = round(montant * 3) / 100
                        _logger.info("Indemnité fin cdd %s", indemnite_fin_cdd2)
                        #employee.write({'indemnite_fin_cdd': indemnite_fin_cdd2})
                        employee.write({'indemnite_fin_cdd2': indemnite_fin_cdd2})
            if emp.contract_id.date_start and not emp.contract_id.date_end:
                emp.indemnite_fin_cdd = 0
            if not emp.contract_id.date_start and not emp.contract_id.date_end:
                emp.indemnite_fin_cdd = 0

    def _get_indemnite_deces(self):
        for emp in self:
            emp_id = emp.ids[0]
            employee = emp.env['hr.employee'].search([('id', '=', emp_id)])
            _logger.info("Indemnité de décès de l'employe %s", employee)
            if emp.contract_id and emp.is_deces:
                year = emp.contract_id.an_anciennete
                wage = emp.contract_id.wage
                if 0 <= year <= 6:
                    emp.indemnite_deces = wage * 3
                    indemnite_deces2 = wage * 3
                    employee.write({'indemnite_deces2': indemnite_deces2})
                elif 6 <= year <= 10:
                    emp.indemnite_deces = (wage * 4) + (wage * 3)
                    indemnite_deces2 = (wage * 4) + (wage * 3)
                    employee.write({'indemnite_deces2': indemnite_deces2})
                elif 10 < year:
                    emp.indemnite_deces = (wage * 6) + (wage * 4) + (wage * 3)
                    indemnite_deces2 = (wage * 6) + (wage * 4) + (wage * 3)
                    employee.write({'indemnite_deces2': indemnite_deces2})
            if emp.contract_id and not emp.is_deces:
                emp.indemnite_deces = 0
            if not emp.contract_id and not emp.is_deces:
                emp.indemnite_deces = 0
            if not emp.contract_id and emp.is_deces:
                emp.indemnite_deces = 0

    def _get_jour_conge(self):
        #        self.ensure_one()
        for emp in self:
            emp_id = emp.ids[0]
            print(emp_id, emp.contract_id.date_start)
            if emp.contract_id.date_start and not emp.date_retour_conge:
                payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', emp_id), ('date_from', '>=', emp.contract_id.date_start)])
                # payslip = slip_obj.search(
                #     [('employee_id', '=', emp_id), ('date_from', '>=', emp.contract_id.date_start)])
                # payslip = slip_obj.browse(slip_ids)
                worked_days_number = list()
                _logger.info("Bulletion pour les jours de conge  %s %s" % (emp_id, payslip))
                if payslip:
                    print('ok for payslip')
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    nwd = sum(worked_days_number)
                    jc = len(payslip) * 2.2
                    #print("jour de conge de l'employé %s " % emp.name, jc / nwd)
                    emp.jour_conge = jc / nwd if nwd else 0
                    print(emp.jour_conge)
                    _logger.info("Allocation congé de l'employe est %s", emp.jour_conge)
            elif emp.date_retour_conge and emp.contract_id.date_start:
                # payslip = slip_obj.search([('employee_id', '=', emp_id), ('date_from', '>=', emp.date_retour_conge)])
                payslip = self.env['hr.payslip'].search(
                    [('employee_id', '=', emp_id), ('date_from', '>=', emp.date_retour_conge)])
                # payslip = slip_obj.browse(payslips)
                worked_days_number = list()
                if payslip:
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    nwd = sum(worked_days_number)
                    jc = len(payslip) * 2.2
                    emp.jour_conge = jc / nwd if nwd else 0
                    _logger.info("Allocation congé de l'employe est %s", emp.jour_conge)
            # elif emp.date_retour_conge and emp.debut_rupture:
            #     date1 = datetime.strptime(emp.date_retour_conge, '%Y-%m-%d')
            #     date2 = datetime.strptime(emp.debut_rupture, '%Y-%m-%d')
            #     delta = date2 - date1
            #     days = delta.days
            #     emp.jour_conge = (days * 2.2) / 30

    def _get_allocation_conge(self):
        # smj = self.env['hr.employee'].search([('id', '=', self.id)]).montant_moyen_journalier
        # smm = self.env['hr.employee'].search([('id', '=', self.id)]).montant_moyen_mensuel
        # jcr = self.env['hr.employee'].search([('id', '=', self.id)]).remaining_leaves
        # jour_conge = self.env['hr.employee'].search([('id', '=', self.id)]).jour_conge
        # employee = self.env['hr.employee'].search([('id', '=', self.id)])
        #slip_obj = self.env['hr.payslip'].search([])
        for emp in self:
            print(type(emp.id), emp.ids[0])
            smj = emp.env['hr.employee'].search([('id', '=', emp.ids[0])]).montant_moyen_journalier
            smm = emp.env['hr.employee'].search([('id', '=', emp.ids[0])]).montant_moyen_mensuel
            jc = emp.env['hr.employee'].search([('id', '=', emp.ids[0])]).jour_conge
            jour_conge = emp.env['hr.employee'].search([('id', '=', emp.ids[0])]).jour_conge
            employee = emp.env['hr.employee'].search([('id', '=', emp.ids[0])])
            company = emp.env.user.company_id
            # if company.moyen_allocation == "smj":
            #     print('Salaire moyen journalier')
            #     if emp.contract_id.date_start and not emp.date_retour_conge:
            #         emp.allocation_conge = round(smj * jour_conge * 1.25)
            #         allocation_conge = round(smj * jour_conge * 1.25)
            #         employee.write({'allocation_conge2': allocation_conge})
            #         return float(allocation_conge)
            #     elif emp.date_retour_conge and emp.contract_id.date_start and not emp.debut_rupture:
            #         emp.allocation_conge = round(smj * jour_conge * 1.25)
            #         allocation_conge = round(smj * jour_conge * 1.25)
            #         employee.write({'allocation_conge2': allocation_conge})
            #         return float(allocation_conge)
            #     elif emp.date_retour_conge and emp.debut_rupture:
            #         emp.allocation_conge = round(smj * jour_conge * 1.25)
            #         allocation_conge = round(smj * jour_conge * 1.25)
            #         employee.write({'allocation_conge2': allocation_conge})
            #         return float(allocation_conge)
            # if company.moyen_allocation == "smm":
            #     print('Salaire moyen mensuel')
            if emp.contract_id.date_start and not emp.date_retour_conge:
                slip_obj = self.env['hr.payslip'].search([])
                slip_ids = slip_obj.search(
                    [('employee_id', '=', emp.id), ('date_from', '>=', emp.contract_id.date_start)])
                payslip = slip_obj.browse(slip_ids)
                #jc = len(payslip) * 2.2
                #sj = (smm / 30)
                emp.allocation_conge = round(smm * jc * 1.25)
                allocation_conge = round(smm * jc * 1.25)
                employee.write({'allocation_conge2': allocation_conge})
                _logger.info("Allocation congé est %s", (str(allocation_conge)))
                return allocation_conge
            elif emp.date_retour_conge and emp.contract_id.date_start and not emp.debut_rupture:
                slip_obj = self.env['hr.payslip'].search([])
                payslips = slip_obj.search(
                    [('employee_id', '=', emp.id), ('date_from', '>=', emp.date_retour_conge)])
                payslip = slip_obj.browse(payslips)
                #jc = len(payslip) * 2.2
                sj = (smm / 30)
                emp.allocation_conge = round(smm * jc * 1.25)
                allocation_conge = round(smm * jc * 1.25)
                employee.write({'allocation_conge2': allocation_conge})
                _logger.info("Allocation congé de l'employe %s est %s", (employee, str(allocation_conge)))
                return allocation_conge
            # elif emp.date_retour_conge and emp.debut_rupture:
            #     date1 = datetime.strptime(emp.date_retour_conge, '%Y-%m-%d')
            #     date2 = datetime.strptime(emp.debut_rupture, '%Y-%m-%d')
            #     delta = date2 - date1
            #     days = delta.days
            #     jc = (days * 2.2) / 30
            #     sj = (smm / 30)
            #     emp.allocation_conge = round(sj * jc * 1.25)
            #     allocation_conge = round(sj * jc * 1.25)
            #     employee.write({'allocation_conge2': allocation_conge})
            #     return allocation_conge




