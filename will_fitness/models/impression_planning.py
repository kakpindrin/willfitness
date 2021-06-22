from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, date

class will_fitness_planning(models.Model):
    _name = 'will.fitness.planning'
    _description = "Planning des coaches"
    
    #infos à saisir plour imprimer le planning
    name = fields.Char(string="ID Planning", copy=False, index=True, required=True, default=lambda self: _('New'), readonly=True)
    debut = fields.Datetime(string='Début')
    fin = fields.Datetime(string='Fin')
    planning_slot_ids = fields.Many2many('planning.slot', string="Coaches plans")
    
    state = fields.Selection(string="Statut", selection=[('new','Nouveau'),
                                                         ('generate','Généré'),], default="new", track_visibility='onchange')

    def generate_planning_to_impress(self):
        if self.debut and self.fin:
            plannings_domain = [('start_datetime','>=',self.debut),('end_datetime','<=',self.fin),]
            plannings = self.env['planning.slot'].search(plannings_domain, order='id desc')

            if len(plannings) > 0:
                self.write({
                    'planning_slot_ids': plannings,
                    'state': 'generate'
                })


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('will.fitness.planning.sequence',) or _('New')
        result = super(will_fitness_planning, self).create(vals)

        return result