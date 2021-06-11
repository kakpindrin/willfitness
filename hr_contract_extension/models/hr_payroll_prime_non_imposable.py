#-*- encoding: utf-8 -*-


from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import *


class PrimeNonImposable(models.Model):
    _name = 'prime.non.imposable'
    _description = "Prime Non Imposable"

    name = fields.Char('name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class PrimeNonImposableMontant(models.Model):
    _name = 'prime.non.imposable.montant'
    _description = "Prime Non Imposable Montant"

    prime_id = fields.Many2one('prime.non.imposable', 'prime non imposable', required=True)
    code = fields.Char(string="Code")
    contract_id = fields.Many2one('hr.contract', 'Contract')
    montant_prime = fields.Integer('Montant', required=True)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    prime_non_imposable_ids = fields.One2many("prime.non.imposable.montant",'contract_id',"Primes non imposables")
    cumul_prime_non_imposable = fields.Monetary(store=True, readonly=True, compute='_get_cumul_non_imposable', string='Cumul Prime Non Imposable')
    cumul_prime_non_imposable2 = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Cumul Prime Non Imposable 2')
    prime_risque = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de Risque')
    prime_assiduite = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime d\'assiduité')
    prime_caisse = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de Caisse')
    prime_technicite = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de Technicité')
    prime_salissure = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de Salissure')
    prime_panier = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de Panier')
    prime_outillage = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de Outillage')
    prime_fonction_non = fields.Monetary(digits_compute=dp.get_precision('Account'), string='Prime de fonction')
    # is_prime_risque = fields.Boolean()
    # is_prime_assiduite = fields.Boolean()
    # is_prime_caisse = fields.Boolean()
    # is_prime_technicite = fields.Boolean()
    # is_prime_salissure = fields.Boolean()
    # is_prime_panier = fields.Boolean()
    # is_prime_outillage = fields.Boolean()
    # is_prime_fonction_non = fields.Boolean()

    @api.depends('prime_non_imposable_ids.montant_prime')
    def _get_cumul_non_imposable(self):
        for c in self:
            if c.prime_non_imposable_ids:
                amount = 0
                for line in c.prime_non_imposable_ids:
                    print(line.prime_id.code)
                    if line.prime_id.code == 'PR':
                        c.write({'prime_risque': line.montant_prime})
                    if line.prime_id.code == 'PA':
                        c.write({'prime_assiduite': line.montant_prime})
                    if line.prime_id.code == 'PC':
                        c.write({'prime_caisse': line.montant_prime})
                    if line.prime_id.code == 'PT':
                        c.write({'prime_technicite': line.montant_prime})
                    if line.prime_id.code == 'PS':
                        c.write({'prime_salissure': line.montant_prime})
                    if line.prime_id.code == 'PP':
                        c.write({'prime_panier': line.montant_prime})
                    if line.prime_id.code == 'PO':
                        c.write({'prime_outillage': line.montant_prime})
                    if line.prime_id.code == 'PF':
                        c.write({'prime_fonction_non': line.montant_prime})
                    amount += line.montant_prime
                print(amount)
                c.cumul_prime_non_imposable = amount
                c.cumul_prime_non_imposable2 = amount
                return amount
