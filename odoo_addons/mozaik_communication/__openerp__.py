# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_communication, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_communication is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_communication is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_communication.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'MOZAIK: Communication',
    'version': '8.0.1.0.1',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mass_mailing_distribution_list',
        'mozaik_person',
        'mozaik_structure',
        'mozaik_membership',
        'mozaik_retrocession',
        # from https://github.com/OCA/social
        'email_template_configurator',
    ],
    'description': """
MOZAIK Communication
====================
* New Menus:
** Communication/Persons
** Communication/Mailing
** Communication/Postal Mailing
** Communication/Configuration
* Customization of the Distribution List Module
""",
    'images': [
        'static/src/img/icon-mass.png',
    ],
    'data': [
        'security/mail_mass_mailing_group.xml',
        'security/ir.model.access.csv',
        'security/communication_security.xml',
        'wizard/distribution_list_mass_function_view.xml',
        'wizard/add_registrations_view.xml',
        'wizard/distribution_list_add_filter_view.xml',
        'wizard/export_csv_view.xml',
        'distribution_list_view.xml',
        'postal_mail_view.xml',
        'res_partner_view.xml',
        'communication_view.xml',
        'mass_mailing_view.xml',
        'email_template_view.xml',
        'event_view.xml',
        'membership_request_view.xml',
        'views/mail_mail_statistics_view.xml',
        'views/virtual_models_view.xml',
        'views/email_template_view.xml',
        'views/mass_mailing_report.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'sequence': 150,
    'installable': True,
    'auto_install': False,
}
