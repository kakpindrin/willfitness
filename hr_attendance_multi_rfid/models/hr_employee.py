from odoo import models, exceptions, _, api, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def attendance_action_change_with_date(self, action_date):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': action_date,
            }
            return self.env['hr.attendance'].create(vals)

        attendance = self.env['hr.attendance'].search([ ('employee_id', '=', self.id),
                                                        ('check_out', '=', False) ], limit=1)
        if attendance:
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_("Impossible d'effectuer l'extraction sur %(empl_name)s, "
                                          "Impossible de trouver l'enregistrement correspondant. Votre "
                                          "les présences ont probablement été modifiées manuellement"
                                          " par les ressources humaines.") % {"empl_name": self.name, })
        return attendance