from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _descripton = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        copy=False,
        string="Status",
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    # that property_id will link to estate_property one2many
    property_id = fields.Many2one(
        "estate.property", string="Property", required=True, ondelete="cascade"
    )
    property_type_id = fields.Many2one(
        related="property_id.property_type_id", store=True, string="Property Type"
    )
    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        string="Deadline",
    )
    _sql_constraints = [
        (
            "check_price",
            "CHECK(price > 0)",
            "A property offer price must be strictly positive",
        ),
    ]

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = (
                record.create_date or fields.Datetime.now()
            ) + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                # Calculate validity = difference in days between date_deadline and create_date (or today)
                start_date = (
                    record.create_date.date()
                    if record.create_date
                    else fields.Date.context_today(record)
                )
                # Make sure to get integer days difference
                delta = record.date_deadline - start_date
                record.validity = delta.days if delta.days >= 0 else 0

    def action_accept(self):
        for record in self:
            accepted_offer = self.search_count(
                [
                    ("property_id", "=", record.property_id.id),
                    ("status", "=", "accepted"),
                ]
            )
            if accepted_offer:
                raise UserError(_("Only one offer can be accepted for a property."))
            record.status = "accepted"
            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id

    def action_refuse(self):
        for record in self:
            record.status = "refused"

    @api.model
    def create(self, vals):
        property_record = self.env["estate.property"].browse(vals["property_id"])
        if property_record:
            property_record.state = "offered"
        return super().create(vals)
