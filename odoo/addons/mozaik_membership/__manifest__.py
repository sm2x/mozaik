# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Mozaik: Membership',
    'summary': """
        Manage memberships""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'website': 'https://acsone.eu/',
    'category': 'Political Association',
    'depends': [
        'base_address_city',
        'product',
        'partner_contact_birthdate',
        'partner_multi_relation',
        'queue_job',
        'mozaik_email',
        'mozaik_address',
        'mozaik_phone',
        'mozaik_partner_assembly',
        'mozaik_structure',
        'mozaik_person',
        'mozaik_involvement',
    ],
    'data': [
        'data/membership_state.xml',
        'data/product_category.xml',
        'data/res_partner.xml',
        'security/res_groups.xml',
        'security/membership_security.xml',
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/membership_state.xml',
        'views/membership_line.xml',
        'views/membership_tarification.xml',
        'views/res_city.xml',
        'views/coordinate.xml',
        'views/partner_involvement.xml',
        'views/int_instance.xml',
        'wizards/add_membership.xml',
        'wizards/update_membership.xml',
        'views/res_partner.xml',
        'views/membership_menu.xml',
        'wizards/change_main_address.xml',
        'wizards/membership_renew.xml',
        'wizards/mass_membership_renew.xml',
    ],
    'demo': [
        "demo/product_product.xml",
        "demo/res_users.xml",
        "demo/res_partner.xml",
        "demo/int_instance.xml",
        "demo/sta_instance.xml",
        "demo/membership_tarification.xml",
        "demo/res_city.xml",
    ],
    'installable': True,
}