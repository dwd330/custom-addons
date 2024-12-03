from odoo import models, fields

class FcmToken(models.Model):
    _name = 'fcm.token'
    _description = 'FCM Token'


    token = fields.Char(string='token', required=True)
    user = fields.Char(string='user')
    created_at = fields.Datetime(string='Created At', default=fields.Datetime.now)
