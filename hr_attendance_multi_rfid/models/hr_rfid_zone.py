# -*- coding: utf-8 -*-
from odoo import models, api, fields, exceptions


class HrRfidZone(models.Model):
    _inherit = 'hr.rfid.zone'

    attendance = fields.Boolean(
        string='Présence',
        help="La zone suivra la fréquentation si elle est cochée.",
        default=False,
    )

    overwrite_check_in = fields.Boolean(
        string="Écraser l'enregistrement",
        help="Si un utilisateur s'est déjà enregistré et entre également dans cette zone, écrasez l'heure de l'enregistrement",
        default=False,
    )

    overwrite_check_out = fields.Boolean(
        string='Écraser le check-out',
        help="Si un utilisateur a déjà vérifié et quitte également cette zone, écrasez l'heure de la vérification",
        default=False,
    )


    def person_entered(self, person, event):
        if not isinstance(person, type(self.env['hr.employee'])):
            return super(HrRfidZone, self).person_entered(person, event)

        for zone in self:
            if zone.attendance is False:
                continue

            if person in zone.employee_ids and zone.overwrite_check_in:
                check = self.env['hr.attendance'].search([('employee_id', '=', person.id)], limit=1)
                if check.check_out:
                    continue
                event.in_or_out = 'in'
                check.check_in = event.event_time
            elif person not in zone.employee_ids and person.attendance_state == 'checked_out':
                event.in_or_out = 'in'
                person.attendance_action_change_with_date(event.event_time)
        return super(HrRfidZone, self).person_entered(person, event)

    def person_left(self, person, event):
        if not isinstance(person, type(self.env['hr.employee'])):
            return super(HrRfidZone, self).person_left(person, event)

        for zone in self:
            if not zone.attendance:
                continue

            if person not in zone.employee_ids and zone.overwrite_check_out:
                check = self.env['hr.attendance'].search([('employee_id', '=', person.id)], limit=1)
                if event:
                    event.in_or_out = 'out'
                    check.check_out = event.event_time
                else:
                    check.check_out = fields.datetime.now()
            elif person in zone.employee_ids and person.attendance_state == 'checked_in':
                if event:
                    event.in_or_out = 'out'
                    person.attendance_action_change_with_date(event.event_time)
                else:
                    person.attendance_action_change_with_date(fields.datetime.now())

        return super(HrRfidZone, self).person_left(person, event)