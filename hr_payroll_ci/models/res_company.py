# -*- coding: utf-8 -*-
##############################################################################
##############################################################################


from odoo import models, fields

class res_company(models.Model):
    _inherit = 'res.company'

    num_cnps= fields.Char("Numéro CNPS", size=124,required=True)
    num_contribuable= fields.Char("Numéro Contribuable",size=128,required=True)
    moyen_allocation = fields.Selection([('smm', 'Salaire moyen mensuel'), ('smj', 'Salaire moyen journalier')],"Moyen de calcule de l'allocation")
