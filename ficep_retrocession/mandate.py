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
from openerp.tools.translate import _
from openerp.osv import orm, fields
from structure import sta_assembly, ext_assembly
from openerp.addons.ficep_retrocession.common import INVOICE_AVAILABLE_TYPES, CALCULATION_METHOD_AVAILABLE_TYPES


class mandate_category(orm.Model):

    _name = 'mandate.category'
    _description = 'Mandate Category'
    _inherit = ['mandate.category']

    def get_linked_sta_mandate_ids(self, cr, uid, ids, context=None):
        return super(mandate_category, self).get_linked_sta_mandate_ids(cr, uid, ids, context=context)

    def get_linked_ext_mandate_ids(self, cr, uid, ids, context=None):
        return super(mandate_category, self).get_linked_ext_mandate_ids(cr, uid, ids, context=context)

    def _check_retro_instance_on_assemblies(self, cr, uid, ids, for_unlink=False, context=None):
        """
        ==============
        _check_retro_instance_on_assemblies
        ==============
        Check if a retrocession management instance is set on all impacted assemblie
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        for category in self.browse(cr, uid, ids, context=context):
            if category.invoice_type != 'none':
                if category.type == 'sta':
                    assembly_cat_id = category['sta_assembly_category_id'].id
                    assembly_model = 'sta.assembly'
                elif category.type == 'ext':
                    assembly_cat_id = category['ext_assembly_category_id'].id
                    assembly_model = 'ext.assembly'
                else:
                    continue

                assembly_ids = self.pool.get(assembly_model).search(cr, uid, [('assembly_category_id', '=', assembly_cat_id),
                                                                              ('retro_instance_id', '=', False)], context=context)
                if len(assembly_ids) > 0:
                    return False

        return True

    _columns = {
        'fractionation_id': fields.many2one('fractionation', string='Fractionation',
                                            select=True, track_visibility='onchange'),
        'calculation_method_id': fields.many2one('calculation.method', string='Calculation Method',
                                            select=True, track_visibility='onchange'),
        'invoice_type': fields.selection(INVOICE_AVAILABLE_TYPES, 'Invoicing', required=True, track_visibility='onchange'),
        'property_retrocession_account': fields.property(type='many2one',
                                                              relation='account.account',
                                                              string='Retrocession Account',),
        'property_retrocession_cost_account': fields.property(type='many2one',
                                                 relation='account.account',
                                                 string='Cost Account',),
    }

    _defaults = {
        'invoice_type': INVOICE_AVAILABLE_TYPES[2][0],
    }

    _constraints = [
        (_check_retro_instance_on_assemblies, _("Some impacted assemblies has no retrocession management instance set!"), ['invoice_type'])
    ]


class abstract_mandate_retrocession(orm.AbstractModel):
    _name = 'abstract.mandate.retrocession'
    _description = 'Abstract Mandate for retrocession'
    _inherit = ['abstract.mandate']

    _inactive_cascade = True
    _retrocession_foreign_key = False
    _assembly_foreign_key = False
    _assembly_model = False

    _method_id_store_trigger = {}
    _invoice_type_store_trigger = {}

    def _get_method_id(self, cr, uid, ids, fname, arg, context=None):
        """
        =================
        _get_method_id
        =================
        Get id of calculation method
        :rparam: id of calculation method
        :rtype: integer
        """
        res = {}
        for mandate in self.browse(cr, uid, ids, context=context):
            cat_method = mandate.mandate_category_id.calculation_method_id
            ass_method = mandate[self._assembly_foreign_key].calculation_method_id

            if ass_method:
                method_id = ass_method.id
            elif cat_method:
                method_id = cat_method.id
            else:
                method_id = False
            res[mandate.id] = method_id
        return res

    def _has_retrocessions_linked(self, cr, uid, ids, fname, arg, context=None):
        """
        =========================
        has_retrocessions_linked
        =========================
        Return whether retrocessions are linked to mandate or not
        :rparam: True if this is the case else False
        :rtype: Boolean
        """
        res = {}
        for mandate_id in ids:
            nb_retro = len(self.pool.get('retrocession').search(cr, uid, [(self._retrocession_foreign_key, '=', mandate_id)], context=context))
            res[mandate_id] = True if nb_retro > 0 else False
        return res

    _columns = {
        'invoice_type': fields.related('mandate_category_id', 'invoice_type', string='Invoicing', type='selection',
                               selection=INVOICE_AVAILABLE_TYPES, store=_invoice_type_store_trigger),
        'calculation_method_id': fields.function(_get_method_id, string='Calculation Method',
                                 type='many2one', relation="calculation.method", select=True, store=_method_id_store_trigger),
        'method_type': fields.related('calculation_method_id', 'type', string='Calculation Method Type', type='selection',
                                       selection=CALCULATION_METHOD_AVAILABLE_TYPES, store=_method_id_store_trigger),
        'has_retrocessions_linked': fields.function(_has_retrocessions_linked, string='Has Retrocessions',
                                 type='boolean', store=False),
        'retro_instance_id': fields.many2one('int.instance', 'Retrocession Management Instance',
                                       select=True, track_visibility='onchange'),
        'reference': fields.char('Communication', size=64, help="The mandate reference for payments."),
    }

    #orm methods
    def create(self, cr, uid, vals, context=None):
        if 'invoice_type' not in vals:
            mandate_category_id = vals['mandate_category_id']
            category = self.pool.get('mandate.category').browse(cr, uid, mandate_category_id)
            vals['invoice_type'] = category.invoice_type

        if ('retro_instance_id' not in vals or vals['retro_instance_id'] == False):
            assembly_id = vals[self._assembly_foreign_key]
            assembly = self.pool.get(self._assembly_model).browse(cr, uid, assembly_id)
            vals['retro_instance_id'] = assembly.retro_instance_id.id

        res = super(abstract_mandate_retrocession, self).create(cr, uid, vals, context=context)

        self.generate_mandate_reference(cr, uid, res)
        if res:
            mandate = self.browse(cr, uid, res, context=context)
            if mandate.calculation_method_id:
                self.pool.get('calculation.method').copy_fixed_rules_on_mandate(cr, uid, mandate.calculation_method_id.id, mandate.id, self._retrocession_foreign_key, context=context)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        if self._assembly_foreign_key in vals or 'mandate_category_id' in vals:
            dataset = self.read(cr, uid, ids, ['calculation_method_id'], context=context)
            method_dict = {}
            for value in dataset:
                method_dict[value['id']] = value['calculation_method_id'][0] if type(value['calculation_method_id']) == tuple else False

        res = super(abstract_mandate_retrocession, self).write(cr, uid, ids, vals, context=context)
        if self._assembly_foreign_key in vals or 'mandate_category_id' in vals:
            for mandate in self.browse(cr, uid, ids, context=context):
                mandate_method_id = mandate.calculation_method_id.id if mandate.calculation_method_id else False
                if mandate.id in method_dict and method_dict[mandate.id] != mandate_method_id:
                    self.pool.get('calculation.method').copy_fixed_rules_on_mandate(cr, uid, mandate.calculation_method_id.id, mandate.id, self._retrocession_foreign_key, context=context)
        return res

    def generate_mandate_reference(self, cr, uid, mandate_id, context=None):
        """
        ==========================
        generate_mandate_reference
        ==========================
        Generate and store structured reference for mandate
        :rparam: True
        :rtype: Bolean
        """
        unique_id = self.read(cr, uid, mandate_id, ['unique_id'], context=context)['unique_id']
        base = 8000000000 + unique_id
        mod = base % 97 or 97
        mod = str(mod).rjust(2, '0')
        base_str = str(base)
        reference = '+++%s/%s/%s%s+++' % (base_str[:3], base_str[3:7], base_str[7:], mod)
        return self.write(cr, uid, mandate_id, {'reference': reference}, context=context)

    def get_retro_instance_id(self, cr, uid, assembly_id, context=None):
        if assembly_id:
            assembly = self.pool.get(self._assembly_model).browse(cr, uid, assembly_id)
            return assembly.retro_instance_id.id

        return False


class sta_mandate(orm.Model):
    _name = 'sta.mandate'
    _description = 'State Mandate'
    _inherit = ['sta.mandate', 'abstract.mandate.retrocession']

    _retrocession_foreign_key = 'sta_mandate_id'
    _assembly_foreign_key = 'sta_assembly_id'
    _assembly_model = 'sta.assembly'

    def _get_method_id(self, cr, uid, ids, fname, arg, context=None):
        return super(sta_mandate, self)._get_method_id(cr, uid, ids, fname, arg, context=context)

    def _has_retrocessions_linked(self, cr, uid, ids, fname, arg, context=None):
        return super(sta_mandate, self)._has_retrocessions_linked(cr, uid, ids, fname, arg, context=context)

    _method_id_store_trigger = {
        'sta.mandate': (lambda self, cr, uid, ids, context=None: ids,
            ['sta_assembly_id', 'mandate_category_id'], 20),
        'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['calculation_method_id'], 20),
        'sta.assembly': (sta_assembly.get_linked_sta_mandate_ids, ['calculation_method_id'], 20),
    }

    _invoice_type_store_trigger = {
       'sta.mandate': (lambda self, cr, uid, ids, context=None: ids,
            ['mandate_category_id'], 20),
       'mandate.category': (mandate_category.get_linked_sta_mandate_ids, ['invoice_type'], 20),
    }

    _columns = {
        'invoice_type': fields.related('mandate_category_id', 'invoice_type', string='Invoicing', type='selection',
                               selection=INVOICE_AVAILABLE_TYPES, store=_invoice_type_store_trigger),
        'calculation_method_id': fields.function(_get_method_id, string='Calculation Method',
                                 type='many2one', relation="calculation.method", select=True, store=_method_id_store_trigger),
        'method_type': fields.related('calculation_method_id', 'type', string='Calculation Method Type', type='selection',
                                       selection=CALCULATION_METHOD_AVAILABLE_TYPES, store=_method_id_store_trigger),
        'calculation_rule_ids': fields.one2many('calculation.rule', 'sta_mandate_id', 'Calculation Rules', domain=[('active', '=', True)]),
        'calculation_rule_inactive_ids': fields.one2many('calculation.rule', 'sta_mandate_id', 'Calculation Rules', domain=[('active', '=', False)]),
    }

    def onchange_sta_assembly_id(self, cr, uid, ids, sta_assembly_id, context=None):
        res = super(sta_mandate, self).onchange_sta_assembly_id(cr, uid, ids, sta_assembly_id, context=context)
        res['value']['retro_instance_id'] = self.get_retro_instance_id(cr, uid, sta_assembly_id, context=context)

        return res

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        res = super(sta_mandate, self).onchange_mandate_category_id(cr, uid, ids, mandate_category_id, context=context)

        if mandate_category_id:
            category_data = self.pool.get('mandate.category').read(cr, uid, mandate_category_id, ['invoice_type'], context)
            invoice_type = category_data['invoice_type'] or False

            res['value']['invoice_type'] = invoice_type
        return res


class ext_mandate(orm.Model):
    _name = 'ext.mandate'
    _description = 'External Mandate'
    _inherit = ['ext.mandate', 'abstract.mandate.retrocession']

    _inactive_cascade = True
    _retrocession_foreign_key = 'ext_mandate_id'
    _assembly_foreign_key = 'ext_assembly_id'
    _assembly_model = 'ext.assembly'

    def _get_method_id(self, cr, uid, ids, fname, arg, context=None):
        return super(ext_mandate, self)._get_method_id(cr, uid, ids, fname, arg, context=context)

    def _has_retrocessions_linked(self, cr, uid, ids, fname, arg, context=None):
        return super(ext_mandate, self)._has_retrocessions_linked(cr, uid, ids, fname, arg, context=context)

    _method_id_store_trigger = {
        'ext.mandate': (lambda self, cr, uid, ids, context=None: ids,
            ['ext_assembly_id', 'mandate_category_id'], 20),
        'mandate.category': (mandate_category.get_linked_ext_mandate_ids, ['calculation_method_id'], 20),
        'ext.assembly': (ext_assembly.get_linked_ext_mandate_ids, ['calculation_method_id'], 20),
    }

    _invoice_type_store_trigger = {
       'ext.mandate': (lambda self, cr, uid, ids, context=None: ids,
            ['mandate_category_id'], 20),
       'mandate.category': (mandate_category.get_linked_ext_mandate_ids, ['invoice_type'], 20),
    }

    _columns = {
        'invoice_type': fields.related('mandate_category_id', 'invoice_type', string='Invoicing', type='selection',
                                       selection=INVOICE_AVAILABLE_TYPES, store=_invoice_type_store_trigger),
        'calculation_method_id': fields.function(_get_method_id, string='Calculation Method',
                                 type='many2one', relation="calculation.method", select=True, store=_method_id_store_trigger),
        'method_type': fields.related('calculation_method_id', 'type', string='Calculation Method Type', type='selection',
                                       selection=CALCULATION_METHOD_AVAILABLE_TYPES, store=_method_id_store_trigger),
        'calculation_rule_ids': fields.one2many('calculation.rule', 'ext_mandate_id', 'Calculation Rules', domain=[('active', '=', True)]),
        'calculation_rule_inactive_ids': fields.one2many('calculation.rule', 'ext_mandate_id', 'Calculation Rules', domain=[('active', '=', False)]),
    }

    def onchange_ext_assembly_id(self, cr, uid, ids, ext_assembly_id, context=None):
        res = super(ext_mandate, self).onchange_ext_assembly_id(cr, uid, ids, ext_assembly_id, context=context)
        res['value']['retro_instance_id'] = self.get_retro_instance_id(cr, uid, ext_assembly_id, context=context)

        return res

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        res = super(ext_mandate, self).onchange_mandate_category_id(cr, uid, ids, mandate_category_id, context=context)

        if mandate_category_id:
            category_data = self.pool.get('mandate.category').read(cr, uid, mandate_category_id, ['invoice_type'], context)
            invoice_type = category_data['invoice_type'] or False

            res['value']['invoice_type'] = invoice_type
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
