# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    canal = fields.Char(string='Canal', help="Canal de récupération des mails", config_parameter='crm_ademat.canal')
    #default_email_biller = fields.Char(string='Email factureur', config_parameter='crm_ademat.email_biller', default_model="crm.lead")
