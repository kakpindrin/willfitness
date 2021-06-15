# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class res_partner(models.Model):
    _inherit = 'res.partner'

    prenom = fields.Char(string='Prénom')
    date_naissance = fields.Date(string='Date Naissance',)
    adresse_postale = fields.Char(string='Adresse Postale')
    poids = fields.Float(string='Poids')
    taille = fields.Float(string='Taille')
    antecedent_medical = fields.Text(string='Antécédent médical')
    contact_urgence = fields.Char(string='Contact Urgence')