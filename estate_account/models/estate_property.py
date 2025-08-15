from odoo import models, fields, Command, api, _


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):

        self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.buyer.id,
                "journal_id": 1,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": self.name,
                            "quantity": 1.0,
                            "price_unit": self.selling_price,
                        }
                    ),
                ],
            }
        )

        return super().action_sold()
