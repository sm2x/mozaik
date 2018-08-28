# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Involvement',
    'summary': """
        Manage involvements (and all kind of segmentation) on partners""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'depends': [
        'base',
        'base_suspend_security',
        'contacts',
        'mozaik_abstract_model',
        'mozaik_partner_assembly',
    ],
    'data': [
        'security/res_groups.xml',
        'security/partner_involvement_category.xml',
        'security/partner_involvement.xml',
        'views/partner_involvement.xml',
        'views/partner_involvement_category.xml',
        'views/involvement_menu.xml',
        'views/res_partner.xml',
    ],
    'demo': [
        'demo/partner_involvement_category.xml',
    ],
    'installable': True,
}