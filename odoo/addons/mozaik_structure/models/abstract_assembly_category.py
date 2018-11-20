# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


class AbstractAssemblyCategory(models.AbstractModel):

    _name = 'abstract.assembly.category'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Assembly Category'
    _order = 'power_level_id, name'
    _unicity_keys = 'power_level_id, name'
    _log_access = True

    name = fields.Char(
        required=True,
        index=True,
        track_visibility='onchange',
    )
    duration = fields.Integer(
        'Duration of Mandates',
        track_visibility='onchange',
        group_operator='min',
    )
    months_before_end_of_mandate = fields.Integer(
        'Alert Delay (#Months)',
        track_visibility='onchange',
        group_operator='min',
    )
    power_level_id = fields.Many2one(
        'abstract.power.level',
        string='Power Level',
        index=True,
        track_visibility='onchange',
    )
    assembly_ids = fields.One2many(
        'abstract.assembly',
        'assembly_category_id',
        string='Assemblies',
        domain=[('active', '=', True)],
    )
    assembly_inactive_ids = fields.One2many(
        'abstract.assembly',
        'assembly_category_id',
        string='Assemblies',
        domain=[('active', '=', False)],
    )

    @api.multi
    @api.constrains('power_level_id')
    def _check_power_level(self):
        """
        Check if power level is consistent with all related assembly
        Note:
        Only relevant for internal and state assemblies
        """
        for cat in self:
            assemblies = cat.assembly_ids + cat.assembly_inactive_ids
            power_levels = (
                assemblies.mapped('instance_id.power_level_id') -
                cat.power_level_id)
            if power_levels:
                raise exceptions.ValidationError(
                    _('Power level is inconsistent with '
                      'power level of all related assemblies'))