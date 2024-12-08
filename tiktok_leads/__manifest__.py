# __manifest__.py

{
    'name': 'TikTok Lead Integration',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['base','crm'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/tiktok_lead_views.xml',
        'views/menu.xml',
        'views/res_config_settings_views.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
}