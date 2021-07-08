# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
from datetime import timedelta, datetime
from enum import Enum


class OwnerType(Enum):
    Employee = 1
    Contact = 2


class HrRfidCard(models.Model):
    _name = 'hr.rfid.card'
    _description = 'Card'
    _inherit = ['mail.thread']

    def _get_cur_employee_id(self):
        return self.env.context.get('employee_id', None)

    def _get_cur_contact_id(self):
        return self.env.context.get('contact_id', None)

    name = fields.Char(
        compute='_compute_card_name',
    )

    #MODIFICATION NUMBER
    number = fields.Char(
        string='Numéro de Carte',
        required=True,
        limit=12, 
        index=True,
        track_visibility='onchange',
    )

    activation_temp_date = fields.Datetime(string='Date Temporaire')

    card_type = fields.Many2one(
        'hr.rfid.card.type',
        string='Type de Carte',
        help="Seules les portes prenant en charge ce type pourront être ouvertes avec cette carte",
        default=lambda self: self.env.ref('hr_rfid.hr_rfid_card_type_def').id,
        track_visibility='onchange',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Titulaire de la carte (employé)',
        default=_get_cur_employee_id,
        track_visibility='onchange',
    )

    contact_id = fields.Many2one(
        'res.partner',
        string='Titulaire de la carte (contact)',
        default=_get_cur_contact_id,
        track_visibility='onchange',
        domain=[('is_company', '=', False)],
    )

    user_event_ids = fields.One2many(
        'hr.rfid.event.user',
        'card_id',
        string='Évènements',
        help="Événements concernant cet utilisateur",
    )

    activate_on = fields.Datetime(
        string='Activer le',
        help="Date et heure d'activation de la carte",
        track_visibility='onchange',
        default=lambda self: datetime.now(),
        index=True,
    )

    deactivate_on = fields.Datetime(
        string='Désactiver le',
        help='Date et heure de désactivation de la carte le',
        track_visibility='onchange',
        index=True,
    )

    active = fields.Boolean(
        string='Actif',
        help='Que la carte soit active ou non',
        track_visibility='onchange',
        default=True,
    )

    cloud_card = fields.Boolean(
        string='Carte Nuage',
        help='Une carte cloud ne sera pas ajoutée aux contrôleurs qui sont en mode "externalDB".',
        track_visibility='onchange',
        default=True,
        required=True,
    )

    door_rel_ids = fields.One2many(
        'hr.rfid.card.door.rel',
        'card_id',
        string='Portes',
        help='Portes auxquelles cette carte a accès',
    )

    door_ids = fields.Many2many(
        'hr.rfid.door',
        string='Portes',
        compute='_compute_door_ids',
    )

    pin_code = fields.Char(compute='_compute_pin_code')

    def get_owner(self):
        self.ensure_one()
        if len(self.employee_id) == 1:
            return self.employee_id
        return self.contact_id

    #DÉBUT DIBI CODE
    @api.onchange("employee_id",)
    def _onchange_employee(self):
        if self.employee_id:
            self.number = self.employee_id.barcode
    #Merci SEIGNEUR !
    @api.onchange("contact_id",)
    def _onchange_contact(self):
        if self.contact_id:
            self.number = self.contact_id.barcode
    #FIN DIBI CODE

    def get_potential_access_doors(self, access_groups=None):
        """
        Renvoie une liste de tuples (door, time_schedule) auxquels la carte a potentiellement accès
        """
        if access_groups is None:
            owner = self.get_owner()
            access_groups = owner.hr_rfid_access_group_ids.mapped('access_group_id')
        else:
            owner = self.get_owner()
            valid_access_groups = owner.hr_rfid_access_group_ids.mapped('access_group_id')
            if access_groups not in valid_access_groups:
                return [ ]
        door_rel_ids = access_groups.mapped('all_door_ids')
        return [ (rel.door_id, rel.time_schedule_id) for rel in door_rel_ids ]

    def door_compatible(self, door_id):
        return self.card_type == door_id.card_type \
               and not (self.cloud_card is True and door_id.controller_id.external_db is True)

    def card_ready(self):
        return self.active

    #BUILD
    @api.depends('employee_id', 'contact_id')
    def _compute_pin_code(self):
        for card in self:
            card.pin_code = card.get_owner().hr_rfid_pin_code

    def toggle_card_active(self):
        self.ensure_one()
        self.active = not self.active

    @api.constrains('employee_id', 'contact_id')
    def _check_user(self):
        for card in self:
            if card.employee_id is not None and card.contact_id is not None:
                if card.employee_id == card.contact_id or \
                   (len(card.employee_id) > 0 and len(card.contact_id) > 0):
                    raise exceptions.ValidationError("L'utilisateur de la carte et le contact ne peuvent pas être définis tous les deux"
                                                      "en même temps, et ne peuvent pas être tous les deux vides.")

    @api.onchange('number')
    def _check_len_number(self):
        for card in self:
            if card.number:
                if len(card.number) < 12: 
                    zeroes = 12 - len(card.number)
                    card.number = (zeroes * '0') + card.number
                elif len(card.number) > 12: 
                    raise exceptions.UserError(_("Le numéro de carte doit comporter exactement 12 chiffres"))



    @api.constrains('number')
    def _check_number(self):
        for card in self:
            dupes = self.search([ ('number', '=', card.number), ('card_type', '=', card.card_type.id) ])
            if len(dupes) > 1:
                raise exceptions.ValidationError(_("Le numéro de carte doit être unique pour chaque type de carte !"))

            if len(card.number) > 12:
                raise exceptions.ValidationError(_("Le numéro de carte doit comporter exactement 12 chiffres"))

            # if len(card.number) < 10:
            #     zeroes = 10 - len(card.number)
            #     card.number = (zeroes * '0') + card.number

            try:
                for char in card.number:
                    int(char, 10)
            except ValueError:
                raise exceptions.ValidationError("Les chiffres du numéro de carte doivent être compris entre 0 et 9")

    def _compute_card_name(self):
        for record in self:
            record.name = record.number

    @api.depends('door_rel_ids')
    def _compute_door_ids(self):
        for card in self:
            card.door_ids = card.door_rel_ids.mapped('door_id')

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']
        invalid_user_and_contact_msg = _("L'utilisateur de la carte et le contact ne peuvent pas être définis tous les deux" \
                                        " en même temps, et ne peuvent pas être tous les deux vides.")

        records = self.env['hr.rfid.card']
        for val in vals:
            card = super(HrRfidCard, self).create([val])
            records = records + card

            if len(card.employee_id) > 0 and len(card.contact_id) > 0:
                raise exceptions.ValidationError(invalid_user_and_contact_msg)

            if len(card.employee_id) == 0 and len(card.contact_id) == 0:
                raise exceptions.ValidationError(invalid_user_and_contact_msg)

            card_door_rel_env.update_card_rels(card)

        return records

    def write(self, vals):
        rel_env = self.env['hr.rfid.card.door.rel']
        invalid_user_and_contact_msg = "L'utilisateur de la carte et le contact ne peuvent pas être définis tous les deux" \
                                        " en même temps, et ne peuvent pas être tous les deux vides."

        for card in self:
            old_number = str(card.number)[:]
            old_owner = card.get_owner()
            old_active = card.active
            old_card_type_id = card.card_type
            old_cloud = card.cloud_card

            super(HrRfidCard, card).write(vals)

            if len(card.employee_id) > 0 and len(card.contact_id) > 0:
                raise exceptions.ValidationError(invalid_user_and_contact_msg)

            if len(card.employee_id) == 0 and len(card.contact_id) == 0:
                raise exceptions.ValidationError(invalid_user_and_contact_msg)

            if old_number != card.number:
                card.door_rel_ids.card_number_changed(old_number)

            if old_owner != card.get_owner():
                old_owner_doors = old_owner.get_doors()
                new_owner_doors = card.get_owner().get_doors()
                removed_doors = old_owner_doors - new_owner_doors
                added_doors = new_owner_doors - old_owner_doors
                for door in removed_doors:
                    rel_env.remove_rel(card, door)
                for door in added_doors:
                    rel_env.check_relevance_fast(card, door)

            if old_active != card.active:
                if card.active is False:
                    card.door_rel_ids.unlink()
                else:
                    rel_env.update_card_rels(card)

            if old_card_type_id != card.card_type:
                rel_env.update_card_rels(card)

            if old_cloud != card.cloud_card:
                rel_env.update_card_rels(card)

    def unlink(self):
        for card in self:
            card.door_rel_ids.unlink()
        return super(HrRfidCard, self).unlink()


    @api.model
    def _update_cards(self):
        cenv = self.env['hr.rfid.card']
        now = fields.datetime.now()
        str_before = str(now - timedelta(seconds=31))
        str_after  = str(now + timedelta(seconds=31))
        cards_to_activate = cenv.search(['|',('active', '=', True), ('active', '=', False),
                                         ('activate_on', '<', str_after),
                                          ('activate_on', '>', str_before) ])
        cards_to_deactivate = cenv.search(['|',('active', '=', True), ('active', '=', False),
                                           ('deactivate_on', '<', str_after),
                                            ('deactivate_on', '>', str_before) ])

        neutral_cards = cards_to_activate & cards_to_deactivate
        cards_to_activate = cards_to_activate - neutral_cards
        cards_to_deactivate = cards_to_deactivate - neutral_cards

        if len(neutral_cards) > 0:
            to_activate = neutral_cards.filtered(lambda c: c.activate_on >= c.deactivate_on)
            cards_to_activate = cards_to_activate + to_activate
            cards_to_deactivate = cards_to_deactivate + (neutral_cards - to_activate)

        cards_to_activate.write({'active': True})
        cards_to_deactivate.write({'active': False})


class HrRfidCardType(models.Model):
    _name = 'hr.rfid.card.type'
    _inherit = ['mail.thread']
    _description = 'Card Type'

    name = fields.Char(
        string='Nom du Type',
        help='Étiquette pour différencier les types avec',
        required=True,
        track_visibility='onchange',
    )

    card_ids = fields.One2many(
        'hr.rfid.card',
        'card_type',
        string='Cartes',
        help='Cartes de ce type de carte',
        context={'active_test': False},
    )

    door_ids = fields.One2many(
        'hr.rfid.door',
        'card_type',
        string='Portes',
        help="Les portes qui s'ouvriront à ce type de carte",
    )

    def unlink(self):
        default_card_type_id = self.env.ref('hr_rfid.hr_rfid_card_type_def').id

        for card_type in self:
            if card_type.id == default_card_type_id \
                    or len(card_type.card_ids) > 0 \
                    or len(card_type.door_ids) > 0:
                raise exceptions.ValidationError("Impossible de supprimer le type de carte par défaut ou une carte"
                                                  "type qui est déjà utilisé par les portes ou les cartes. "
                                                  "Veuillez d'abord changer les types de portes/cartes. ")

        return super(HrRfidCardType, self).unlink()

    def list_cards_from_this_type(self):
        self.ensure_one()
        return {
            'name': _('%s list' % self.name),
            'domain': [('card_type', '=', self.id)],
            # 'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'hr.rfid.card',
            'views': [[False, "tree"], [False, "form"]],
            'type': 'ir.actions.act_window',
            'context': {'active_test': False},
            # 'target': 'new',
        }


class HrRfidCardDoorRel(models.Model):
    _name = 'hr.rfid.card.door.rel'
    _description = 'Card and door relation model'

    card_id = fields.Many2one(
        'hr.rfid.card',
        string='Carte',
        required=True,
    )

    door_id = fields.Many2one(
        'hr.rfid.door',
        string='Porte',
        required=True,
        ondelete='cascade',
    )

    time_schedule_id = fields.Many2one(
        'hr.rfid.time.schedule',
        string='Horaire',
        required=True,
        ondelete='cascade',
    )

    @api.model
    def update_card_rels(self, card_id: HrRfidCard, access_group: models.Model = None):
        """
         Checks all card-door relations and updates them
         :param card_id: Card for which the relations to be checked
         :param access_group: Which access groups to go through when searching for the doors. If None will
         go through all access groups the owner of the card is in
         """
        potential_doors = card_id.get_potential_access_doors(access_group)
        for door, ts in potential_doors:
            self.check_relevance_fast(card_id, door, ts)

    @api.model
    def update_door_rels(self, door_id: models.Model, access_group: models.Model = None):
        """
        Checks all card-door relations and updates them
        :param door_id: Door for which the relations to be checked
        :param access_group: Which access groups to go through when searching for the cards. If None will
        go through all the access groups the door is in
        """
        potential_cards = door_id.get_potential_cards(access_group)
        for card, ts in potential_cards:
            self.check_relevance_fast(card, door_id, ts)

    @api.model
    def reload_door_rels(self, door_id: models.Model):
        door_id.card_rel_ids.unlink(create_cmd=False)
        self.update_door_rels(door_id)

    @api.model
    def check_relevance_slow(self, card_id: HrRfidCard, door_id: models.Model, ts_id: models.Model = None):
        """
        Check if card has access to door. If it does, create relation or do nothing if it exists,
        and if not remove relation or do nothing if it does not exist.
        :param card_id: Recordset containing a single card
        :param door_id: Recordset containing a single door
        :param ts_id: Optional parameter. If supplied, the relation will be created quicker.
        """
        card_id.ensure_one()
        door_id.ensure_one()

        if not card_id.card_ready():
            return

        potential_doors = card_id.get_potential_access_doors()
        found_door = False

        for door, ts in potential_doors:
            if door_id == door:
                if ts_id is not None and ts_id != ts:
                    raise exceptions.ValidationError('Cela ne devrait jamais arriver. Veuillez contacter les développeurs. +225 07 49 94 33 27')
                ts_id = ts
                found_door = True
                break
        if found_door and self._check_compat_n_rdy(card_id, door_id):
            self.create_rel(card_id, door_id, ts_id)
        else:
            self.remove_rel(card_id, door_id)

    @api.model
    def check_relevance_fast(self, card_id: HrRfidCard, door_id: models.Model, ts_id: models.Model = None):
        """
        Check if card is compatible with the door. If it is, create relation or do nothing if it exists,
        and if not remove relation or do nothing if it does not exist.
        :param card_id: Recordset containing a single card
        :param door_id: Recordset containing a single door
        :param ts_id: Optional parameter. If supplied, the relation will be created quicker.
        """
        card_id.ensure_one()
        door_id.ensure_one()
        if self._check_compat_n_rdy(card_id, door_id):
            self.create_rel(card_id, door_id, ts_id)
        else:
            self.remove_rel(card_id, door_id)

    @api.model
    def create_rel(self, card_id: HrRfidCard, door_id: models.Model, ts_id: models.Model = None):
        ret = self.search([
            ('card_id', '=', card_id.id),
            ('door_id', '=', door_id.id),
        ])
        if len(ret) == 0 and self._check_compat_n_rdy(card_id, door_id):
            if ts_id is None:
                acc_grs = card_id.get_owner().mapped('hr_rfid_access_group_ids').mapped('access_group_id')
                door_rels = acc_grs.mapped('all_door_ids')
                door_rel = None
                for rel in door_rels:
                    if rel.door_id == door_id:
                        door_rel = rel
                        break
                if door_rel is None:
                    raise exceptions.ValidationError('Pas moyen que cette carte ait accès à cette porte ??? 17512849')
                ts_id = door_rel.time_schedule_id

            self.create([{
                'card_id': card_id.id,
                'door_id': door_id.id,
                'time_schedule_id': ts_id.id,
            }])

    @api.model
    def remove_rel(self, card_id: models.Model, door_id: models.Model):
        ret = self.search([
            ('card_id', '=', card_id.id),
            ('door_id', '=', door_id.id),
        ])
        if len(ret) > 0:
            ret.unlink()

    def check_rel_relevance(self):
        for rel in self:
            self.check_relevance_slow(rel.card_id, rel.door_id)

    def time_schedule_changed(self, new_ts):
        self.time_schedule_id = new_ts

    def pin_code_changed(self):
        self._create_add_card_command()

    def card_number_changed(self, old_number):
        for rel in self:
            if old_number != rel.card_id.number:
                rel._create_remove_card_command(old_number)
                rel._create_add_card_command()

    def reload_add_card_command(self):
        self._create_add_card_command()

    @api.model
    def _check_compat_n_rdy(self, card_id, door_id):
        return card_id.door_compatible(door_id) and card_id.card_ready()

    def _create_add_card_command(self):
        cmd_env = self.env['hr.rfid.command']
        for rel in self:
            door_id = rel.door_id.id
            ts_id = rel.time_schedule_id.id
            pin_code = rel.card_id.pin_code
            card_id = rel.card_id.id
            cmd_env.add_card(door_id, ts_id, pin_code, card_id)

    def _create_remove_card_command(self, number: str = None, door_id: int = None):
        cmd_env = self.env['hr.rfid.command']
        for rel in self:
            if door_id is None:
                door_id = rel.door_id.id
            if number is None:
                number = rel.card_id.number[:]
            pin_code = rel.card_id.pin_code
            cmd_env.remove_card(door_id, pin_code, card_number=number)

    @api.constrains('door_id')
    def _door_constrains(self):
        for rel in self:
            if len(rel.door_id.access_group_ids) == 0:
                raise exceptions.ValidationError("La porte doit faire partie d'un groupe d'accès !")

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        records = self.env['hr.rfid.card.door.rel']

        for vals in vals_list:
            rel = super(HrRfidCardDoorRel, self).create([vals])
            records += rel
            rel._create_add_card_command()

        # if records.contact_id:
        #     records.sudo().write({
        #         'number': records.contact_id.barcode
        #     })

        # if records.employee_id:
        #     records.sudo().write({
        #         'number': records.employee_id.barcode
        #     })
        return records

    def write(self, vals):
        for rel in self:
            old_door = rel.door_id
            old_card = rel.card_id
            old_ts_id = rel.time_schedule_id

            super(HrRfidCardDoorRel, rel).write(vals)

            new_door = rel.door_id
            new_card = rel.card_id
            new_ts_id = rel.time_schedule_id

            if old_door != new_door or old_card != new_card:
                rel._create_remove_card_command(number=old_card.number, door_id=old_door.id)
                rel._create_add_card_command()
            elif old_ts_id != new_ts_id:
                rel._create_add_card_command()

    def unlink(self, create_cmd=True):
        if create_cmd:
            for rel in self:
                rel._create_remove_card_command()

        return super(HrRfidCardDoorRel, self).unlink()
