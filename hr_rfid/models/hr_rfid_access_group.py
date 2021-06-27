# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, _
import logging
import queue

_logger = logging.getLogger(__name__)


class HrRfidAccessGroup(models.Model):
    _name = 'hr.rfid.access.group'
    _inherit = ['mail.thread']
    _description = 'Access Group'

    def access_group_generate_name(self):
        env = self.env['hr.rfid.access.group'].search([])

        if len(env) == 0:
            return 'Access Group 1'
        else:
            return 'Access Group ' + str(env[-1].id + 1)

    name = fields.Char(
        string='Name',
        help="Une étiquette pour aider à différencier les groupes d'accès",
        default=access_group_generate_name,
        limit=32,
        track_visibility='onchange',
    )

    employee_ids = fields.One2many(
        'hr.rfid.access.group.employee.rel',
        'access_group_id',
        string='Utilisateurs',
        help="Utilisateurs faisant partie de ce groupe d'accès",
    )

    contact_ids = fields.One2many(
        'hr.rfid.access.group.contact.rel',
        'access_group_id',
        string='Contacts',
        help="Contacts faisant partie de ce groupe d'accès"
    )

    door_ids = fields.One2many(
        'hr.rfid.access.group.door.rel',
        'access_group_id',
        string='Portes',
        help="Portes incluses dans ce groupe d'accès",
    )

    default_department_ids = fields.One2many(
        'hr.department',
        'hr_rfid_default_access_group',
        string='Département (Par Défaut)',
        help="Départements qui ont ce groupe d'accès par défaut",
    )

    department_ids = fields.Many2many(
        'hr.department',
        string='Départements',
        help="Départements qui ont ce groupe d'accès par défaut",
    )

    inherited_ids = fields.Many2many(
        comodel_name='hr.rfid.access.group',
        relation='access_group_inheritance',
        column1='inheritor',
        column2='inherited',
        string="Groupes d'accès hérités",
    )

    inheritor_ids = fields.Many2many(
        comodel_name='hr.rfid.access.group',
        relation='access_group_inheritance',
        column1='inherited',
        column2='inheritor',
        string='Héritiers',
        help="Accéder aux groupes qui ont hérité de celui-ci",
    )

    all_door_ids = fields.Many2many(
        'hr.rfid.access.group.door.rel',
        string='Toutes les portes',
        help="Toutes les portes, y compris celles héritées",
        compute='_compute_all_doors',
    )

    all_employee_ids = fields.Many2many(
        'hr.rfid.access.group.employee.rel',
        string='Tous les employés',
        help="Tous les employés qui utilisent ce groupe d'accès, y compris ceux des héritiers",
        compute='_compute_all_employees',
    )

    all_contact_ids = fields.Many2many(
        'hr.rfid.access.group.contact.rel',
        string='Tous les contacts',
        help="Tous les contacts qui utilisent ce groupe d'accès, y compris ceux des héritiers",
        compute='_compute_all_contacts',
    )

    def add_doors(self, door_ids, time_schedule=None):
        if time_schedule is None:
            time_schedule = self.env.ref('hr_rfid.hr_rfid_time_schedule_0')

        rel_env = self.env['hr.rfid.access.group.door.rel']
        for door in door_ids:
            res = rel_env.search([ ('access_group_id', '=', self.id),
                                   ('door_id', '=', door.id) ])
            if len(res) == 1:
                if res.time_schedule_id != time_schedule:
                    res.time_schedule_id = time_schedule
            else:
                # if controller is of type iCON130 or iCON180
                if door.controller_id.hw_version in ['17', '10'] and time_schedule.number > 3:
                    raise exceptions.ValidationError(_('La porte %s ne peut utiliser que les 3 premiers horaires') %
                                                     door.name)
                rel_env.create([{
                    'access_group_id': self.id,
                    'door_id': door.id,
                    'time_schedule_id': time_schedule.id,
                }])
        self.check_for_ts_inconsistencies()

    def del_doors(self, door_ids):
        rel_env = self.env['hr.rfid.access.group.door.rel']
        for door in door_ids:
            rel_env.search([
                ('access_group_id', '=', self.id),
                ('door_id', '=', door.id)
            ]).unlink()

    @api.returns('hr.rfid.door')
    def get_all_doors(self):
        return self.mapped('all_door_ids').mapped('door_id')

    @api.returns('hr.employee')
    def get_all_employees(self):
        return self.mapped('all_employee_ids').mapped('employee_id')

    @api.returns('res.partner')
    def get_all_contacts(self):
        return self.mapped('all_contact_ids').mapped('contact_id')

    @api.constrains('door_ids')
    def door_ids_constrains(self):
        for acc_gr in self:
            door_id_list = []
            for rel in acc_gr.door_ids:
                if rel.door_id.id in door_id_list:
                    raise exceptions.ValidationError("Impossible de lier le groupe d'accès à une porte"
                                                      "il est déjà lié à.")

            relay_doors = dict()
            for rel in acc_gr.all_door_ids:
                ctrl = rel.door_id.controller_id
                if ctrl.is_relay_ctrl():
                    if ctrl in relay_doors and ctrl.mode == 3:
                        un_message = 'Les portes "%s" et "%s" appartiennent toutes deux à un contrôleur qui ne peut pas donner accès à plusieurs portes en même temps.'
                        raise exceptions.ValidationError(
                            _(un_message)
                            % (relay_doors[ctrl].name, rel.door_id.name)
                        )
                    relay_doors[ctrl] = rel.door_id

                door_id_list.append(rel.door_id.id)

    @api.depends('door_ids', 'inherited_ids')
    def _compute_all_doors(self):
        for acc_gr in self:
            door_ids = set()
            HrRfidAccessGroup._check_all_doors_rec(door_ids, [], acc_gr)
            acc_gr.all_door_ids = self.env['hr.rfid.access.group.door.rel'].browse(list(door_ids))

    @api.depends('employee_ids', 'inheritor_ids')
    def _compute_all_employees(self):
        for acc_gr in self:
            employee_ids = set()
            HrRfidAccessGroup._check_all_employees_rec(employee_ids, [], acc_gr)
            acc_gr.all_employee_ids = self.env['hr.rfid.access.group.employee.rel'].browse(list(employee_ids))

    @api.depends('contact_ids', 'inheritor_ids')
    def _compute_all_contacts(self):
        for acc_gr in self:
            contact_ids = set()
            HrRfidAccessGroup._check_all_contacts_rec(contact_ids, [], acc_gr)
            acc_gr.all_contact_ids = self.env['hr.rfid.access.group.contact.rel'].browse(list(contact_ids))

    @staticmethod
    def _check_all_doors_rec(door_ids: set, checked_ids: list, acc_gr):
        if acc_gr.id in checked_ids:
            return
        checked_ids.append(acc_gr.id)
        for door in acc_gr.door_ids:
            door_ids.add(door.id)
        for rec_gr in acc_gr.inherited_ids:
            HrRfidAccessGroup._check_all_doors_rec(door_ids, checked_ids, rec_gr)

    @staticmethod
    def _check_all_employees_rec(emp_ids: set, checked_ids: list, acc_gr):
        if acc_gr.id in checked_ids:
            return
        checked_ids.append(acc_gr.id)
        for employee in acc_gr.employee_ids:
            emp_ids.add(employee.id)
        for rec_gr in acc_gr.inheritor_ids:
            HrRfidAccessGroup._check_all_employees_rec(emp_ids, checked_ids, rec_gr)

    @staticmethod
    def _check_all_contacts_rec(contact_ids: set, checked_ids: list, acc_gr):
        if acc_gr.id in checked_ids:
            return
        checked_ids.append(acc_gr.id)
        for contact in acc_gr.contact_ids:
            contact_ids.add(contact.id)
        for rec_gr in acc_gr.inheritor_ids:
            HrRfidAccessGroup._check_all_contacts_rec(contact_ids, checked_ids, rec_gr)

    def check_for_ts_inconsistencies(self):
        def get_highest_acc_grs(_gr):
            if len(_gr.inheritor_ids) == 0:
                return _gr

            _hg = self.env['hr.rfid.access.group']
            for _acc_gr in _gr.inheritor_ids:
                if len(_acc_gr.inheritor_ids) == 0:
                    _hg += _acc_gr
                else:
                    _hg += get_highest_acc_grs(_acc_gr)
            return _hg
        
        def check_tses(_gr1, _gr2):
            _doors1 = _gr1.door_ids
            _doors2 = _gr2.door_ids
            _door_rel_env = self.env['hr.rfid.access.group.door.rel']
            _door_rel_env.check_for_ts_inconsistencies(_doors1, _doors2)

        def iterate_acc_grs(_gr, _checked_groups):
            for _gr2 in _gr.inherited_ids:
                if _gr2 in _checked_groups:
                    continue
                _checked_groups.append(_gr2)
                check_tses(_gr, _gr2)
                iterate_acc_grs(_gr2, _checked_groups)

        highest_groups = get_highest_acc_grs(self)
        for acc_gr in highest_groups:
            iterate_acc_grs(acc_gr, [])
        employees = self.all_employee_ids.mapped('employee_id')
        contacts = self.all_contact_ids.mapped('contact_id')
        employees.mapped(lambda r: r.check_for_ts_inconsistencies())
        contacts.mapped(lambda r: r.check_for_ts_inconsistencies())

    @api.constrains('inherited_ids')
    def _check_inherited_ids(self):
        env = self.env['hr.rfid.access.group']
        for acc_gr in self:
            group_order = []
            ret = HrRfidAccessGroup._check_inherited_ids_rec(acc_gr, [], group_order)
            if ret is True:
                err2 = ''
                for acc_gr_id in group_order:
                    acc_gr = env.browse(acc_gr_id)
                    err2 += '\n-> '
                    err2 += acc_gr.name
                err = _("Référence circulaire trouvée dans les groupes d'accès hérités : %s") % err2
                raise exceptions.ValidationError(err)

            acc_gr.check_for_ts_inconsistencies()

    @staticmethod
    def _check_inherited_ids_rec(acc_gr, visited_groups: list, group_order: list, orig_id=None):
        group_order.append(acc_gr.id)
        if acc_gr.id == orig_id:
            return True
        if orig_id is None:
            orig_id = acc_gr.id

        if acc_gr.id in visited_groups:
            return False

        visited_groups.append(acc_gr.id)

        for inh_gr in acc_gr.inherited_ids:
            res = HrRfidAccessGroup._check_inherited_ids_rec(inh_gr, visited_groups,
                                                                       group_order, orig_id)
            if res is True:
                return True

        group_order.pop()
        return False

    def _create_add_door_commands(self, doors):
        card_rel_env = self.env['hr.rfid.card.door.rel']
        employees = self.all_employee_ids.mapped('employee_id')
        contacts = self.all_contact_ids.mapped('contact_id')
        cards = employees.mapped('hr_rfid_card_ids') + contacts.mapped('hr_rfid_card_ids')
        for door in doors:
            for card in cards:
                card_rel_env.check_relevance_fast(card, door)

    def _create_remove_door_commands(self, doors):
        card_rel_env = self.env['hr.rfid.card.door.rel']
        employees = self.all_employee_ids.mapped('employee_id')
        contacts = self.all_contact_ids.mapped('contact_id')
        cards = employees.mapped('hr_rfid_card_ids') + contacts.mapped('hr_rfid_card_ids')
        for door in doors:
            for card in cards:
                card_rel_env.check_relevance_slow(card, door)

    def write(self, vals):
        for acc_gr in self:
            old_doors = self.all_door_ids.mapped('door_id')

            super(HrRfidAccessGroup, acc_gr).write(vals)

            new_doors = self.all_door_ids.mapped('door_id')

            added_doors = new_doors - old_doors
            removed_doors = old_doors - new_doors

            env = self.env['hr.rfid.access.group']
            completed_groups = [ ]
            acc_gr_to_complete = queue.Queue()
            acc_gr_to_complete.put(acc_gr.id)

            while not acc_gr_to_complete.empty():
                inh_id = acc_gr_to_complete.get()
                if inh_id in completed_groups:
                    continue
                completed_groups.append(inh_id)
                inh = env.browse(inh_id)
                HrRfidAccessGroup._create_add_door_commands(inh, added_doors)
                HrRfidAccessGroup._create_remove_door_commands(inh, removed_doors)

                for upper_inh in inh.inheritor_ids:
                    acc_gr_to_complete.put(upper_inh.id)

        return True

    def unlink(self):
        for acc_gr in self:
            acc_gr.door_ids.unlink()  # Unlinks the relations
            acc_gr.employee_ids.unlink()  # Unlinks the relations
            acc_gr.contact_ids.unlink()  # Unlinks the relations
        return super(HrRfidAccessGroup, self).unlink()


class HrRfidAccessGroupDoorRel(models.Model):
    _name = 'hr.rfid.access.group.door.rel'
    _description = 'Relation between access groups and doors'

    def _get_cur_access_group_id(self):
        return self.env['hr.rfid.access.group'].browse(self._context.get('active_id'))

    def _get_cur_door_id(self):
        return self.env.context.get('door_id', None)

    access_group_id = fields.Many2one(
        'hr.rfid.access.group',
        string="Groupe d'Accès",
        default=_get_cur_access_group_id,
        required=True,
    )

    door_id = fields.Many2one(
        'hr.rfid.door',
        string='Porte',
        default=_get_cur_door_id,
        required=True,
        ondelete='cascade',
    )

    time_schedule_id = fields.Many2one(
        'hr.rfid.time.schedule',
        string='Horaire',
        help="Horaire de la combinaison porte/groupe d'accès",
        default=lambda self: self.env.ref('hr_rfid.hr_rfid_time_schedule_0').id,
        required=True,
        ondelete='cascade',
    )

    @api.model
    def check_for_ts_inconsistencies(self, rels1, rels2):
        for door_rel in rels1:
            for door_rel2 in rels2[:]:
                if door_rel.door_id == door_rel2.door_id:
                    if door_rel.time_schedule_id != door_rel2.time_schedule_id:
                        un_message = "L'horaire ne correspond pas à la porte" + "'%s' dans les groupes d'accès '%s' et '%s'"
                        raise exceptions.ValidationError(
                            _(un_message)
                            % (door_rel.door_id.name, door_rel.access_group_id.name,
                               door_rel2.access_group_id.name))
                    rels2 -= door_rel2

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']

        records = super(HrRfidAccessGroupDoorRel, self).create(vals)

        records.mapped('access_group_id').door_ids_constrains()

        for rel in records:
            card_door_rel_env.update_door_rels(rel.door_id, rel.access_group_id)

        return records

    def write(self, vals):
        raise exceptions.ValidationError('Pas autorisé à écrire ici (hr.rfid.access.group.door.rel)')

    def unlink(self):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']
        for rel in self:
            door = rel.door_id
            cards = door.get_potential_cards(access_groups=rel.access_group_id)
            super(HrRfidAccessGroupDoorRel, rel).unlink()
            for card, ts in cards:
                card_door_rel_env.check_relevance_slow(card, door)


###
# Possible to have 'hr.rfid.access.group.employee.rel' and '...contact.rel' inherit another model,
# but then we'll have an empty table in the database. Better to just copy-paste a few fields i guess.
# Maybe there is a model that does not create a database table?
###

class HrRfidAccessGroupEmployeeRel(models.Model):
    _name = 'hr.rfid.access.group.employee.rel'
    _description = 'Relation between access groups and employees'

    access_group_id = fields.Many2one(
        'hr.rfid.access.group',
        string="Groupe d'Accès",
        required=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True,
    )

    expiration = fields.Datetime(
        string='Date Expiration',
        help="Le groupe d'accès se retirera de l'employé"
              "à la date d'expiration. N'expirera jamais si vide.",
        index=True,
    )

    @api.model
    def _check_expirations(self):
        self.search([
            ('expiration', '<=', fields.Datetime.now())
        ]).unlink()

    @api.constrains('employee_id', 'access_group_id')
    def _check_for_duplicates(self):
        for rel in self:
            duplicates = self.search([
                ('access_group_id', '=', rel.access_group_id.id),
                ('employee_id', '=', rel.employee_id.id),
            ])
            if len(duplicates) > 1:
                raise exceptions.ValidationError(
                    _("Les employés (%s) ne peuvent pas avoir deux fois le même groupe d'accès (%s) !")
                    % (rel.employee_id.name, rel.access_group_id.name))

    @api.model
    @api.model_create_multi
    def create(self, vals_list):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']

        records = super(HrRfidAccessGroupEmployeeRel, self).create(vals_list)
        records.mapped('employee_id').check_access_group()
        
        for rel in records:
            cards = rel.employee_id.hr_rfid_card_ids
            for card in cards:
                card_door_rel_env.update_card_rels(card, rel.access_group_id)

        return records

    def write(self, vals):
        if 'employee_id' in vals:
            raise exceptions.ValidationError("Impossible de changer l'employé de la relation !")
        card_door_rel_env = self.env['hr.rfid.card.door.rel']
        for rel in self:
            old_acc_gr = rel.access_group_id
            super(HrRfidAccessGroupEmployeeRel, rel).write(vals)
            new_acc_gr = rel.access_group_id

            rel.employee_id.check_access_group()

            if new_acc_gr != old_acc_gr:
                # Potentially remove old rels
                cards = rel.employee_id.hr_rfid_card_ids
                doors = old_acc_gr.all_door_ids.mapped('door_id')
                for card in cards:
                    for door in doors:
                        card_door_rel_env.check_relevance_slow(card, door)

                # Potentially create new rels
                cards = rel.employee_id.hr_rfid_card_ids
                for card in cards:
                    card_door_rel_env.update_card_rels(card, new_acc_gr)

    def unlink(self):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']

        for rel in self:
            cards = rel.employee_id.hr_rfid_card_ids
            doors = rel.access_group_id.all_door_ids.mapped('door_id')
            super(HrRfidAccessGroupEmployeeRel, rel).unlink()
            for card in cards:
                for door in doors:
                    card_door_rel_env.check_relevance_slow(card, door)


class HrRfidAccessGroupContactRel(models.Model):
    _name = 'hr.rfid.access.group.contact.rel'
    _description = 'Relation between access groups and contacts'

    access_group_id = fields.Many2one(
        'hr.rfid.access.group',
        string="Groupe d'Accès",
        required=True,
    )

    contact_id = fields.Many2one(
        'res.partner',
        string='Contact',
        required=True,
    )

    expiration = fields.Datetime(
        string="Date Expiration",
        help="Le groupe d'accès se retirera du contact "
              "à la date d'expiration. N'expirera jamais si vide.",
        index=True,
    )

    @api.model
    def _check_expirations(self):
        self.search([
            ('expiration', '<=', fields.Datetime.now())
        ]).unlink()

    @api.constrains('contact_id', 'access_group_id')
    def _check_for_duplicates(self):
        for rel in self:
            duplicates = self.search([
                ('access_group_id', '=', rel.access_group_id.id),
                ('contact_id', '=', rel.contact_id.id),
            ])
            if len(duplicates) > 1:
                raise exceptions.ValidationError(
                    _("Les employés (%s) ne peuvent pas avoir le même groupe d'accès (%s) deux fois !")
                    % (rel.contact_id.name, rel.access_group_id.name))

    @api.model
    @api.model_create_multi
    def create(self, vals_list):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']

        records = super(HrRfidAccessGroupContactRel, self).create(vals_list)
        records.mapped('contact_id').check_access_group()

        for rel in records:
            cards = rel.contact_id.hr_rfid_card_ids
            for card in cards:
                card_door_rel_env.update_card_rels(card, rel.access_group_id)

        return records

    def write(self, vals):
        if 'contact_id' in vals:
            raise exceptions.ValidationError("Impossible de changer l'employé de la relation !")
        card_door_rel_env = self.env['hr.rfid.card.door.rel']
        for rel in self:
            old_acc_gr = rel.access_group_id
            super(HrRfidAccessGroupContactRel, rel).write(vals)
            new_acc_gr = rel.access_group_id

            rel.contact_id.check_access_group()

            if new_acc_gr != old_acc_gr:
                # Potentially remove old rels
                cards = rel.contact_id.hr_rfid_card_ids
                doors = old_acc_gr.all_door_ids.mapped('door_id')
                for card in cards:
                    for door in doors:
                        card_door_rel_env.check_relevance_slow(card, door)

                # Potentially create new rels
                cards = rel.contact_id.hr_rfid_card_ids
                for card in cards:
                    card_door_rel_env.update_card_rels(card, new_acc_gr)

    def unlink(self):
        card_door_rel_env = self.env['hr.rfid.card.door.rel']

        for rel in self:
            cards = rel.contact_id.hr_rfid_card_ids
            doors = rel.access_group_id.all_door_ids.mapped('door_id')
            super(HrRfidAccessGroupContactRel, rel).unlink()
            for card in cards:
                for door in doors:
                    card_door_rel_env.check_relevance_slow(card, door)


class HrRfidAccessGroupWizard(models.TransientModel):
    _name = 'hr.rfid.access.group.wizard'
    _description = 'Add or remove doors to the access group'

    def _default_acc_gr(self):
        return self.env['hr.rfid.access.group'].browse(self._context.get('active_ids'))

    def _default_acc_gr_doors(self):
        acc_gr = self._default_acc_gr()
        doors = self.env['hr.rfid.door']
        for door_rel in acc_gr.door_ids:
            doors += door_rel.door_id
        return doors

    acc_gr_id = fields.Many2many(
        'hr.rfid.access.group',
        string="Groupe d'Accès",
        required=True,
        default=_default_acc_gr,
    )

    door_ids = fields.Many2many(
        'hr.rfid.door',
        'my_door_ids',
        'wiz',
        'door',
        string='Portes',
        help="Quelles portes ajouter au groupe d'accès",
        required=True,
    )

    acc_gr_doors = fields.Many2many(
        'hr.rfid.door',
        'custom_door_ids',
        'wiz',
        'door',
        string="Toutes les portes de groupe d'accès",
        default=_default_acc_gr_doors,
    )

    time_schedule_id = fields.Many2one(
        'hr.rfid.time.schedule',
        string='Horaire',
        help="Horaire de la combinaison porte/groupe d'accès",
        required=True,
        default=lambda self: self.env.ref('hr_rfid.hr_rfid_time_schedule_0').id,
    )

    def add_doors(self):
        self.ensure_one()
        self.acc_gr_id.add_doors(self.door_ids, self.time_schedule_id)

    def del_doors(self):
        self.ensure_one()
        self.acc_gr_id.del_doors(self.door_ids)
