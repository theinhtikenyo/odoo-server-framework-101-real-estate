from odoo import models, fields, api


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "sequence,name"  # it says sequence should come first, but as i check , we can even remove sequence

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(default=1, string="Sequence")

    _sql_constraints = [
        ("uniq_name", "unique(name)", "A property type name must be unique"),
    ]

    property_ids = fields.One2many("estate.property", "property_type_id")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_offer_count", string="Offer Count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
