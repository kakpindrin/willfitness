# -*- coding: utf-8 -*-

from random import choice
from string import digits
from odoo import api, fields, models, _

class res_partner(models.Model):
    _inherit = 'res.partner'

    prenom = fields.Char(string='Prénoms')
    date_naissance = fields.Date(string='Date Naissance',)
    adresse_postale = fields.Char(string='Adresse Postale')
    poids = fields.Float(string='Poids')
    taille = fields.Float(string='Taille')
    antecedent_medical = fields.Text(string='Antécédent médical')
    contact_urgence = fields.Char(string='Contact Urgence')

    #barcode = fields.Char(string="Badge ID", help="ID used for partner identification.", groups="hr.group_hr_user", copy=False)
    barcode = fields.Char(string="Badge ID", help="ID used for partner identification.", groups="hr.group_hr_user", copy=False)

    _sql_constraints = [
        ('barcode_uniq', 'unique (barcode)', "The Badge ID must be unique, this one is already assigned to another partner."),
    ]

    #THINK GOOD
    def generate_random_barcode(self):
        for partner in self:
            partner.barcode = '041'+"".join(choice(digits) for i in range(9))