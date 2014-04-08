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
from .abstract_mandate import abstract_candidature
from .structure import legislature


class sta_candidature(orm.Model):

    _name = 'sta.candidature'
    _description = "State Candidature"
    _inherit = ['abstract.candidature']

    _init_mandate_columns = abstract_candidature._init_mandate_columns
    _init_mandate_columns.extend(['legislature_id', 'sta_assembly_id'])

    _columns = {
        'electoral_district_id': fields.related('selection_committee_id', 'electoral_district_id', string='Electoral District',
                                          type='many2one', relation="electoral.district",
                                          store=True),
        'legislature_id': fields.related('selection_committee_id', 'legislature_id', string='Legislature',
                                          type='many2one', relation="legislature",
                                          store=True),
        'sta_assembly_id': fields.related('selection_committee_id', 'sta_assembly_id', string='State Assembly',
                                          type='many2one', relation="sta.assembly",
                                          store=True),
        }

    # view methods: onchange, button
    def onchange_selection_committee(self, cr, uid, ids, selection_committee_id, context=None):
        res = {}
        selection_committee = self.pool.get('selection.committee').browse(cr, uid, selection_committee_id, context)

        res['value'] = dict(legislarure_id=selection_committee.legislature_id.id or False,
                            electoral_distric_id=selection_committee.electoral_district_id.id or False,
                            sta_assembly_id=selection_committee.sta_assembly_id.id or False)
        return res

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        res = {}
        sta_category_id = False
        if mandate_category_id:
            sta_category_id_val = self.pool.get('mandate.category').read(cr, uid, mandate_category_id, ['sta_assembly_category_id'])['sta_assembly_category_id']
            if sta_category_id_val:
                sta_category_id = sta_category_id_val[0]

        res['value'] = dict(electoral_distric_id=False,
                            sta_assembly_category_id=sta_category_id)
        return res

    def button_create_mandate(self, cr, uid, ids, context=None):
        for candidature_id in ids:
            self.pool.get('sta.mandate').create_from_candidature(cr, uid, [candidature_id], context=context)


class sta_mandate(orm.Model):
    _name = 'sta.mandate'
    _description = "State Mandate"
    _inherit = ['abstract.mandate']

    _columns = {
        'legislature_id': fields.many2one('legislature', string='Legislature',
                                                 required=True, track_visibility='onchange'),
        'sta_assembly_id': fields.related('electoral_district_id', 'assembly_id', string='State Assembly',
                                          type='many2one', relation="sta.assembly",
                                          store=False),
        'sta_assembly_category_id': fields.related('mandate_category_id', 'sta_assembly_category_id', string='State Assembly Category',
                                          type='many2one', relation="sta.assembly.category",
                                          store=False),
        'deadline_date': fields.related('legislature_id', 'deadline_date', string='Deadline Date',
                                          type='date', relation="legislature",
                                          store={'legislature': (legislature.get_linked_sta_mandate_ids, ['deadline_date'], 20)}),
        }

    def create_from_candidature(self, cr, uid, ids, context=None):
        candidature_pool = self.pool.get('sta.candidature')
        candidature_data_list = candidature_pool.read(cr, uid, ids, [], context)
        res = False
        for candidature_data in candidature_data_list:
            mandate_values = {}
            for column in candidature_pool._init_mandate_columns:
                if column in self._columns:
                    if candidature_pool._columns[column]._type == 'many2one':
                        mandate_values[column] = candidature_data[column][0]
                    else:
                        mandate_values[column] = candidature_data[column]

            if mandate_values:
                res = self.create(cr, uid, mandate_values, context)
        return res
