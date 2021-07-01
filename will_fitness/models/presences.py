from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime, date
#from xl2dict import XlToDict


class will_fitness_presence(models.Model):
    _name = 'will.fitness.presence'
    _description = "Presence des eleves"

    #infos à saisir pour le voyage
    name = fields.Char(string="ID Presence",
                       copy=False,
                       index=True,
                       required=True,
                       default=lambda self: _('New'),
                       readonly=True)
    client = fields.Many2one(
        'res.partner',
        string="Client",
    )
    arrivee = fields.Datetime(
        string='Arrivée',
        default=fields.Datetime.now,
    )
    sortie = fields.Datetime(
        string='Sortie',
        default=fields.Datetime.now,
    )
    duree_de_travail = fields.Float(string='Durée de travail', readonly=True)


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'will.fitness.presence.sequence', ) or _('New')
        result = super(will_fitness_presence, self).create(vals)

        #Thanks LORD (Jesus)
        #a = datetime.now().time()
        time_one = result.arrivee.hour + result.arrivee.minute / 60.0
        time_two = result.sortie.hour + result.sortie.minute / 60.0
        result.write({'duree_de_travail': time_two - time_one})
        return result


    # def _treat_xlsx(self, attachment):
    #     fname = attachment.store_fname
    #     full_path = attachment._full_path(fname)
    #     myxlobject = XlToDict()
    #     data = myxlobject.fetch_data_by_column_by_sheet_index(
    #         file_name=full_path, sheet_index=0)
    #     i = 1
    #     for d in data:
    #         coach = d.get("coach")
    #         nom = d.get("nom")
    #         arrivee = d.get("arrivee")
    #         sortie = d.get("sortie")

    #         str_coach = False
    #         str_nom = False
    #         str_arrivee = False
    #         str_sortie = False

    #         if coach:
    #             str_coach = str(coach)
    #         if nom:
    #             str_nom = str(nom)
    #         if arrivee:
    #             str_arrivee = str(arrivee)
    #         if sortie:
    #             str_sortie = str(sortie)
                
    #         infos = dict(None or {
    #             'coach': str_coach,
    #             'nom': str_nom,
    #             'arrivee': str_arrivee,
    #             'sortie': str_sortie,
    #             })
                    
    #         if str_coach == "1":
    #             #Créer la présence dans les employés si l'employé existe
    #             self.env['hr.employee'].sudo().create(infos)

    #         if str_coach == "0":
    #             #Créer la présence dans les clients si le contact existe
    #             self.env['res.partner'].sudo().create(infos)