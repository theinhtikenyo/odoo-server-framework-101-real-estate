# here odoo is a package(imagine as a folder called /odoo) that has modules( imagine as python files(models.py,etc.,))
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from random import randint


# in models.Model, models is a python module from odoo package , and Model is a class
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        string="Date Availability",
        default=lambda self: fields.Datetime.now() + relativedelta(months=3),
    )
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price")
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    living_area = fields.Integer(string="Living Area")
    garden_area = fields.Integer(string="Garden Area")
    total_area = fields.Integer(compute="_compute_total_area")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )
    active = fields.Boolean(string="Active", default=True)

    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("offered", "Offer Received"),
            ("accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("cancelled", "Cancelled"),
        ],
        default="new",
        copy=False,  # that means when duplicating record, this state field will now be copied to new field
        required=True,
    )
    # A Property can only have one type, but there are many properties types can choose and assigned to a property
    # Imagine , a list dropdown appeares at UI
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer = fields.Many2one("res.partner", string="Buyer", copy=False)
    saleperson = fields.Many2one(
        "res.users", string="Saleperson", default=lambda self: self.env.user
    )
    # A property can have many tags , there are many properties (tags)
    # Imagine, Tags widget at UI
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    # we need to define many2one field at estate.property.offer model for estate_property model, so that we can use
    # Imagine, one2many as a list
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    best_price = fields.Float(compute="_compute_best_price", string="Best Offer")

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "A property expected price must be strictly positive",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price > 0)",
            "A property selling price must be strictly positive",
        ),
    ]

    @api.depends("garden_area", "living_area")
    # preferred to use since it can triggered outside of the context of a form view
    # easier to debug
    # when store true, care for dependencies , it can takes so long to compute
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("selling_price", "offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0.0

    # this is private method (starts with underscore) and it called internally
    @api.onchange("garden")
    # can trigger only at form view, so, never used at business logic
    def _onchange_garden(self):
        # @api.onchange does not require to loop
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # this is public method, it can be called xml-rpc, so need to return something, when in doubt , just return True
    def action_sold(self):
        for record in self:
            if record.state == "cancelled":
                raise UserError(_("Cancelled properties cannot be sold"))
            record.state = "sold"
            return True

    def action_cancel(self):
        for record in self:
            if record.state == "sold":
                raise UserError(_("Sold properties cannot be cancelled"))
            record.state = "cancelled"
            return True

    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            min_price = record.expected_price * 0.9
            # return value -1 , means a < b == true
            # return value 0 , means a == b
            # return value 1 , means a > b == true
            if float_compare(record.selling_price, min_price, precision_digits=2) == -1:
                raise UserError(
                    _(f"selling price cannot be lower than 90% of the expected price.")
                )

    @api.ondelete(at_uninstall=False)
    def _unlink_property(self):
        for record in self:
            if record.state not in ["new", "cancelled"]:
                raise UserError(
                    _("Property of state 'New' or 'Cancelled' cannot be deleted")
                )
