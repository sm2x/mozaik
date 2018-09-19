# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.osv import expression


class DistributionListLine(models.Model):
    _name = "distribution.list.line"
    _inherit = [
        'mozaik.abstract.model',
        'distribution.list.line',
    ]
    _unicity_keys = 'N/A'

    name = fields.Char(
        track_visibility='onchange',
    )
    domain = fields.Text(
        track_visibility='onchange',
    )
    src_model_id = fields.Many2one(
        track_visibility='onchange',
    )

    @api.multi
    def action_show_filter_result_without_coordinate(self):
        """
        Show the result of the list without coordinate
        :return: dict/action
        """
        self.ensure_one()
        result = self.action_show_filter_result()
        result.update({
            'name': _('Result of %s without coordinate') % self.name
        })
        domain = result.get('domain', [])
        domain = expression.AND([domain, [('active', '=', False)]])
        result.update({
            'domain': domain,
        })
        return result