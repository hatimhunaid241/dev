# -*- coding: utf-8 -*-
#######################################################################################
#
#    Recreate System Limited
#
#    Copyright (C) Recreate System Limited(<https://www.recreatesys.com>).
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#    or modified copies of the Software.
#
########################################################################################
{
    'name': "Backup",

    'summary': """
        Backup Odoo Instance""",

    'description': """
        
    """,

    'author': 'Recreate System Limited',
    'website': "https://www.recreatesys.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/email_template.xml',
        'views/views.xml',
        'views/setting_view.xml',
        'data/daily_backup_cron.xml'
    ],
    'installable': True,
    'application': True,
}
