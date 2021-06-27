# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions, http, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hr_rfid_pin_code = fields.Char(
        string='Code PIN Utilisateur',
        help="Code PIN pour cet utilisateur, quatre zéros signifient que l'utilisateur n'a pas de code PIN.",
        limit=4,
        default='0000',
        track_visibility='onchange',
    )

    hr_rfid_access_group_ids = fields.One2many(
        'hr.rfid.access.group.employee.rel',
        'employee_id',
        string="Groupes d'Accès",
        help="De quels groupes d'accès l'utilisateur fait-il partie",
        track_visibility='onchange',
    )

    hr_rfid_card_ids = fields.One2many(
        'hr.rfid.card',
        'employee_id',
        string='Carte RFID',
        help='Cartes appartenant à cet employé',
        context = {'active_test': False},
    )

    hr_rfid_event_ids = fields.One2many(
        'hr.rfid.event.user',
        'employee_id',
        string='Évènements RFID',
        help='Évènements concernat cet employé',
    )

    def add_acc_gr(self, access_groups, expiration=None):     
        rel_env = self.env['hr.rfid.access.group.employee.rel']
        for emp in self:
            for acc_gr in access_groups:
                rel = rel_env.search([
                    ('employee_id', '=', emp.id),
                    ('access_group_id', '=', acc_gr.id),
                ])
                if rel:
                    rel.expiration = expiration
                    continue
                emp.check_for_ts_inconsistencies_when_adding(acc_gr)
                creation_dict = {
                    'employee_id': emp.id,
                    'access_group_id': acc_gr.id,
                }
                if expiration is not None and expiration is not False:
                    creation_dict['expiration'] = str(expiration)
                rel_env.create(creation_dict)

    def remove_acc_gr(self, access_groups):
        rel_env = self.env['hr.rfid.access.group.employee.rel']
        rel_env.search([
            ('employee_id', 'in', self.ids),
            ('access_group_id', 'in', access_groups.ids)
        ]).unlink()

    @api.returns('hr.rfid.door')
    def get_doors(self, excluding_acc_grs=None, including_acc_grs=None):
        if excluding_acc_grs is None:
            excluding_acc_grs = self.env['hr.rfid.access.group']
        if including_acc_grs is None:
            including_acc_grs = self.env['hr.rfid.access.group']

        acc_grs = self.hr_rfid_access_group_ids.mapped('access_group_id')
        acc_grs = acc_grs - excluding_acc_grs
        acc_grs = acc_grs + including_acc_grs
        return acc_grs.mapped('all_door_ids').mapped('door_id')

    def check_for_ts_inconsistencies_when_adding(self, new_acc_grs):
        acc_gr_door_rel_env = self.env['hr.rfid.access.group.door.rel']
        acc_grs = self.hr_rfid_access_group_ids.mapped('access_group_id')
        for acc_gr1 in acc_grs:
            for acc_gr2 in new_acc_grs:
                door_rels1 = acc_gr1.all_door_ids
                door_rels2 = acc_gr2.all_door_ids
                acc_gr_door_rel_env.check_for_ts_inconsistencies(door_rels1, door_rels2)

    def check_for_ts_inconsistencies(self):
        acc_gr_door_rel_env = self.env['hr.rfid.access.group.door.rel']
        acc_grs = self.hr_rfid_access_group_ids.mapped('access_group_id')
        for i in range(len(acc_grs)):
            for j in range(i+1, len(acc_grs)):
                door_rels1 = acc_grs[i].all_door_ids
                door_rels2 = acc_grs[j].all_door_ids
                acc_gr_door_rel_env.check_for_ts_inconsistencies(door_rels1, door_rels2)

    @api.constrains('hr_rfid_access_group_ids')
    def check_access_group(self):
        for user in self:
            user.check_for_ts_inconsistencies()

            for acc_gr_rel in user.hr_rfid_access_group_ids:
                acc_gr = acc_gr_rel.access_group_id
                if acc_gr not in user.department_id.hr_rfid_allowed_access_groups:
                    raise exceptions.ValidationError("Le groupe d'accès doit être l'un des accès"
                                                      "groupes affectés au département !")

            doors = user.hr_rfid_access_group_ids.mapped('access_group_id')\
                .mapped('all_door_ids').mapped('door_id')
            relay_doors = dict()
            for door in doors:
                ctrl = door.controller_id
                if ctrl.is_relay_ctrl():
                    if ctrl in relay_doors and ctrl.mode == 3:
                        raise exceptions.ValidationError(
                            _('Les portes "%s" et "%s" appartiennent toutes deux à un contrôleur qui ne peut pas donner accès à plusieurs portes en même temps.')
                            % (relay_doors[ctrl].name, door.name)
                        )
                    relay_doors[ctrl] = door

    @api.constrains('hr_rfid_pin_code')
    def _check_pin_code(self):
        for user in self:
            pin = user.hr_rfid_pin_code
            if len(pin) != 4:
                raise exceptions.ValidationError('Pin code must have exactly 4 characters')

            # If char is not a valid decimal number, int(char, 10) will raise an error
            try:
                for char in str(pin):
                    int(char, 10)
            except ValueError:
                raise exceptions.ValidationError('Invalid pin code, digits must be from 0 to 9')

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        records = super(HrEmployee, self).create(vals_list)

        for rec in records:
            rec.add_acc_gr(rec.department_id.hr_rfid_default_access_group)

        return records

    def write(self, vals):
        for user in self:
            old_pin_code = user.hr_rfid_pin_code[:]
            old_dep = user.department_id

            super(HrEmployee, user).write(vals)

            new_pin_code = user.hr_rfid_pin_code
            new_dep = user.department_id

            if old_dep != new_dep:
                new_dep_acc_grs = new_dep.hr_rfid_allowed_access_groups
                for acc_gr_rel in user.hr_rfid_access_group_ids:
                    if acc_gr_rel.access_group_id not in new_dep_acc_grs:
                        acc_gr_rel.unlink()
                if new_dep.hr_rfid_default_access_group:
                    user.add_acc_gr(new_dep.hr_rfid_default_access_group)

            if old_pin_code != new_pin_code:
                user.hr_rfid_card_ids.mapped('door_rel_ids').pin_code_changed()

    def unlink(self):
        for emp in self:
            emp.hr_rfid_card_ids.unlink()
            emp.hr_rfid_access_group_ids.unlink()
        return super(HrEmployee, self).unlink()

    def log_person_out(self, sids=None):
        for emp in self:
            if not emp.user_id:
                continue
            user = emp.user_id
            session_storage = http.root.session_store
            if sids is None:
                sids = session_storage.list()
            for sid in sids:
                session = session_storage.get(sid)
                if session['uid'] == user.id:
                    session_storage.delete(session)


class HrEmployeeDoors(models.TransientModel):
    _name = 'hr.rfid.employee.doors.wiz'
    _description = "Display doors employee has access to"

    def _default_employee(self):
        return self.env['hr.employee'].browse(self._context.get('active_ids'))

    def _default_doors(self):
        return self._default_employee().get_doors()

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True,
        default=_default_employee,
    )

    door_ids = fields.Many2many(
        'hr.rfid.door',
        string='Portes',
        required=True,
        default=_default_doors,
    )
