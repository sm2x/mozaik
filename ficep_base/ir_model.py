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

from openerp.osv import orm
from openerp.tools import SUPERUSER_ID


class ir_model(orm.Model):

    _inherit = 'ir.model'

    def _get_active_relations(self, cr, uid, ids, model_name, context=None, with_ids=False):
        uid = SUPERUSER_ID
        relation_ids = self.pool.get('ir.model.fields').search(cr, uid, [('relation', '=', model_name),
                                                                         ('ttype', '=', 'many2one')],
                                                               context=context)
        relations = self.pool.get('ir.model.fields').browse(cr, uid, relation_ids, context=context)

        results = {}
        for record_id in ids:
            relation_models = {}
            for relation in relations:
                model = self.pool.get(relation.model, False)
                if not model:
                    continue
                if not model._auto or model._transient or not model._columns.get(relation.name):
                    continue
                col = model._columns[relation.name]
                if hasattr(col, 'store') and not col.store:
                    continue
                if hasattr(model, '_allowed_inactive_link_models'):
                    if model_name in model._allowed_inactive_link_models:
                        continue

                active_dep_ids = model.search(cr, uid, [(relation.name, '=', record_id)], context=context)

                if len(active_dep_ids) > 0:
                    if with_ids:
                        relation_models.update({relation.model: active_dep_ids})
                        results.update({record_id: relation_models})
                    else:
                        results.update({record_id: relation.model})

        return results

    def _get_relation_column_name(self, cr, uid, model_name, relation_model_name, context=None):
        relation_ids = self.pool.get('ir.model.fields').search_read(cr, uid, [('model', '=', model_name),
                                                                              ('relation', '=', relation_model_name),
                                                                              ('ttype', '=', 'many2one')],
                                                                              fields=['name'], context=context)
        if relation_ids:
            return relation_ids[0]['name']

        return False


class ir_model_data(orm.Model):

    _inherit = 'ir.model.data'

# private methods

    def _updatexx(self, cr, uid, model, module, values, xml_id=False, store=True, noupdate=False, mode='init', res_id=False, context=None):
        '''
        Let's the developper to decide if a record is updatable or not
        I.e force the init mode if the data tag is marked noupdate="0"
        '''
        if not noupdate and mode == 'update':
            mode = 'init'
        res = super(ir_model_data, self)._update(cr, uid, model, module, values, xml_id=xml_id, store=store, noupdate=noupdate, mode=mode, res_id=res_id, context=context)
        return res

# public methods

    def get_object_alternative(self, cr, uid, alts):
        """
        Returns (model, res_id) corresponding to the given (module, xml_id) couple or, if not found,
        to the alternative given couple
        """
        alts = alts or ()

        for alt in alts:
            try:
                return self.get_object_reference(cr, SUPERUSER_ID, alt[0], alt[1])
            except ValueError:
                pass
            except:
                raise

        return False, False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
