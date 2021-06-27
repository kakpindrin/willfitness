from odoo import models, fields

import json


class RawData(models.Model):
    _name = 'hr.rfid.raw.data'
    _description = 'Raw Data'

    data = fields.Char(
        string='Données',
    )

    timestamp = fields.Datetime(
        string='Horodatage des événements/données',
        help="Heure de création de l'événement/des données",
    )

    receive_ts = fields.Datetime(
        string="Recevoir l'horodatage",
        default=fields.Datetime.now()
    )

    identification = fields.Char(
        string='Série Webstack',
    )

    security = fields.Char(
        string='Sécurité',
    )

    do_not_save = fields.Boolean(
        string='Enregistrer des données?',
        help="S'il faut ou non sauvegarder les données après leur traitement",
        default=False,
    )

    return_data = fields.Char(
        string='Renvoyer les données',
        help='Que retourner à la requête json',
        default=json.dumps({'status': 200}),
    )
