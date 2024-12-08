from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mobile_app_ID = fields.Char(string="mobile app ID")

