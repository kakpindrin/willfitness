# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class planning_slot(models.Model):
    _inherit = 'planning.slot'

    #Thank you LORD

    classe_id = fields.Many2one('will.fitness.classe', string='Classe',)