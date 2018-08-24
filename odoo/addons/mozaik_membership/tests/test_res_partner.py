# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import uuid
from datetime import date
from dateutil.relativedelta import relativedelta

from openerp.osv import orm
from anybox.testing.openerp import SharedSetupTransactionCase


class test_partner(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../mozaik_base/tests/data/res_partner_data.xml',
        # load structures
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_address/tests/data/reference_data.xml',
        '../../mozaik_address/tests/data/address_data.xml',
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_partner, self).setUp()

        self.partner_obj = self.registry('res.partner')
        self.ms_obj = self.registry('membership.state')
        self.ml_obj = self.registry('membership.line')
        self.prd_obj = self.registry('product.template')
        self.imd_obj = self.registry['ir.model.data']

        self.partner1 = self.browse_ref(
            '%s.res_partner_thierry' % self._module_ns)

        self.partner2 = self.browse_ref(
            '%s.res_partner_fgtb' % self._module_ns)

        self.user_model = self.registry('res.users')
        self.partner_jacques_id = self.ref(
            '%s.res_partner_jacques' % self._module_ns)
        self.group_fr_id = self.ref('mozaik_base.mozaik_res_groups_reader')

    def get_partner(self, partner_id=False):
        """
        Return a new browse record of partner
        """
        if not partner_id:
            name = uuid.uuid4()
            partner_values = {
                'lastname': name,
            }
            partner_id = self.partner_obj.create(self.cr, self.uid,
                                                 partner_values)
        # check each time the current state change
        return self.partner_obj.browse(self.cr, self.uid, partner_id)

    def test_workflow(self):
        """
        Test all possible ways of partner membership workflow
        Check `state_membership_id`:
        * create = without_membership
        * without_status -> member_candidate
        * without_status -> supporter -> member_candidate
            -> member_committee -> refused_member_candidate
            -> supporter -> member_committee -> refused_member_candidate
            -> member_candidate -> supporter -> former_supporter -> supporter
        * without_status -> member_candidate -> member_committee
            -> member -> former_member -> former_member_committee -> member
            -> former_member -> former_member_committee
                -> inappropriate_former_member
        * former_member -> inappropriate_former_member -> former_member
        * former_member -> break_former_member -> former_member
        * member -> expulsion_former_member -> former_member
        * member -> resignation_former_member -> former_member

        * check also for voluntaries and local only fields automatic update
        """
        cr, uid = self.cr, self.uid
        partner_obj = self.partner_obj
        prd_obj = self.prd_obj
        imd_obj = self.imd_obj
        today = date.today().strftime('%Y-%m-%d')

        # create = without_membership
        partner = self.get_partner()
        self.assertEqual(
            partner.membership_state_code, 'without_membership')
        self.assertFalse(partner.regional_voluntary)

        # without_status -> member_candidate
        partner.local_only = True
        partner.write({'accepted_date': today, 'free_member': False})
        self.assertEqual(
            partner.membership_state_code, 'member_candidate')
        self.assertTrue(partner.regional_voluntary)
        self.assertFalse(partner.local_only)

        nbl = 0

        # without_status -> supporter
        partner = self.get_partner()
        partner.write({
            'accepted_date': today, 'free_member': True,
            'del_doc_date': today,
        })
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'supporter')
        self.assertFalse(partner.regional_voluntary)

        # supporter -> former_supporter
        partner_obj.resign(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'former_supporter')
        self.assertFalse(partner.regional_voluntary)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'supporter')
        self.assertFalse(partner.regional_voluntary)

        # supporter -> member_candidate
        partner.write({'accepted_date': today, 'free_member': False})
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member_candidate')
        self.assertTrue(partner.regional_voluntary)
        self.assertFalse(partner.del_doc_date)

        # member_candidate -> supporter
        partner.write({'decline_payment_date': today, 'free_member': True})
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'supporter')
        self.assertFalse(partner.regional_voluntary)

        # supporter -> member_candidate (already tested)
        partner.write({'accepted_date': today, 'free_member': False})
        nbl += 1

        # member_candidate -> refused_member_candidate
        partner.write({'rejected_date': today})
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'refused_member_candidate')

        # refused_member_candidate -> member_candidate
        partner.write({
            'accepted_date': today,
            'free_member': False,
            'regional_voluntary': False,
        })
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member_candidate')
        self.assertFalse(partner.regional_voluntary)

        # member_candidate -> member_committee
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member_committee')
        self.assertFalse(partner.regional_voluntary)

        # member_committee -> refused_member_candidate
        partner.write({'rejected_date': today, 'regional_voluntary': True})
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'refused_member_candidate')
        self.assertTrue(partner.regional_voluntary)

        # refused_member_candidate -> supporter
        partner.write({'accepted_date': today, 'free_member': True})
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'supporter')
        self.assertFalse(partner.regional_voluntary)

        # supporter -> member_committee
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member_committee')
        self.assertTrue(partner.regional_voluntary)

        # member_committee -> member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'accept')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member')
        self.assertTrue(partner.regional_voluntary)

        # member -> former_member
        partner.write({'decline_payment_date': today})
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'former_member')

        # former_member -> former_member_committee
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'former_member_committee')

        # former_member_committee -> inappropriate_former_member
        partner_obj.exclude(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'inappropriate_former_member')

        # inappropriate_former_member -> former_member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'former_member')

        # former_member -> inappropriate_former_member
        partner_obj.exclude(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'inappropriate_former_member')

        # inappropriate_former_member -> former_member (already tested)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1

        # former_member -> break_former_member
        partner_obj.resign(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'break_former_member')

        # break_former_member -> former_member
        partner.local_only = True
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'former_member')
        self.assertFalse(partner.local_only)

        # former_member -> former_member_committee (already tested)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1

        # former_member_committee -> member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'accept')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member')

        # member -> resignation_former_member
        partner_obj.resign(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'resignation_former_member')
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'former_member')

        # former_member -> former_member_committee -> member (already tested)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        ml = partner.current_membership_line_id
        def_prd_id = prd_obj._get_default_subscription(cr, uid)
        ml.write({
            'product_id': def_prd_id,
            'price': 44.44,
        })
        self.assertEqual(partner.subscription_product_id.id, def_prd_id)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'accept')
        nbl += 1

        # member -> member (with free subscription)
        partner_obj.register_free_membership(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'member')
        ml = partner.current_membership_line_id
        self.assertEqual(ml.price, 0.0)
        free_prd_id = imd_obj.xmlid_to_res_id(
            cr, uid, 'mozaik_membership.membership_product_free')
        self.assertEqual(partner.subscription_product_id.id, free_prd_id)

        # member -> expulsion_former_member
        partner_obj.exclude(cr, uid, [partner.id])
        nbl += 1
        self.assertEqual(
            partner.membership_state_code, 'expulsion_former_member')
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEqual(partner.membership_state_code, 'former_member')
        self.assertTrue(partner.regional_voluntary)

        # number of membership lines ?
        self.assertEqual(len(partner.membership_line_ids), nbl)

    def test_update_membership_line(self):
        """
        This method does not create a membership_line if partner has no status
        Otherwise a membership_line is created:
        First time:
            * date from = today - 3 days
            * membership_state = partner status
            * date_to = False
            * active = True
        Second time:
            * the first membership_line is updated:
                 * date_to = today
                 * active = False
            * a new one is created:
                 * date from = today
                 * membership_state = partner status
                 * date_to = False
                 * active = True
        """
        partner, partner_obj = self.partner1, self.partner_obj
        cr, uid, context = self.cr, self.uid, {'active_test': False}
        partner = partner_obj.browse(cr, uid, partner.id, context=context)

        partner_obj._update_membership_line(cr, uid, [partner.id])
        self.assertFalse(partner.membership_line_ids)

        today = (date.today() - relativedelta(days=3)).strftime('%Y-%m-%d')
        partner.write({'accepted_date': today})
        self.assertEqual(1, len(partner.membership_line_ids))
        membership_line = partner.membership_line_ids[0]
        self.assertTrue(membership_line.active)
        self.assertEqual(membership_line.date_from, today)
        self.assertFalse(membership_line.date_to)
        self.assertEqual(
            membership_line.state_id, partner.membership_state_id)

        today = date.today().strftime('%Y-%m-%d')
        partner_obj._update_membership_line(cr, uid, [partner.id])
        self.assertEqual(2, len(partner.membership_line_ids))
        self.assertFalse(membership_line.active)
        self.assertEqual(membership_line.date_to, today)

        membership_line = partner.membership_line_ids.filtered(
            lambda s: s.id != membership_line.id)
        self.assertTrue(membership_line.active)
        self.assertEqual(membership_line.date_from, today)
        self.assertFalse(membership_line.date_to)
        return

    def test_update_is_company(self):
        """
        Check that the existence of a workflow attached to a partner is
        correctly handled regarding the flag is_company:
        1- True: no workflow, state=None
        2- False: with workflow, state!=None
        3- is_company: True=>False: always possible
        4- is_company: False=>True: only possible without membership history
        5- otherwise exception
        """
        cr, uid, context = self.cr, self.uid, {}
        partner, partner_obj = self.partner2, self.partner_obj

        pid = partner.id

        def wkf_exist():
            cr.execute("SELECT 1 "
                       "FROM wkf w, wkf_instance i "
                       "WHERE i.wkf_id = w.id "
                       "AND w.osv = 'res.partner' "
                       "AND i.res_id = %s",
                       (pid,))
            one = cr.fetchone()
            return one

        # 1- True: no workflow, state=None
        self.assertFalse(
            wkf_exist(),
            'No workflow should be existed for a legal person')
        self.assertFalse(
            partner.membership_state_id,
            'Field membership_state_id should be None '
            'because the partner is a company')

        # 2- False: with workflow, state!=None
        # 3- is_company: True => False: always possible
        partner_obj.write(cr, uid, pid, {'is_company': False})
        self.assertTrue(
            wkf_exist(),
            'A workflow should be existed for a natural person')
        self.assertTrue(
            partner.membership_state_id,
            'Field membership_state_id should be initialised '
            'because the partner is not a company')

        # 4- is_company: False=>True: only possible without membership history
        partner_obj.write(cr, uid, pid, {'is_company': True})
        self.assertFalse(
            wkf_exist(),
            'No workflow should be existed for a legal person')
        self.assertFalse(
            partner.membership_state_id,
            'Field membership_state_id should be None '
            'because the partner is a company')
        pass

    def test_change_instance(self):
        '''
        Check that instance well updated into the partner when its main postal
        coo is changed
        '''
        cr, uid, context = self.cr, self.uid, {}
        postal_obj = self.registry['postal.coordinate']
        address_obj = self.registry['address.address']
        zip_obj = self.registry['address.local.zip']

        int_instance_id = self.ref('%s.int_instance_06' % self._module_ns)

        postal_ids = postal_obj.search(cr, uid, [], limit=1, context=context)
        postal_rec = postal_obj.browse(cr, uid, postal_ids, context=context)[0]
        partner_id = postal_rec.partner_id.id
        vals = {
            'local_zip': '123456789',
            'town': 'numbers',
            'int_instance_id': int_instance_id,
        }
        zip_id = zip_obj.create(cr, uid, vals, context=context)
        vals = {
            'country_id': self.ref("base.be"),
            'address_local_zip_id': zip_id,
        }
        address_id = address_obj.create(cr, uid, vals, context=context)
        vals = {
            'address_id': address_id,
            'partner_id': partner_id,
            'is_main': True,
        }
        postal_id = postal_obj.create(cr, uid, vals, context=context)
        postal_rec = postal_obj.browse(cr, uid, postal_id, context=context)
        self.assertEqual(
            int_instance_id, postal_rec.partner_id.int_instance_id.id)

    def test_generate_membership_reference(self):
        """
        Check if the membership reference match the arbitrary pattern:
          'MS: YYYY/<partner-id>'
        """
        cr, uid, context = self.cr, self.uid, {}
        p_obj = self.partner_obj
        # create a partner
        partner_id = p_obj.create(
            cr, uid, {'lastname': '%s' % uuid.uuid4()}, context=context)
        year = str(date.today().year)
        # generate the reference
        genref = p_obj._generate_membership_reference(
            cr, uid, partner_id, year, context=context)

        ref = 'MS: %s/%s' % (year, partner_id)
        self.assertEqual(genref, ref)

    def test_create_user_from_partner(self):
        """
        Test the propagation of int_instance into the int_instance_m2m_ids
        when creating a user from a partner
        """
        cr, uid, context = self.cr, self.uid, {}
        jacques_id = self.partner_jacques_id
        fr_id = self.group_fr_id
        partner_model, user_model = self.partner_obj, self.user_model

        # Check for reference data
        dom = [('partner_id', '=', jacques_id)]
        vals = user_model.search(cr, uid, dom, context=context)
        self.assertFalse(
            len(vals), 'Wrong expected reference data for this test')
        dom = [('id', '=', jacques_id), ('ldap_name', '>', '')]
        vals = partner_model.search(cr, uid, dom, context=context)
        self.assertFalse(
            len(vals), 'Wrong expected reference data for this test')

        # Create a user from a partner
        partner_model.create_user(
            cr, uid, 'jack', jacques_id, [fr_id], context=context)
        jack = partner_model.browse(cr, uid, jacques_id, context=context)
        self.assertEqual(
            [jack.int_instance_id.id], jack.int_instance_m2m_ids.ids,
            'Update partner fails with wrong int_instance_m2m_ids')