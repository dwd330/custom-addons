{
    'name': 'Custom IT management',
    'summary': " IT app for help desk tickets and to manage assests effectively",
    'author': "Dawoud",
    'website': "https://www.nooralmamzar.com",
    'license': 'LGPL-3',
    'depends': ['base', 'helpdesk', 'maintenance','dev_equipment_allocation'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/it_menu.xml',
        'data/cron.xml',
    ],
    'installable': True,
    'application': True,
}
