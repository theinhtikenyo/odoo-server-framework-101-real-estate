from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property",
        "saleperson",
        domain=[
            ("state", "in", ["offered", "new"])
        ],  # we can apply domain at fields definition
    )
