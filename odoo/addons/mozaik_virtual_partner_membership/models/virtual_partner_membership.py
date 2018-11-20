# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerMembership(models.Model):
    _name = "virtual.partner.membership"
    _description = "Partner/Membership"
    _inherit = [
        'abstract.virtual.model',
        'abstract.term.finder',
    ]
    _auto = False
    _terms = ['interest_ids', 'competency_ids']

    int_instance_id = fields.Many2one(
        store=True,
        search=None,
    )
    membership_state_id = fields.Many2one(
        comodel_name='membership.state',
        string="State",
    )
    reference = fields.Char()
    is_donor = fields.Boolean(
        string="Is a donor",
    )
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = super()._get_select() + """,
            m.int_instance_id,
            m.state_id as membership_state_id,
            m.reference as reference,
            p.is_donor,
            p.is_volunteer"""
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM res_partner AS p
            JOIN membership_line AS m
                ON (m.partner_id = p.id
                AND m.active = TRUE)
            LEFT OUTER JOIN postal_coordinate AS pc
                ON (pc.partner_id = p.id
                AND pc.active = TRUE
                AND pc.is_main = TRUE)
            LEFT OUTER JOIN email_coordinate AS e
                ON (e.partner_id = p.id
                AND e.active = TRUE
                AND e.is_main = TRUE)"""
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active = TRUE"