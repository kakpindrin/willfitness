#-*- coding:utf-8 -*-

from odoo import fields, models, api
from collections import namedtuple
from datetime import datetime


class hr_holidays(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def computeHoldaysByType(self,date_from, date_to, contract):
        res = []
        Range = namedtuple('Range', ['start', 'end'])
        hstatus = self.env['hr.leave.type'].search([])
        r1 = Range(start=date_from, end=date_to)
        self._cr.execute("SELECT id FROM hr_leave WHERE\
         ((date_from between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) \
         OR (date_to between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))) \
         AND state='validate'", (str(date_from), str(date_to), str(date_from), str(date_to)))
        holidays_ids = [x[0] for x in self._cr.fetchall()]
        if holidays_ids:
            holidays = self.browse(holidays_ids)
            for status in hstatus:
                days = 0
                temp = holidays.filtered(lambda r: r.holiday_status_id == status)
                for tp in temp:
                    print(tp.date_from.date())
                    old_date_from = datetime.strptime(str(tp.date_from.date()), '%Y-%m-%d')
                    old_date_to = datetime.strptime(str(tp.date_to.date()), '%Y-%m-%d')
                    r2 = Range(start=old_date_from, end=old_date_to)
                    result = (min(r1.end, r2.end) - max(r1.start, r2.start)).days + 1
                    if result > 0:
                        days += result
                if days != 0:
                    vals = {
                        'name': status.name,
                        'sequence': 5,
                        'code': status.code,
                        'number_of_days': days,
                        'number_of_hours': days * 8,
                        'contract_id': contract.id,

                    }
                    res += [vals]
        return res


__author__ = 'lekaizen'
