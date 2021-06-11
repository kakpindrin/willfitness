# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil import relativedelta
import time

class HrEtatResumeCotisationMensuelle(models.Model):
    _name = "hr.etat.cotisation.mensuelle"

    # date_from = fields.Date()
    # date_to = fields.Date()
    date_from = fields.Date('Date de début', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('Date de fin', required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    company = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.user.company_id)
    cn = fields.Float("Contribution Nationnale", digits_compute=dp.get_precision('Account'))
    igr = fields.Float("Impot general sur revenu", digits_compute=dp.get_precision('Account'))
    IS = fields.Float("Impot sur salaire", digits_compute=dp.get_precision('Account'))
    part_is_locaux = fields.Float("Part patronale IS locaux", digits_compute=dp.get_precision('Account'))
    crtci_cnps = fields.Float("C.R.T.C.I(C.N.P.S)", digits_compute=dp.get_precision('Account'))
    retraite_generale = fields.Float("Retraite generale", digits_compute=dp.get_precision('Account'))
    prestation_familiale = fields.Float("Prestation familiale", digits_compute=dp.get_precision('Account'))
    accident_travail = fields.Float("Accident de travail", digits_compute=dp.get_precision('Account'))
    cmu_employe = fields.Float(digits_compute=dp.get_precision('Account'))
    cmu_employeur = fields.Float(digits_compute=dp.get_precision('Account'))
    taxe_fpc = fields.Float("Taxe F.P.C", digits_compute=dp.get_precision('Account'))
    taxe_apprentissage = fields.Float("Taxe apprentissage", digits_compute=dp.get_precision('Account'))
    salaire_brut = fields.Float("Salaire brut", digits_compute=dp.get_precision('Account'))
    base_cnps = fields.Float("Base CNPS", digits_compute=dp.get_precision('Account'))
    total_montant_salarial_impot = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_patronal_impot = fields.Float(digits_compute=dp.get_precision('Account'))
    montant_global_impot = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_salarial_cnps = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_patronal_cnps = fields.Float(digits_compute=dp.get_precision('Account'))
    montant_global_cnps = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_salarial_fpc = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_patronal_fpc = fields.Float(digits_compute=dp.get_precision('Account'))
    montant_global_fpc = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_salarial_fdfp = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_patronal_fdfp = fields.Float(digits_compute=dp.get_precision('Account'))
    montant_global_fdfp = fields.Float(digits_compute=dp.get_precision('Account'))
    total_salarial = fields.Float(digits_compute=dp.get_precision('Account'))
    total_patronal = fields.Float(digits_compute=dp.get_precision('Account'))
    total_montant_global = fields.Float(digits_compute=dp.get_precision('Account'))
    male = fields.Integer(default=0)
    female = fields.Integer(default=0)
    assiette_pf = fields.Float(digits_compute=dp.get_precision('Account'))
    base_pf = fields.Float(digits_compute=dp.get_precision('Account'))
    assiette_at = fields.Float(digits_compute=dp.get_precision('Account'))
    base_at = fields.Float(digits_compute=dp.get_precision('Account'))
    assiette_cmu = fields.Float(digits_compute=dp.get_precision('Account'))
    base_cmu = fields.Float(digits_compute=dp.get_precision('Account'))

    def sum_lines(self, lines, code):
        montant = 0
        if lines:
            for line in lines:
                for l in line:
                    if l.code == code:
                        montant += l.amount
            return montant

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

    def get_etat_mensuelle(self):
        payslip_obj = self.env['hr.payslip'].search([('date_from', '>=', self.date_from),
                                                     ('date_to', '<=', self.date_to)])
        line_ids = list()
        male = 0
        female = 0
        for slip in payslip_obj:
            if slip.employee_id.gender == 'male':
                male += 1
            if slip.employee_id.gender == 'female':
                female += 1
            line_ids.append(slip.line_ids)
        self.male = male
        self.female = female
        if line_ids:
            self.salaire_brut = self.get_amount_by_code(payslip_obj, 'BASE_IMP')
            self.base_cnps = self.get_amount_by_code(payslip_obj, 'BASE_CNPS')
            # Assiette et Base de cotisation PF
            self.assiette_pf = self.get_amount_by_code(payslip_obj, 'BASE_IMP_2')
            self.base_pf = self.get_amount_by_code(payslip_obj, 'BASE_IMP_2')
            self.prestation_familiale = (self.base_pf * 5.75)/100
            # Assiette et Base de cotisation AT
            self.assiette_at = self.get_amount_by_code(payslip_obj, 'BASE_CNPS')
            self.base_at = self.get_amount_by_code(payslip_obj, 'BASE_IMP_2')
            self.accident_travail = (self.base_at * 3) / 100
            self.cn = self.get_amount_by_code(payslip_obj, 'CN')
            self.igr = self.get_amount_by_code(payslip_obj, 'IGR')
            self.IS = self.get_amount_by_code(payslip_obj, 'ITS')
            self.part_is_locaux = self.get_amount_by_code(payslip_obj, 'ITS')
            self.crtci_cnps = (self.base_cnps * 6.3)/100
            self.retraite_generale = (self.base_cnps * 7.7)/100
            self.cmu_employe = self.get_amount_by_code(payslip_obj, 'CMU_EMPLOYE')
            self.cmu_employeur = self.get_amount_by_code(payslip_obj, 'CMU_EMPLOYEUR')
            # Assiette et base CMU
            self.assiette_cmu = self.cmu_employe + self.cmu_employeur
            self.base_cmu = self.cmu_employe + self.cmu_employeur
            # Taxe
            self.taxe_fpc = (self.salaire_brut * 0.60)/100
            self.taxe_apprentissage = (self.salaire_brut * 0.40)/100
            # Total Impot
            self.total_montant_salarial_impot = self.cn + self.igr + self.IS
            self.total_montant_patronal_impot = self.part_is_locaux
            self.montant_global_impot = self.total_montant_salarial_impot + self.total_montant_patronal_impot
            # Total C.N.P.S
            self.total_montant_salarial_cnps = self.crtci_cnps + self.cmu_employe
            self.total_montant_patronal_cnps = self.retraite_generale + self.prestation_familiale + self.accident_travail + self.cmu_employeur
            self.montant_global_cnps = self.total_montant_salarial_cnps + self.total_montant_patronal_cnps
            # Total F.P.C
            self.total_montant_salarial_fpc = 0
            self.total_montant_patronal_fpc = self.taxe_fpc
            self.montant_global_fpc = self.total_montant_patronal_fpc
            # Total F.D.F.P
            self.total_montant_salarial_fdfp = 0
            self.total_montant_patronal_fdfp = self.taxe_apprentissage
            self.montant_global_fdfp = self.total_montant_patronal_fdfp
            # Total
            self.total_salarial = self.total_montant_salarial_impot + self.total_montant_salarial_cnps
            self.total_patronal = self.total_montant_patronal_impot + self.total_montant_patronal_cnps + self.total_montant_patronal_fpc + self.total_montant_patronal_fdfp
            self.total_montant_global = self.montant_global_impot + self.montant_global_cnps + self.montant_global_fpc + self.montant_global_fdfp

    def print_etat_mensuelle(self):
        print('ok here')
        #data = {'form': self.read(['date_from', 'date_to'])[0]}
        data = {'ids': self.id, 'form': self.read(['date_from', 'date_to'])[0], 'model': 'hr.etat.cotisation.mensuelle'}
        self.get_etat_mensuelle()
        return self.env.ref('hr_payroll_ci_raport.hr_etat_resume_report').with_context(landscape=True).report_action(self, data=data)
