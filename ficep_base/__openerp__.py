# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'FICEP: Base',
    'version': '1.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'base',
        'settings_improvement',  # from https://github.com/acsone/acsone-addons
        'website',
        'portal',
        'mass_mailing',
        'mail',
        'report',
        'product',
        'board',
        'edi',
        'partner_firstname',     # from lp:~partner-contact-core-editors/partner-contact-management/7.0
        'mass_editing',          # from lp:~server-env-tools-core-editors/server-env-tools/7.0
        'cron_run_manually',     # from lp:~server-env-tools-core-editors/server-env-tools/7.0
        'auth_admin_passkey',    # from lp:~server-env-tools-core-editors/server-env-tools/7.0
        'document',
        'distribution_list',     # from lp:acsone-addons
        'readonly_bypass',       # from lp:acsone-addons
        'connector',             # from git https://github.com/OCA/connector.git connector-addons master
        #'event',
    ],
    'description': """
FICEP Base
==========
* improve user context adding a flag by ficep group
* provide a work-around to handle correctly the readonly attribute of the widget mail_thread
* define ficep menus skeleton
    """,
    'images': [
    ],
    'data': [
        'data/delete_data.xml',
        'security/ficep_base_security.xml',
        'data/ir_filters_data.xml',
        'data/res_lang_data.xml',
        'data/res_lang_install.xml',
        'data/ir_config_parameter_data.xml',
        'ficep_view.xml',
        'res_partner_view.xml',
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'sequence': 150,
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
