# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'MOZAIK: Phone',
    'version': '11.0.1.0.0',
    "author": "ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    'category': 'Political Association',
    'depends': [
        'mozaik_coordinate',
    ],
    'description': """
MOZAIK Phone
============
This module manages phone numbers and phone coordinates.
It covers three types of phone: fix, mobile and fax.
Numbers are normalized regarding the external python library: phonenumbers
""",
    'external_dependencies': {
        'python': [
            'phonenumbers',
        ],
    },
    'images': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/phone_security.xml',
        'data/ir_config_parameter_data.xml',
        'data/phone_phone_data.xml',
        'phone_phone_view.xml',
        'coordinate_category_view.xml',
        'res_partner_view.xml',
        'wizard/change_main_phone.xml',
        'wizard/allow_duplicate_view.xml',
        'wizard/bounce_editor_view.xml',
        'wizard/change_phone_type.xml',
    ],
    'qweb': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'license': 'AGPL-3',
    'installable': False,
}