# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
import odoo.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging


_logger = logging.getLogger(__name__)


class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    conge_non_exceptionne = fields.Boolean('Congé non exceptionnel')
    montant_conge = fields.Float('Montant')
    motif_conge = fields.Text('Motif de la demande')


# class hr_employee(models.Model):
#     _inherit = 'hr.employee'


class Hrholidays(models.Model):
    
    _inherit = "hr.holidays"
    
    state_payroll = fields.Selection([('payed','Payé'),('not_payed','Pas payé')],string="Etat de paie",default='not_payed')
    # prime_trsp = fields.Integer(compute='_get_prime_trsp', digits_compute=dp.get_precision('Account'),
    #                             string='Prime de transport')

    # @api.multi
    # def _get_prime_trsp(self):
    #     for rec in self:
    #         contract = rec.env['hr.contract'].search([('employee_id', '=', rec.id)])
    #         for c in contract:
    #             primes = c.hr_payroll_prime_ids
    #             if primes:
    #                 for p in primes:
    #                     if p.prime_id.code == 'TRSP':
    #                         print(p.montant_prime)


class HrContractType(models.Model):
    _inherit = "hr.contract.type"

    line_ids = fields.One2many('notify.model.line', 'hr_contract_type_id', 'Lignes', required=True)


class NotifModelLine(models.Model):
    _name= 'notify.model.line'
    _description= "Notify line model managment"

    type= fields.Selection([('mois', 'Mois'),('day', 'Jours'), ('hours', 'Heures')],
           'Type', required=True)
    number= fields.Integer('Date', required=True, default=1)
    hr_contract_type_id= fields.Many2one('hr.contract.type', 'Notif')

class HhContract(models.Model):
    _inherit = 'hr.contract'

    mail_server_id = fields.Many2one('ir.mail_server', 'Outgoing MailServer')
    contract_mail = fields.Char()
    manger_mail = fields.Char()
    mail_destination = fields.Char('Adresses mails')

    @api.cr_uid_ids_context
    def mail_reminder_sender(self, cr, uid, context=None):
        today = datetime.now()
        d = datetime.strftime(today, '%Y-%m-%d')
        d1 = datetime.strptime(d, '%Y-%m-%d')
        mail_server = self.pool.get('ir.mail_server')
        mail_server_id = self.pool.get('ir.mail_server').search(cr, uid, [])
        smtp_user = mail_server.browse(cr, uid, mail_server_id).smtp_user
        contract_obj = self.pool.get('hr.contract')
        hr_mail_config_obj = self.pool.get('hr.mail.config')
        hr_mail_config = self.pool.get('hr.mail.config').search(cr, uid, [])
        hr_mail = hr_mail_config_obj.browse(cr, uid, hr_mail_config).mail
        hr_jour_number = hr_mail_config_obj.browse(cr, uid, hr_mail_config).notif_number
        contracts = self.pool.get('hr.contract').search(cr, uid, [('type_id.code', '=', 'CDD')],context=context)
        for c in contracts:
            contract_obj.write(cr, uid, c, {'contract_mail': smtp_user}, context=context)
            date_end = contract_obj.browse(cr, uid, c).date_end
            manger_mail = contract_obj.browse(cr, uid, c).manger_mail
            manger_hr_mail = contract_obj.browse(cr, uid, c).employee_id.department_id.manager_id.work_email if contract_obj.browse(cr, uid, c).employee_id.department_id.manager_id.work_email is not False\
                else contract_obj.browse(cr, uid, c).employee_id.department_id.manager_id.user_id.login is not False
            date = datetime.strptime(date_end, '%Y-%m-%d')
            daysDiff = int(str((date - d1).days))
            followers = '%s;%s' % (hr_mail, manger_hr_mail)
            contract_obj.write(cr, uid, c, {'mail_destination': followers}, context=context)
            if daysDiff <= hr_jour_number and daysDiff > 0:
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hr_holidays_extensions', 'contract_notification')
                mail_templ = self.pool.get('email.template').browse(cr, uid, template_id[1])
                result = mail_templ.send_mail(res_id=c, force_send=True)


# class HrMailConfig(models.Model):
#     _name = 'hr.mail.config'
#
#     mail = fields.Char()
#     notif_number = fields.Integer('Nombre jour Notif')


# class TakenDays(models.Model):
#     _name = 'taken.days'
#
#     taken_day = fields.Char('Taken day')
#     employee_id = fields.Many2one('hr.employee')


# class hr_days(models.Model):
#     _name="hr.days"
#     _description = 'Les jours'
#
#     name = fields.Char('Libéllé',size=128,required=True)
#     sequence = fields.Integer('Sequence',required=True)


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

#
# class hr_type_attribution_holidays(models.Model):
#     _name="hr.type.attribution.holidays"
#     _description = "Type d'attribution de conges"
#
#     name = fields.Char("Libellé",size=128,required=True)
#     code = fields.Char('Code', size=3, required=True)
#     taux = fields.Float("Taux de calcul",required=True)

