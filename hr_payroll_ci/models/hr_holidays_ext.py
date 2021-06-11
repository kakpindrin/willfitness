# -*- coding: utf-8 -*-
##############################################################################
#
#    hr_holidays_extensions Odoo 8
#    Copyright (c) 2018 Copyright (c) 2018 aek
#      Anicet Eric Kouame <anicetkeric@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import math
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from odoo import fields, models, api
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import Warning, UserError

from odoo.tools.safe_eval import safe_eval as eval

#
# class hr_type_attribution_holidays(models.Model):
#     _name="hr.type.attribution.holidays"
#     _description = "Type d'attribution de conges"
#
#     name = fields.Char("Libellé",size=128,required=True)
#     code = fields.Char('Code', size=3, required=True)
#     taux = fields.Float("Taux de calcul",required=True)
#
#
# class hr_days(models.Model):
#     _name="hr.days"
#     _description = 'Les jours'
#
#     name = fields.Char('Libéllé',size=128,required=True)
#     sequence = fields.Integer('Sequence',required=True)
#
#
# class hr_holidays_days(models.Model):
#     _name="hr.holidays.days"
#     _description="The holidays "
#
#     name = fields.Char("Name",size=128,required=True)
#     date_holidays = fields.Date("Date")
#     description = fields.Text("Description")


# class resource_calandar(models.Model):
#     _inherit = "resource.calendar"
#
#     days_ids = fields.Many2many('hr.days', 'resource_days_rel', 'resource_id', 'days_id', 'Label')


# class hr_holidays_status(models.Model):
#     _inherit = 'hr.holidays.status'
#
#     code = fields.Char("Code",siez="5",required=True)
#     number_of_days = fields.Integer("Nombre de jours")


class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].browse(vals['employee_id'])
        status = self.env['hr.holidays.status'].browse(vals['holiday_status_id'])
        # hhstatus_obj=self.pool.get('hr.holidays.status')
        # employee=hremp_obj.browse(cr,uid,vals['employee_id'],context)
        # status=hhstatus_obj.browse(cr,uid,vals['holiday_status_id'],context)
        if status.code =='CONG' and employee.contract_id.an_anciennete < 1 and vals['type'] == 'add':
            raise Warning(_("Attention ! Cet employé ne peut pas bénéficier de ce type de congés"))
        if status.number_of_days < vals['number_of_days_temp'] and status.number_of_days != 0:
            raise Warning(_("Attention !  le nombre de jours de congés pour ce type ne doit pas depassé {0}".format(status.number_of_days)))
        date_attribution=time.strftime('%Y-%m-01')[:4]
        vals.update({"year_attribution": date_attribution})
        print(vals)
        return super(hr_holidays, self).create(vals)
    
    def get_employee_for_leave(self,):
        he_obj=self.env["hr.employee"]
        self.cr.execute("SELECT id FROM hr_employee")
        he_ids=[]
        results=self.cr.fetchall()
        if results :
            he_ids=[res[0] for res in results]
        hr_employee=he_obj.browse(he_ids)
        list_employee=[]
        for emp in hr_employee:
            if emp.contract_id and emp.contract_id.an_anciennete>=1:
                list_employee+=[emp.id]
        if not list_employee:
            raise Warning("Attention Il faut qu'un de vos employés ait au moins un an d'anciennété")
        else :
            return {'domain':{'employee_id':[('id','in',list_employee)]}}
    
    def get_all_employee(self):
        he_obj=self.env["hr.employee"]
        self.cr.execute("SELECT id FROM hr_employee")
        he_ids=[]
        results=self.cr.fetchall()
        if results :
            he_ids=[res[0] for res in results]
        return {'domain':{'employee_id':[('id','in',he_ids)]}}
    
    def _get_year_attribution(self):
        raise Warning(_('Test',time.strftime('%Y-%m-01')))

    def _get_number_of_hours(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = float(timedelta.seconds)/3600
        return diff_day
    
    def get_number_of_day_by_periode(self, employee_id,date_from,date_to):
        hld_res=[]
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        employee=self.pool.get('hr.employee').browse(employee_id)
        days_ids=employee.contract_id.working_hours.days_ids
        from_dt = datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        day_temp = timedelta.days + float(timedelta.seconds) / 86400
        diff_day = int(round(math.floor(day_temp))+1)
        total_day=0
        number_of_day=0
        if (employee_id and date_from and date_to):
            self.cr.execute("select SUM(number_of_days_temp) from hr_holidays where employee_id=%s and type='remove' and state='validate'"
                " and (date_from between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))"
                " and (date_to between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))",(employee_id,date_from,date_to,date_from,date_to,))
            results=self.cr.fetchall()
            if results :
                number_of_day+=results[0]
            
            self.cr.execute("select id as id from hr_holidays where employee_id=%s and type='remove' and state='validate'"
                       " and (date_from between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) and "
                       "(date_to >to_date(%s,'yyyy-mm-dd'))",(employee_id,date_from,date_to,date_to))
            results=self.cr.fetchall()
            if results:
                print("ok")
            else:
                raise Warning(_('Testons', results))
        
    number_of_hours = fields.Float("Nombre d'heures")
    year_attribution = fields.Char("Année",size=10)


class hr_employee(models.Model):
    _inherit="hr.employee"
    
    def calcul_remaing_days(self):
        date_attribution=time.strftime('%Y-%m-%d')
        holiday_obj=self.env['hr.holidays']
        hr_emp_obj = self.env['hr.employee']
        holiday_status_obj = self.env['hr.holidays.status']
        company_obj = self.env['res.company']
        hr_emp_ids=hr_emp_obj.search([('date_next_attribution','=',date_attribution)])
        company=company_obj.browse(1)
        holiday_status=holiday_status_obj.search([('code','=','CONG')])
        for emp in self.browse(hr_emp_ids):
            values={
                    'type':'add',
                    'number_of_days_temp':company.base_holidays,
                    'employee_id':emp.id,
                    'name':'Attribution de jours de congés pour le mois de Test',
                    'holiday_status_id':holiday_status[0],
                    'state':'validate',
                }
            holidays_id=holiday_obj.create(values)
            holiday_obj.write(holidays_id,{'state':'validate'})
            date_next_attribution=str(datetime.now() + relativedelta.relativedelta(months=+1))[:10]
            self.write({'date_next_attribution':date_next_attribution})

    def get_holiday_status(self):
        hhs_obj = self.env["hr.holidays.status"]
        hh_obj = self.env["hr.holidays"]
        date_attribution = time.strftime('%Y-%m-01')[:4]
        hh_status_id = hhs_obj.search([('code','=','CONG')])
        hholiday_id = hh_obj.search([('year_attribution','=',date_attribution),('type','=','add'),
                ('state','=','validate'),('holiday_status_id','in',hh_status_id),("employee_id",'=',self.id)])
        if hholiday_id:
            hholiday=hh_obj.browse(hholiday_id[0])
            return hholiday.holiday_status_id
        else:
            return False

    @api.multi
    def _get_max_leave(self):
        res={}
        hhs_obj=self.env["hr.holidays.status"]
        for i in self:
            hh_status=self.get_holiday_status()
            if hh_status:
                res[i.id]=hh_status.max_leaves
        return res
    
    def _get_taken_leave(self):
        res={}
        hhs_obj=self.pool.get("hr.holidays.status")
        for i in self:
            hh_status = self.get_holiday_status()
            if hh_status:
                res[i.id]=hh_status.remaining_leaves
        return res

    def get_date_retour_conges(self):
        holidays_obj = self.env['hr.holidays']
        hhs_obj = self.env["hr.holidays.status"]
        hol_status_id = hhs_obj.search([('code','=','CONG')])[0]
        date_from = time.strftime('%Y-%m-01')
        date_to=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]
        for emp in self:
            holidays_ids=holidays_obj.search([('employee_id','=',emp.id),('holiday_status_id','=',hol_status_id),
                                              ('type','=','remove'),('state','=','validate'),
                                              ('date_to','<=',str(datetime.now())[:10]),
                                              ('date_to','<',date_from)], order='date_to')
            if holidays_ids:
                holiday=holidays_obj.browse(holidays_ids[len(holidays_ids)-1])
                return holiday.date_to
            else:
                return emp.date_embauche
    
    def _get_date_retour_conges(self):
        res={}
        for emp in self:
            res[emp.id]=self.get_date_retour_conges()
        return res

    def get_montant_by_periode_reference(self):
        slip_obj = self.env['hr.payslip']
        montant = 0
        for emp in self:
            if emp.contract_id.date_start and not emp.date_retour_conge:
                payslip = slip_obj.search([('employee_id', '=', emp.id), ('date_from', '>=', emp.contract_id.date_start)])
                # payslip = slip_obj.browse(slip_ids)
                number = len(payslip)
                print(number)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    SMM = round(montant / 12)
                    return SMM
            elif emp.date_retour_conge and emp.contract_id.date_start and not emp.debut_rupture:
                print(emp.date_retour_conge)
                payslips = slip_obj.search([('employee_id', '=', emp.id), ('date_from', '>=', emp.date_retour_conge)])
                payslip = slip_obj.browse(payslips)
                number = len(payslip)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    SMM = round(montant / 12)
                    return SMM
            elif emp.contract_id.date_start and emp.contract_id.date_end:
                print(emp.date_retour_conge)
                payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                   ('date_from', '>=', emp.contract_id.date_start),
                                                   ('date_from', '<=', emp.contract_id.date_end)])
                payslip = slip_obj.browse(payslips)
                number = len(payslip)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    SMM = round(montant / 12)
                    return SMM
            elif emp.date_retour_conge and emp.debut_rupture:
                payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                    ('date_from', '>=', emp.date_retour_conge),
                                                    ('date_from', '<=', emp.debut_rupture)])
                payslip = slip_obj.browse(payslips)
                if payslip != 0:
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    SMM = round(montant / 12)
                    return SMM

    @api.multi
    def _get_montant_by_periode_reference(self):
        # res={}
        for emp in self:
            res = emp.get_montant_by_periode_reference()
            emp.montant_moyen_mensuel = res
            return res

    def get_montant_moyen_journalier(self):
        slip_obj = self.env['hr.payslip']
        montant = 0
        for emp in self:
            if emp.contract_id.date_start and not emp.date_retour_conge:
                payslip = slip_obj.search([('employee_id', '=', emp.id),('date_from', '>=', emp.contract_id.date_start)])
                # payslip = slip_obj.browse(slip_ids)
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ
            elif emp.date_retour_conge and emp.contract_id.date_start and not emp.debut_rupture:
                payslips = slip_obj.search([('employee_id', '=', emp.id), ('date_from', '>=', emp.date_retour_conge)])
                payslip = slip_obj.browse(payslips)
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ
            elif emp.contract_id.date_start and emp.contract_id.date_end:
                print(emp.date_retour_conge)
                payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                   ('date_from', '>=', emp.contract_id.date_start),
                                                   ('date_from', '<=', emp.contract_id.date_end)])
                payslip = slip_obj.browse(payslips)
                if payslip != 0:
                    worked_days_number = list()
                    for slip in payslip:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslip:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ
            elif emp.date_retour_conge and emp.debut_rupture:
                payslips = slip_obj.search([('employee_id', '=', emp.id),
                                                    ('date_from', '>=', emp.date_retour_conge),
                                                    ('date_from', '<=', emp.debut_rupture)])
                # payslip = slip_obj.browse(payslips)
                if payslips != 0:
                    worked_days_number = list()
                    for slip in payslips:
                        worked_days_line_ids = slip.worked_days_line_ids
                        if worked_days_line_ids:
                            for line in worked_days_line_ids:
                                if 0 < line.number_of_days < 30:
                                    worked_days_number.append(line.number_of_days)
                                if line.number_of_days >= 30:
                                    worked_days_number.append(line.number_of_days)
                    for slip in payslips:
                        for line in slip.line_ids:
                            if line.code == 'BRUT':
                                montant += line.total
                    nwd = sum(worked_days_number)
                    SMJ = round(montant / nwd) if nwd > 0 else 0.0
                    return SMJ

    def _get_montant_moyen_journalier(self):
        res = {}
        for emp in self:
            res = emp.get_montant_moyen_journalier()
        return res

    def _set_remaining_days(self, empl_id, value):
        employee = self.browse(empl_id)
        diff = value - employee.remaining_leaves
        type_obj = self.env['hr.holidays.status']
        holiday_obj = self.env['hr.holidays']
        # Find for holidays status
        status_ids = type_obj.search([('limit', '=', False)])
        if len(status_ids) != 1:
            raise Warning(_("Warning! The feature behind the field 'Remaining Legal Leaves' can only be used when there is only one leave type with the option 'Allow to Override Limit' unchecked. (%s Found). Otherwise, the update is ambiguous as we cannot decide on which leave type the update has to be done. \nYou may prefer to use the classic menus 'Leave Requests' and 'Allocation Requests' located in 'Human Resources \ Leaves' to manage the leave days of the employees if the configuration does not allow to use this field.") % (len(status_ids)))
        status_id = status_ids and status_ids[0] or False
        if not status_id:
            return False
        if diff > 0:
            leave_id = holiday_obj.create({'name': _('Allocation for %s') % employee.name, 'employee_id': employee.id, 'holiday_status_id': status_id, 'type': 'add', 'holiday_type': 'employee', 'number_of_days_temp': diff})
        elif diff < 0:
            raise Warning(_('Warning! You cannot reduce validated allocation requests'))
        else:
            return False
        for sig in ('confirm', 'validate', 'second_validate'):
            holiday_obj.signal_workflow([leave_id], sig)
        return True


    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                hr_holidays h
                join hr_holidays_status s ON (s.id=h.holiday_status_id)
            WHERE
                h.state='validate' AND
                s.limit=False AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (tuple(self.ids),))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())

    @api.multi
    def _compute_remaining_leaves(self):
        remaining = self._get_remaining_leaves()
        for employee in self:
            employee.remaining_leaves = remaining.get(employee.id, 0.0)

    # def _get_remaining_days(self):
    #     ids = self.env['hr.employee'].search([()])
    #     self.cr.execute("""SELECT
    #             sum(h.number_of_days) as days,
    #             h.employee_id
    #         from
    #             hr_holidays h
    #             join hr_holidays_status s on (s.id=h.holiday_status_id)
    #         where
    #             h.state='validate' and
    #             s.limit=False and
    #             h.employee_id in %s
    #         group by h.employee_id""", (tuple(self.ids),))
    #     res = self.cr.dictfetchall()
    #     remaining = {}
    #     diff = 0
    #     for r in res:
    #         employee = self.browse(r['employee_id'])
    #         days = employee.conge_exceptionnel
    #         days2 = employee.conge_non_exceptionnel
    #         if days > 10:
    #             diff = days - 10
    #         remaining[r['employee_id']] = r['days'] - diff - days2
    #     for employee_id in ids:
    #         if not remaining.get(employee_id):
    #             remaining[employee_id] = 0.0
    #     return remaining

    @api.multi
    def _inverse_remaining_leaves(self):
        status_list = self.env['hr.holidays.status'].search([('limit', '=', False)])
        # Create leaves (adding remaining leaves) or raise (reducing remaining leaves)
        actual_remaining = self._get_remaining_leaves()
        for employee in self.filtered(lambda employee: employee.remaining_leaves):
            # check the status list. This is done here and not before the loop to avoid raising
            # exception on employee creation (since we are in a computed field).
            if len(status_list) != 1:
                raise UserError(
                    _("The feature behind the field 'Remaining Legal Leaves' can only be used when there is only one "
                      "leave type with the option 'Allow to Override Limit' unchecked. (%s Found). "
                      "Otherwise, the update is ambiguous as we cannot decide on which leave type the update has to be done. "
                      "\n You may prefer to use the classic menus 'Leave Requests' and 'Allocation Requests' located in Leaves Application "
                      "to manage the leave days of the employees if the configuration does not allow to use this field.") % (
                        len(status_list)))
            status = status_list[0] if status_list else None
            if not status:
                continue
            # if a status is found, then compute remaing leave for current employee
            difference = employee.remaining_leaves - actual_remaining.get(employee.id, 0)
            if difference > 0:
                leave = self.env['hr.holidays'].create({
                    'name': _('Allocation for %s') % employee.name,
                    'employee_id': employee.id,
                    'holiday_status_id': status.id,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'number_of_days_temp': difference
                })
                leave.action_approve()
                if leave.double_validation:
                    leave.action_validate()
            elif difference < 0:
                raise UserError(_('You cannot reduce validated allocation requests'))

    remaining_leaves = fields.Float(compute='_compute_remaining_leaves', string='Remaining Legal Leaves',
                                    inverse='_inverse_remaining_leaves',
                                    help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request. '
                                         'Total based on all the leave types without overriding limit.')
    date_next_attribution = fields.Date('Date prochaine attribution')
    # max_leaves = fields.Float(compute='_get_max_leave', method=True,type="integer",string="Total jours congés")
    # taken_leaves = fields.Float(compute='_get_taken_leave',string="Total jours congés pris")
    montant_moyen_mensuel = fields.Float(compute='_get_montant_by_periode_reference', digits_compute=dp.get_precision('Account'), string="Montant mensuel moyen")
    montant_moyen_journalier = fields.Float(compute='_get_montant_moyen_journalier', digits_compute=dp.get_precision('Account'), string="Montant journalier")







