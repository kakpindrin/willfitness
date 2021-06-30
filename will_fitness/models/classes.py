from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, date
#from xl2dict import XlToDict


class will_fitness_classe(models.Model):
    _name = 'will.fitness.classe'
    _description = "Classe des eleves"

    #infos à saisir pour la classe
    name = fields.Char(string="Nom de la Classe", copy=False, index=True, required=True,)
    
    @api.model
    def create(self, vals):
        result = super(will_fitness_classe, self).create(vals)
        return result