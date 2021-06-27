from odoo import fields, models


class RfidSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    event_lifetime = fields.Integer(string="Durée de vie de l'événement", default=365,
                                    config_parameter='hr_rfid.event_lifetime',
                                    help="Entrez la durée de vie de l'événement. Les événements plus anciens seront supprimés")
    save_webstack_communications = fields.Selection([('True', 'On'),
                                                    ('False', 'Off'),
                                                    ],string='Enregistrer la communication WebStack', default='False',
                                                    config_parameter='hr_rfid.save_webstack_communications',
                                                    help='Enregistrer la communication WebStack')



