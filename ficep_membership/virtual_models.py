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
from openerp.osv import orm, fields
from openerp import tools


class virtual_master_partner(orm.Model):
    """
    All partners with their postal/email coordinates
    """

    _name = "virtual.master.partner"
    _description = "Virtual Master Partner"
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'membership_state_id':  fields.many2one('membership.state', 'State'),
        'display_name': fields.char('Display Name'),
        'identifier': fields.integer('Identifier'),

        'lastname': fields.char('Lastname'),
        'firstname': fields.char('Firstname'),
        'birth_date': fields.date('Birth Date'),
        'is_company': fields.boolean('Is Company'),

        'postal_coordinate_id': fields.integer('Postal Coordinate ID'),
        'email_coordinate_id': fields.integer('Email Coordinate ID'),

        'email': fields.char('Email Coordinate'),
        'postal': fields.char('Postal Coordinate'),

        'email_is_main': fields.boolean('Email is Main'),
        'postal_is_main': fields.boolean('Postal is Main'),

        'email_unauthorized': fields.boolean('Email Unauthorized'),
        'postal_unauthorized': fields.boolean('Postal Unauthorized'),

        'email_bounce_counter': fields.integer('Email Bounce Counter'),
        'postal_bounce_counter': fields.integer('Postal Bounce Counter'),

        'zip': fields.char("Zip Code"),
        'country_id': fields.many2one('res.country', string='Country'),

        'int_instance_id': fields.many2one('int.instance',
                                           string='Internal Instance'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_master_partner')
        cr.execute("""
        create or replace view virtual_master_partner as (
        SELECT
            p.id as partner_id,
            p.membership_state_id as membership_state_id,
            p.display_name as display_name,
            p.identifier as identifier,
            p.lastname as lastname,
            p.firstname as firstname,
            p.birth_date as birth_date,
            p.is_company as is_company,

            e.bounce_counter as email_bounce_counter,
            pc.bounce_counter as postal_bounce_coutner,

            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,

            e.is_main as email_is_main,
            pc.is_main as postal_is_main,

            adr.zip as zip,
            adr.country_id as country_id,

            e.unauthorized as email_unauthorized,
            pc.unauthorized as postal_unauthorized,

            p.int_instance_id as int_instance_id,

            CASE
                WHEN pc.vip is TRUE
                THEN 'VIP'
                ELSE adr.name
            END as postal,
            CASE
                WHEN e.vip is TRUE
                THEN 'VIP'
                ELSE e.email
            END as email
        FROM
            res_partner p

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active IS TRUE)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active IS TRUE)

        LEFT OUTER JOIN
            address_address adr
        ON (adr.id = pc.address_id)

        WHERE p.active IS TRUE
            )""")


class virtual_custom_partner(orm.Model):
    _name = "virtual.custom.partner"
    _inherit = ['virtual.master.partner']
    _description = "Virtual Custom Partner"
    _auto = False

# orm methods

    def init(self, cr):
        """
        ====
        init
        ====
        Select all row of virtual.master.partner but take only main coordinate
        if there are
        """
        super(virtual_custom_partner, self).init(cr)
        cr.execute("""
        create or replace view virtual_custom_partner as (
        SELECT
            partner_id as id,
            *
        FROM
            virtual_master_partner

        WHERE (email_is_main IS TRUE or email_is_main IS NULL)
        AND (postal_is_main IS TRUE or postal_is_main IS NULL)
            )""")
