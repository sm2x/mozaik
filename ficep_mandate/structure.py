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


class int_power_level(orm.Model):

    _name = 'int.power.level'
    _inherit = ['int.power.level']

    _columns = {
        'mandate_category_ids': fields.one2many('mandate.category', 'int_power_level_id', 'Mandate Categories'),
    }


class electoral_district(orm.Model):

    _name = 'electoral.district'
    _inherit = ['electoral.district']

    _columns = {
        'selection_committee_ids': fields.one2many('sta.selection.committee', 'electoral_district_id', 'Selection committees'),
    }


class sta_assembly_category(orm.Model):

    _name = 'sta.assembly.category'
    _inherit = ['sta.assembly.category']

    _columns = {
        'mandate_category_ids': fields.one2many('mandate.category', 'sta_assembly_category_id', 'Mandate categories', domain=[('active', '=', True)]),
        'mandate_category_inactive_ids': fields.one2many('mandate.category', 'sta_assembly_category_id', 'Mandate categories', domain=[('active', '=', False)]),
    }


class sta_assembly(orm.Model):

    _name = 'sta.assembly'
    _inherit = ['sta.assembly']

    _columns = {
         'selection_committee_ids': fields.one2many('sta.selection.committee', 'assembly_id', 'Selection committees', domain=[('active', '=', True)]),
         'selection_committee_inactive_ids': fields.one2many('sta.selection.committee', 'assembly_id', 'Selection committees', domain=[('active', '=', False)]),
    }
