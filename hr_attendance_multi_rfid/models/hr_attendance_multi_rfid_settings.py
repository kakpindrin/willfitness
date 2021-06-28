from odoo import fields, models

class HrAttendanceRfidSetings(models.TransientModel):
    _inherit = 'res.config.settings'

    max_attendance = fields.Integer(string='Participation maximale', default='480',
                                    config_parameter='hr_attendance_multi_rfid.max_attendance',
                                    help='Combien de minutes pour faire sortir les gens automatiquement. (Contrôle toutes les 30 minutes)')