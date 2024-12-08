# models/res_config_settings.py

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tiktok_app_id = fields.Char(
        string='TikTok App ID', config_parameter='tiktok.app_id')
    tiktok_secret = fields.Char(
        string='TikTok Secret', config_parameter='tiktok.secret')
    tiktok_auth_code = fields.Char(
        string='TikTok Auth Code', config_parameter='tiktok.auth_code')
    tiktok_advertiser_id = fields.Char(
        string='TikTok Advertiser ID', config_parameter='tiktok.advertiser_id')
    tiktok_page_id = fields.Char(
        string='TikTok Page ID', config_parameter='tiktok.page_id')

    tiktok_sales_team_id = fields.Many2one(
        'crm.team', string="Default Sales Team",
        config_parameter='tiktok.sales_team_id'
    )
    tiktok_salesperson_id = fields.Many2one(
        'res.users', string="Default Salesperson",
        config_parameter='tiktok.salesperson_id',
        domain=[('share', '=', False)]
    )
