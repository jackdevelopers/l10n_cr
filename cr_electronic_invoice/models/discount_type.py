from odoo import models, fields


class DiscountType(models.Model):
    _name = "discount.type"

    # ==============================================================================================
    #                                          Discount TYPE
    # ==============================================================================================

    code = fields.Char(
        help='Discount related code.'
    )
    name = fields.Char(
        help='Discount code name.'
    )

