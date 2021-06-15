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
    duree_de_travail = fields.Float(string='Durée de travail', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('will.fitness.presence.sequence',) or _('New')
        result = super(will_fitness_presence, self).create(vals)

        #a = datetime.now().time()
        time_one = result.sortie.hour + result.sortie.minute/60.0
        time_two = result.arrivee.hour + result.arrivee.minute/60.0
        result.write({
            'duree_de_travail': time_one - time_two
        })
        return result