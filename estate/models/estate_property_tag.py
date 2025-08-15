from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(
        string="Color Index",
    )

    _sql_constraints = [
        ("uniq_name", "unique(name)", "A property tag name must be unique"),
    ]
