# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CopyIntMandateWizard(models.TransientModel):
    _inherit = 'abstract.copy.mandate.wizard'
    _name = "copy.int.mandate.wizard"

    _mandate_assembly_foreign_key = 'int_assembly_id'

    mandate_id = fields.Many2one(
        comodel_name='int.mandate',
        string='Internal Mandate')
    assembly_id = fields.Many2one(
        comodel_name='int.assembly',
        string='Internal Assembly')
    new_assembly_id = fields.Many2one(
        comodel_name='int.assembly',
        string='Internal Assembly')
    instance_id = fields.Many2one(
        string='Internal Instance')