# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random
from odoo import api, fields, models


class MassMailing(models.Model):
    _inherit = 'mail.mass_mailing'

    create_uid = fields.Many2one(
        comodel_name='res.users',
        readonly=True,
    )
    group_id = fields.Many2one(
        comodel_name='mail.mass_mailing.group',
        string='Group',
        copy=True,
    )
    group_total_sent = fields.Integer(
        related='group_id.total_sent',
    )
    mailing_model = fields.Char(
        default='email.coordinate',
    )

    @api.model
    def _get_mailing_model(self):
        """
        Remove last insert: `mail.mass_mailing.contact`
        :return:
        """
        result = super()._get_mailing_model()
        if result:
            # remove last insert: mailing list
            result.pop()
        return result

    @api.multi
    def get_recipients(self):
        """
        Override this method to get resulting ids of the distribution list
        :param mailing:
        :return: recordset
        """
        self.ensure_one()
        if self.distribution_list_id:
            if self.mailing_model == 'email.coordinate':
                dl = self.distribution_list_id.with_context(
                    main_object_field='email_coordinate_id',
                    main_target_model='email.coordinate'
                )
                mains, __ = dl._get_complex_distribution_list_ids()
                if self.contact_ab_pc < 100 or self.group_id:
                    topick = int(len(mains) / 100.0 * self.contact_ab_pc)
                    already_mailed = self.env['mail.mail.statistics'].search([
                        ('mass_mailing_id.group_id', '=', self.group_id.id),
                    ]).mapped('res_id')
                    remaining = set(mains.ids).difference(already_mailed)
                    if topick > len(remaining):
                        topick = len(remaining)
                    res_ids = random.sample(remaining, topick)
                else:
                    res_ids = mains.ids
                return res_ids
        return super().get_recipients()

    @api.multi
    def send_custom(self):
        self.ensure_one()
        group = self.group_id
        unsent_percent = (100 - group.total_sent)
        wiz = self.env['distribution.list.mass.function'].create({
            'trg_model': 'email.coordinate',
            'e_mass_function': 'email_coordinate_id',
            'mass_mailing_name': self.name,
            'subject': self.name,
            'body': self.body_html,
            'contact_ab_pc': unsent_percent,
            'distribution_list_id': group.distribution_list_id.id,
            'include_unauthorized': group.include_unauthorized,
            'internal_instance_id': group.internal_instance_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': wiz.id,
            'res_model': wiz._name,
            'target': 'new',
            'context': dict(self.env.context, mailing_group_id=group.id),
        }

    @api.multi
    def compare_group(self):
        self.ensure_one()
        group = self.group_id
        context = self.env.context.copy()
        context.update({
            "search_default_group_id": group.id,
            "group_by": 'trial',
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'graph',
            'res_model': 'mail.statistics.report',
            'context': context,
        }