# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, models, fields
from odoo.addons.queue_job.job import job

WORKER_PIVOT = 10


class PassFormerMember(models.TransientModel):

    _name = "pass.former.member"
    _description = 'Wizard to Transform Members to Former Members'

    nb_selected = fields.Integer(string='Selected Partners')
    concerned_members = fields.Text()
    concerned_partner_ids = fields.Many2many(
        comodel_name="res.partner", ondelete="cascade", required=True)
    go = fields.Boolean()

    @api.model
    def _get_selected_values(self):
        partner_obj = self.env['res.partner']
        partners = partner_obj.browse()
        concerned_partner_ids = partner_obj.browse()

        if self.env.context.get('active_domain'):
            active_domain = self.env.context.get('active_domain')
            partners = partner_obj.search(active_domain)
        elif self.env.context.get('active_ids'):
            partners = partner_obj.browse(
                self.env.context.get('active_ids'))

        if partners:
            # search member with reference
            concerned_partner_ids = partners.filtered(lambda s: s.reference)
            domain = [('id', 'in', partners.ids), ('reference', '!=', False)]
            data = partner_obj.read_group(
                domain, ['membership_state_id'], ['membership_state_id'],
                orderby='membership_state_id ASC')
            concerned_partners = [
                '%s: %s' % (st['membership_state_id'][1],
                            st['membership_state_id_count'])
                for st in data if st['membership_state_id']
            ]
            concerned_partners = '\n'.join(concerned_partners)
        return partners, concerned_partner_ids, concerned_partners

    @api.model
    def default_get(self, fields_list):
        """
        To get default values for the object.
        """
        res = super().default_get(fields_list)
        current_fields = ['nb_selected',
                          'concerned_members',
                          'concerned_partner_ids',
                          'go']
        if any(el in fields_list for el in current_fields):
            partner_ids, concerned_partner_ids, concerned_members = \
                self._get_selected_values()
            res['nb_selected'] = len(partner_ids)
            res['concerned_members'] = concerned_members
            res['concerned_partner_ids'] = [(6, 0, concerned_partner_ids.ids)]
            curr_month = date.today().month
            date_ok = curr_month in self._get_available_months()
            res['go'] = date_ok and concerned_partner_ids

        return res

    def _get_available_months(self):
        return [7, 8, 9]

    @api.multi
    def pass_former_member(self):
        """
        Pass to former Member for all partner
        If concerned partner number is > to the ir.parameter value then
        call connector to delay this work
        **Note**
        ir.parameter or `WORKER_PIVOT`
        """

        try:
            parameter_obj = self.env['ir.config_parameter']
            worker_pivot = int(parameter_obj.get_param(
                'worker_pivot', WORKER_PIVOT))
        except ValueError:
            worker_pivot = WORKER_PIVOT
        for wiz in self:
            partner_ids = wiz.concerned_partner_ids
            if len(partner_ids) > worker_pivot:
                description = ("Pass former member for partners %s" %
                               ", ".join(partner_ids.ids))
                self.with_delay(description=description)\
                    .pass_former_member_action(partner_ids)
            else:
                self.pass_former_member_action(partner_ids)

    @job(default_channel="root.pass_former_member")
    def pass_former_member_action(self, partners):
        """
        Pass to former Member for each partner
        Reset reference for each other
        """
        partners.decline_payment()
        partners = partners.filtered(lambda s: s.reference)
        if partners:
            partners.write({'reference': False})
