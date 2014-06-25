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

import logging
import phonenumbers as pn

from openerp.osv import orm, fields
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


"""
Available Types for 'phone.phone':
Fix - Mobile - Fax
"""
PHONE_AVAILABLE_TYPES = [
    ('fix', 'Fix'),
    ('mobile', 'Mobile'),
    ('fax', 'Fax'),
]

FIXFAX = _('Fix + Fax')

phone_available_types = dict(PHONE_AVAILABLE_TYPES)

PREFIX_CODE = 'BE'


class phone_phone(orm.Model):

    _name = 'phone.phone'
    _inherit = ['abstract.ficep.model']
    _description = 'Phone Number'

    def _get_linked_coordinates(self, cr, uid, ids, context=None):
        return self.pool['phone.coordinate'].search(cr, uid, [('phone_id', 'in', ids)], context=context)

    def _validate_data(self, cr, uid, vals, mode='write', context=None):
        if 'type' in vals and vals['type'] != PHONE_AVAILABLE_TYPES[0][0]:
            vals.update(also_for_fax=False)
        if 'name' in vals:
            vals['name'] = self._check_and_format_number(cr, uid, vals['name'], context=context)

    def _check_and_format_number(self, cr, uid, num, context=None):
        """
        ========================
        _check_and_format_number
        ========================
        :param num: the phone number
        :type num: char
        :returns: Number formated into a International Number
                  If number is not starting by '+' then check if it starts by '00'
                  and replace it with '+'. Otherwise set a code value with a PREFIX
        :rtype: char
        :raise: pn.NumberParseException
                * if number is not parsing due to a bad encoded value
        """
        if context == None:
            context = {}

        if context.get('install_mode', False) and num[:4] == 'tbc ':
            # during data migration suspect number are not checked
            return num
        code = False
        numero = num
        if num[:2] == '00':
            numero = '%s%s' % (num[:2].replace('00', '+'), num[2:])
        elif not num.startswith('+'):
            code = self.get_default_country_code(cr, uid, context=context)
        try:
            normalized_number = pn.parse(numero, code) if code else pn.parse(numero)
        except pn.NumberParseException, e:
            errmsg = _('Invalid phone number: %s') % e
            if context.get('install_mode', False):
                # during data migration exception are not allowed
                _logger.warning(errmsg)
                return num
            raise orm.except_orm(_('Error!'), errmsg)
        return pn.format_number(normalized_number, pn.PhoneNumberFormat.INTERNATIONAL)

    _columns = {
        'name': fields.char('Number', size=50, required=True, select=True, track_visibility='onchange'),
        'type': fields.selection(PHONE_AVAILABLE_TYPES, 'Type', required=True, track_visibility='onchange'),
        'also_for_fax': fields.boolean('Also for Fax', track_visibility='onchange'),

        'phone_coordinate_ids': fields.one2many('phone.coordinate', 'phone_id', 'Phone Coordinates',
                                                domain=[('active', '=', True)]),
        'phone_coordinate_inactive_ids': fields.one2many('phone.coordinate', 'phone_id', 'Phone Coordinates',
                                                domain=[('active', '=', False)]),
    }

    _order = 'name'

    _defaults = {
        'type': PHONE_AVAILABLE_TYPES[0][0],
        'also_for_fax': False,
    }

# constraints

    _unicity_keys = 'name'

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        """
        ========
        name_get
        ========
        :rparam: list of tuple (id, name to display)
                 where id is the id of the object into the relation
                 and display_name, the name of this object.
        :rtype: [(id,name)] list of tuple
        """
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.read(cr, uid, ids, ['name', 'type', 'also_for_fax'], context=context):
            display_name = "%s (%s)" % (record['name'],
                                        record['also_for_fax'] and FIXFAX
                                                               or phone_available_types.get(record['type']))
            res.append((record['id'], display_name))
        return res

    def create(self, cr, uid, vals, context=None):
        """
        ==================
        create phone.phone
        ==================
        This method will create a phone number after checking and format this
        Number, calling the _check_and_format_number method
        :param: vals
        :type: dictionary that contains at least 'name'
        :rparam: id of the new phone
        :rtype: integer
        """
        self._validate_data(cr, uid, vals, mode='create', context=context)
        return super(phone_phone, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """
        =====
        write
        =====
        Validate data and update the record
        :param: vals
        :type: dictionary that possibly contains 'name'
        :rparam: True
        :rtype: boolean
        """
        self._validate_data(cr, uid, vals, context=context)
        return super(phone_phone, self).write(cr, uid, ids, vals, context=context)

    def copy(self, cr, uid, ids, default=None, context=None):
        """
        ================
        copy phone.phone
        ================
        Due to the constraint: to avoid the standard except: better explanation
        for the user
        """
        raise orm.except_orm(_('Error'), _('A phone number cannot be duplicated!'))

# public methods

    def get_default_country_code(self, cr, uid, context=None):
        """
        ========================
        get_default_country_code
        ========================
        This method will return a country code.
        e.g. BE, FR, ...
        The country code firstly will be the value of the parameter key ``default.country.code.phone``
        If no value then take the default country code PREFIX_CODE
        :rparam: Country code found into the config_parameter or PREFIX_CODE
        :rtype: char
        """
        param_id = self.pool.get('ir.config_parameter').search(cr, uid, [('key', '=', 'default.country.code.phone')], context=context)
        if param_id:
            return self.pool.get('ir.config_parameter').read(cr, uid, param_id, ['value'], context=context)[0]['value']
        return PREFIX_CODE

    def get_linked_partners(self, cr, uid, ids, context=None):
        """
        ===================
        get_linked_partners
        ===================
        Return all partners ids linked to phones ids
        :param: ids
        :type: list of addresses ids
        :rparam: partner_ids
        :rtype: list of ids
        """
        coord_ids = self._get_linked_coordinates(cr, uid, ids, context=context)
        return self.pool['phone.coordinate'].get_linked_partners(cr, uid, coord_ids, context=context)

# view methods: onchange, button

    def onchange_type(self, cr, uid, ids, new_type, context=None):
        return {
            'value': {
                'also_for_fax': False,
             }
        }


class phone_coordinate(orm.Model):

    _name = 'phone.coordinate'
    _inherit = ['abstract.coordinate']
    _description = 'Phone Coordinate'

    _track = {
        'bounce_counter': {
            'ficep_phone.phone_failure_notification': lambda self, cr, uid, obj, ctx=None: obj.bounce_counter,
        },
    }

    _discriminant_field = 'phone_id'
    _undo_redirect_action = 'ficep_phone.phone_coordinate_action'

    _type_store_triggers = {
        'phone.coordinate': (lambda self, cr, uid, ids, context=None: ids, ['phone_id'], 10),
        'phone.phone': (lambda self, cr, uid, ids, context=None: self.pool['phone.phone']._get_linked_coordinates(cr, uid, ids, context=context), ['type', 'also_for_fax'], 10),
    }

    _columns = {
        'phone_id': fields.many2one('phone.phone', string='Phone', required=True, readonly=True, select=True),

        'coordinate_type': fields.related('phone_id', 'type', string='Phone Type', readonly=True,
                                          type='selection', selection=PHONE_AVAILABLE_TYPES,
                                          store=_type_store_triggers),
        'also_for_fax': fields.related('phone_id', 'also_for_fax', string='Also for fax', readonly=True,
                                          type='boolean', store=_type_store_triggers),
    }

    _rec_name = _discriminant_field

    _defaults = {
        'coordinate_type': False,
    }

# constraints

    _unicity_keys = 'partner_id, phone_id'

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        Automatically add the partner as follower of this new coordinate
        When 'is_main' is true the coordinate has to become the main coordinate for its
        associated partner.
        :rparam: id of the new coordinate
        :rtype: integer
        """
        vals['coordinate_type'] = self.pool.get('phone.phone').read(cr, uid, vals['phone_id'], ['type'], context=context)['type']
        new_id = super(phone_coordinate, self).create(cr, uid, vals, context=context)
        #add partner_id to the followers of the new postal_coordinate
        if vals.get('partner_id', False):
            wiz_invite_obj = self.pool['mail.wizard.invite']
            wiz_invite_id = wiz_invite_obj.create(cr, uid, {'res_model': self._name,
                                                            'res_id': new_id,
                                                            'partner_ids': [[6, False, [vals['partner_id']]]],
                                                            'send_mail': False,
                                                            }, context=context)
            wiz_invite_obj.add_followers(cr, uid, [wiz_invite_id], context=context)

        return new_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
