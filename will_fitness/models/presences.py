from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, date

class will_fitness_presence(models.Model):
    _name = 'will.fitness.presence'
    _description = "Presence des eleves"
    
    #infos à saisir pour le voyage
    name = fields.Char(string="ID Presence", copy=False, index=True, required=True, default=lambda self: _('New'), readonly=True)
    client = fields.Many2one('res.partner', string="Client",)
    arrivee = fields.Datetime(string='Arrivée', default=fields.Datetime.now,)
    sortie = fields.Datetime(string='Sortie', default=fields.Datetime.now,)
    duree_de_travail = fields.Float(string='Durée de travail',)