# -*- coding: utf-8 -*-

from random import choice
from string import digits
from odoo import api, fields, models, _
from datetime import datetime, date

class sale_subscription(models.Model):
    _inherit = 'sale.subscription'

    mode_reglement = fields.Selection(string="Mode Règlement", selection=[('especes','ESPÈCES'),
                                                         ('cartebancaire','CARTE BANCAIRE'),
                                                         ('virement','VIREMENT'),
                                                         ('cheque','CHÈQUE')], default="especes",)
    
    #THINK GOOD
    @api.model
    def create(self, values):
        """
            Create a new record for a model sale_subscription
            @param values: provides a data for new record
    
            @return: returns a id of new record
        """
    
        result = super(sale_subscription, self).create(values)

        partners_domain = [('id','=',result.partner_id.id)]
        all_partners = self.env['res.partner'].search(partners_domain, order='id desc')

        if len(all_partners) > 0:
            #for partner in all_partners:
            if not all_partners[0].barcode:
                a_barcode = '041'+"".join(choice(digits) for i in range(9))
                all_partners[0].write({
                    'barcode': a_barcode
                })

        the_partners_domain = [('id','=',result.partner_id.id)]
        the_all_partners = self.env['res.partner'].search(the_partners_domain, order='id desc')
        if len(the_all_partners) > 0:
            now = datetime.now()
    
            rfid_card = dict(None or {
                'number': the_all_partners[0].barcode,
                'contact_id': the_all_partners[0].id,
                'cloud_card': False,
                'activation_temp_date': result.recurring_next_date,
                'activate_on': result.date_start,
                'deactivate_on': result.date_start,
                })
            self.env['hr.rfid.card'].sudo().create(rfid_card)

        return result

    @api.onchange('recurring_next_date')
    def _onchange_my_recurring_next_date(self):
        if self.recurring_next_date:
            the_cards_domain = [('contact_id','=',self.partner_id.id)]
            the_all_cards = self.env['hr.rfid.card'].search(the_cards_domain, order='id desc')

            if len(the_all_cards) > 0:
                the_all_cards[0].write({
                    'activation_temp_date': self.recurring_next_date,
                })