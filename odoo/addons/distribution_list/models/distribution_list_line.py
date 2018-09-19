# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ast
from odoo import api, models, exceptions, tools, fields, _
from odoo.fields import first
from odoo.osv import expression


class DistributionListLine(models.Model):
    """
    Model used to represents lines of distribution list.
    These lines are used to include or exclude some recordset based
    on a domain.
    """
    _name = 'distribution.list.line'
    _description = 'Distribution List Line'
    _order = 'name'

    name = fields.Char(
        required=True,
    )
    distribution_list_id = fields.Many2one(
        comodel_name="distribution.list",
        string="Distribution list",
        required=True,
        index=True,
        ondelete='cascade',
        copy=False,
    )
    exclude = fields.Boolean(
        default=False,
        help="Check this box to exclude the result of this filter/line on "
             "the related distribution list",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        related="distribution_list_id.company_id",
        store=True,
    )
    domain = fields.Text(
        "Expression",
        required=True,
        default="[]",
    )
    src_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        index=True,
        default=lambda self: self._get_default_src_model_id(),
        domain=lambda self: self._get_domain_src_model_id(),
    )
    bridge_field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Bridge field",
        help="Bridge field between the source model (of this line/filter) "
             "and the destination model (on the distribution list.",
        required=True,
    )

    _sql_constraints = [
        ('unique_name_by_dist_list', 'unique(name, distribution_list_id)',
         'The name of a filter must be unique. A filter with the same name '
         'already exists.'),
    ]

    @api.model
    def _get_src_model_names(self):
        """
        Get the list of available model name
        Intended to be inherited
        :return: list of string
        """
        return []

    @api.model
    def _get_domain_src_model_id(self):
        """
        Get domain of available models
        :return: list of tuple (domain)
        """
        mods = self._get_src_model_names() or ['res.partner']
        return [('model', 'in', mods)]

    @api.model
    def _get_default_src_model_id(self):
        """
        Get the default src model
        :return: model recordset
        """
        model = False
        mods = self._get_src_model_names() or ['res.partner']
        if len(mods) == 1:
            model = self.env['ir.model'].search([('model', 'in', mods)])
            model = model or self.env.ref('base.model_res_partner')
        return model

    @api.multi
    def _get_valid_bridge_fields(self):
        """
        Get every fields available for each distribution.list.line
        :return: dict
        """
        src_models = self.mapped("src_model_id")
        dst_models = self.mapped("distribution_list_id.dst_model_id")
        domain = [
            ('ttype', '=', 'many2one'),
            ('model_id', 'in', src_models.ids),
            ('relation', 'in', dst_models.mapped("model")),
        ]
        all_fields = self.env['ir.model.fields'].search(domain)

        domain = [
            ('ttype', '=', 'integer'),
            ('name', '=', 'id'),
            ('model_id', 'in', src_models.ids),
        ]
        all_id_fields = self.env['ir.model.fields'].search(domain)

        results = {}
        for record in self:
            available_fields = all_fields.filtered(
                lambda f, r=record: f.model_id == r.src_model_id and
                f.relation == r.distribution_list_id.dst_model_id.model)
            if record.distribution_list_id.dst_model_id == \
                    record.src_model_id:
                available_fields |= all_id_fields.filtered(
                    lambda f, r=record: f.model_id == r.src_model_id)
            results.update({
                record: available_fields,
            })
        return results

    @api.multi
    @api.constrains('bridge_field_id', 'src_model_id', 'distribution_list_id')
    def _constraint_valid_bridge_field_id(self):
        """
        Constrain to check if the bridge_field_id set is correct
        :return:
        """
        fields_available = self._get_valid_bridge_fields()
        # Available fields
        bad_dist_list_lines = self.filtered(
            lambda l: l.bridge_field_id not in fields_available.get(l))
        if bad_dist_list_lines:
            details = "\n- ".join(bad_dist_list_lines.mapped("name"))
            message = _("These distribution list lines are not valid because "
                        "the bridge field is not related to the destination "
                        "model set on the distribution list!"
                        "\n- %s") % details
            raise exceptions.ValidationError(message)

    @api.multi
    def _get_eval_domain(self):
        """
        Eval the domain
        Note: copy paste of the same Odoo function on ir.filters
        :return: list
        """
        self.ensure_one()
        return ast.literal_eval(self.domain)

    @api.onchange('src_model_id', 'distribution_list_id')
    def _onchange_src_model_id(self):
        self.domain = self._fields.get('domain').default(self)
        fields_available = self._get_valid_bridge_fields().get(self)
        if len(fields_available) == 1:
            self.bridge_field_id = fields_available
        else:
            self.bridge_field_id = fields_available.filtered(
                lambda s: s.name == 'id')
        result = {
            'domain': {
                'bridge_field_id': [('id', 'in', fields_available.ids)],
            },
        }
        return result

    def _save_domain(self, domain):
        """
        This method will update `domain`
        :param domain: str
        :return:
        """
        self.write({
            "domain": domain,
        })

    @api.multi
    def write(self, vals):
        """
        If `src_model_id` is changed and not `domain`, reset domain to its
        default value: `[]`
        :param vals: dict
        :return: bool
        """
        if vals.get('src_model_id') and not vals.get('domain'):
            vals.update({
                'domain': self._fields.get('domain').default(self),
            })
        return super().write(vals)

    @api.multi
    def _get_target_recordset(self):
        """
        Get target recordset where the related domain is applied with a AND
        between every domains
        :return: target recordset
        """
        # All current recordset should belong to the same model
        if not self:
            return False
        # The target model of every lines should be the same
        target_model = first(self).distribution_list_id.dst_model_id.model
        targets = self.env[target_model].browse()
        for target_model in self.mapped("src_model_id.model"):
            self_model = self.filtered(
                lambda r: r.bridge_field_id.model_id.model == target_model)
            domains = [r._get_eval_domain() for r in self_model]
            big_domain = expression.OR(domains)
            try:
                results = self.env[target_model].search(big_domain)
                for field_name in self_model.mapped("bridge_field_id.name"):
                    if field_name == 'id':
                        targets |= results
                    else:
                        targets |= results.mapped(field_name)
            except Exception as e:
                message = _("A filter for the target model %s is not valid.\n"
                            "Details: %s") % (target_model, tools.ustr(e))
                raise exceptions.UserError(message)
        return targets

    @api.multi
    def action_show_filter_result(self):
        """
        Show the result of the filter
        :return: dict/action
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Result of %s') % self.name,
            'view_mode': 'tree,form',
            'res_model': self.src_model_id.model,
            'context': self.env.context.copy(),
            'domain': self._get_eval_domain(),
            'target': 'current',
        }

    @api.multi
    def action_redefine_domain(self):
        """
        Allow to launch an action to redefine the filter domain
        """
        self.ensure_one()
        context = self.env.context.copy()
        context.update({
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': '%s List' % self.src_model_id.name,
            'res_model': self.src_model_id.model,
            'view_mode': 'tree',
            'target': 'new',
            'flags': {'search_view': True},
            'context': context,
        }