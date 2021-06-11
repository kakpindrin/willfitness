# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
import time
from odoo.exceptions import Warning, UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    conge_non_exceptionne = fields.Boolean('Congé non exceptionnel')
    montant_conge = fields.Float('Montant')
    motif_conge = fields.Text('Motif de la demande')

    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].browse(vals['employee_id'])
        status = self.env['hr.leave.type'].browse(vals['holiday_status_id'])
        if status.code == 'CONG' and employee.contract_id.an_anciennete < 1:
            raise Warning(_("Attention ! Cet employé ne peut pas bénéficier de ce type de congés"))
        if status.number_of_days < vals['number_of_days'] and status.number_of_days != 0:
            raise Warning(_("Attention !  le nombre de jours de congés pour ce type ne doit pas depassé {0}".format(
                status.number_of_days)))
        # date_attribution = time.strftime('%Y-%m-01')[:4]
        # vals.update({"year_attribution": date_attribution})
        # print(vals)
        return super(HrLeave, self).create(vals)


class HrTypeAttributionHolidays(models.Model):
    _name = "hr.type.attribution.holidays"
    _description = "Type d'attribution de conges"

    name = fields.Char("Libellé", size=128, required=True)
    code = fields.Char('Code', size=3, required=True)
    taux = fields.Float("Taux de calcul",required=True)


class HrDays(models.Model):
    _name = "hr.days"
    _description = 'Les jours'

    name = fields.Char('Libéllé', size=128, required=True)
    sequence = fields.Integer('Sequence',required=True)


class HrHolidaysHays(models.Model):
    _name = "hr.leaves.days"
    _description = "The leaves"

    name = fields.Char("Name", size=128, required=True)
    date_holidays = fields.Date("Date")
    description = fields.Text("Description")


class ResourceCalandar(models.Model):
    _inherit = "resource.calendar"

    days_ids = fields.Many2many('hr.days', 'resource_days_rel', 'resource_id', 'days_id', 'Label')


class HrLeavesType(models.Model):
    _inherit = 'hr.leave.type'

    number_of_days = fields.Integer("Nombre de jours")
