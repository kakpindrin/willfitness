# -*- coding: utf-8 -*-

from random import choice
from string import digits
from odoo import api, fields, models, _

class account_move(models.Model):
    _inherit = 'account.move'

    @api.onchange('payment_state')
    def _onchange_payment_state(self):
        for this in self:
            state_of_payment = ['paid', 'in_payment']
            if this.payment_state in state_of_payment:
                the_cards_domain = [('contact_id','=',this.partner_id.id)]
                the_all_cards = this.env['hr.rfid.card'].search(the_cards_domain, order='id desc')

                if len(the_all_cards) > 0:
                    the_all_cards[0].write({
                        'deactivate_on': the_all_cards[0].activation_temp_date
                    })