# -*- encoding: utf-8 -*-

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta


from odoo import models, fields, api
#from openerp import api,modules


class hr_payroll(models.Model):
    _name="hr.payroll"
    _description="Livre de paie"

    name = fields.Char("Libellé",size=128)
    date_from = fields.Date('Date de début',required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('Date de fin',required=True, default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    line_ids = fields.One2many('hr.payroll.line','hr_payroll_id',"Lignes de livre de paie")
    company_id = fields.Many2one('res.company','Compagnie', default=lambda self: self.env.user.company_id)
    partner_id = fields.Many2one('res.partner','Parténaire')

    _defaults = {
        'partner_id':1,
        }
    
    def print_payroll(self):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        data = {'ids': self.id, 'form': self.read(['date_from', 'date_to'])[0], 'model': 'hr.payroll'}
        self.compute_hr_payroll()
        return self.env.ref('hr_payroll_ci_raport.report_hr_payroll').with_context(landscape=True).report_action(self, data=data)

    def get_amount_by_code(self, line_ids, code):
        amount = 0
        for line in line_ids:
            if line.code == code:
                amount += line.total
        return amount
            
    def get_amount_by_category(self, line_ids, category):
        rcategory_obj=self.env['hr.salary.rule.category']
        category_id=rcategory_obj.search([('code',"=",category)])
        montant=0        
        if category_id:
            for line in line_ids:
                if line.category_id == category_id[0]:
                    montant += line.total
        return montant
    
    def compute_hr_payroll(self):
        hpslip_obj=self.env['hr.payslip'].search([])
        hpline_obj=self.env['hr.payroll.line'].search([])
        lines = []
        for i in self:
            if i.line_ids:
                print('lines', i.line_ids)
                i._cr.execute("DELETE FROM hr_payroll_line WHERE hr_payroll_id=%s"%i.id)
                i._cr.commit()
            res={'value':{'line_ids':False}}
            slip_ids=hpslip_obj.search([('date_from','<=',i.date_from),('date_to','>=',i.date_to)])
            for slip in slip_ids:
                vals={
                        'name':slip.employee_id.name,
                        'salaire_base':self.get_amount_by_code(slip.line_ids, "BASE"),
                        "sursalaire":self.get_amount_by_code(slip.line_ids, "SURSA"),
                        "prime_imposable":self.get_amount_by_code(slip.line_ids, "PIMP"),
                        "prime_anciennete":self.get_amount_by_code(slip.line_ids, "PANC"),
                        "hs":self.get_amount_by_code(slip.line_ids, "HSUPP"),
                        "avantage_nature":self.get_amount_by_code(slip.line_ids, "AVTGN"),
                        "salbrut":self.get_amount_by_code(slip.line_ids, "BRUT"),
                        "salbrut_imposable":self.get_amount_by_code(slip.line_ids, "BASE_IMP"),
                        "its":self.get_amount_by_code(slip.line_ids, "ITS"),
                        "igr":self.get_amount_by_code(slip.line_ids, "IGR"),
                        "cn":self.get_amount_by_code(slip.line_ids, "CN"),
                        "cnps":self.get_amount_by_code(slip.line_ids, "CNPS"),
                        "cmu":self.get_amount_by_code(slip.line_ids, "CMU_EMPLOYE"),
                        "total_retenues":self.get_amount_by_code(slip.line_ids, "RET"),
                        "avance":self.get_amount_by_code(slip.line_ids, "AVANT_ACOMPTE"),
                        "autre_retenue":self.get_amount_by_code(slip.line_ids, "AUTRE_RETENUE"),
                        "indem_non_impo":self.get_amount_by_code(slip.line_ids, "C_PNIMP"),
                        "abattement":self.get_amount_by_code(slip.line_ids, "ABB"),
                        "trsp":self.get_amount_by_code(slip.line_ids, "TRSP"),
                        "net_a_paye":self.get_amount_by_code(slip.line_ids, "NET"),
                        "hr_payroll_id":i.id,
                      }
                lines.append((0, 0, vals))
            print(lines)
            self.line_ids = lines


class hr_payroll_line(models.Model):
    _name="hr.payroll.line"
    _description="Ligne de livre de paie"

    name = fields.Char("Nom & Prénoms",size=128,required=True)
    salaire_base = fields.Integer("Salaire de base",requred=True)
    sursalaire = fields.Integer("Sursalaire",required=True)
    prime_imposable = fields.Integer("Primes Imposables",required=True)
    hs = fields.Integer("Heures Supplémentaires",required=True)
    avantage_nature = fields.Integer("Avantages en nature",required=True)
    salbrut_imposable = fields.Integer("Salaire Brut imposable",requried=True)
    salbrut = fields.Integer("Salaire Brut",requried=True)
    its = fields.Integer("ITS",required=True)
    igr = fields.Integer("IGR",required=True)
    cn = fields.Integer("CN",required=True)
    cnps = fields.Integer("CNPS",required=True)
    cmu = fields.Integer("CMU",required=True)
    total_retenues = fields.Integer("Total Retenues",required=True)
    avance = fields.Integer("Avances & Accomptes",required=True)
    indem_non_impo = fields.Integer("Indemnité non impossable",required=True)
    abattement = fields.Integer("Abattemnt 10%",required=True)
    prime_anciennete = fields.Integer("Prime d'ancienneté",required=True)
    trsp = fields.Integer("Prime de transport",required=True)
    net_a_paye = fields.Integer("Net à payer")
    autre_retenue = fields.Integer("Autres retenue")
    hr_payroll_id = fields.Many2one('hr.payroll',"Livre de paie",required=True)
