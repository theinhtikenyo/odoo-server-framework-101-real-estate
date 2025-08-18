from odoo import models, fields


class EstateLocation(models.Model):
    _name = "estate.property.location"
    _description = "Estate Property Location"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence", default=1)
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        default=lambda self: self.env.company.country_id.id,
    )
    state_id = fields.Many2one(
        "res.country.state", string="State", domain="[('country_id', '=?', country_id)]"
    )
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street2")
    city = fields.Char(string="City")
    zip = fields.Integer(string="Zip")
