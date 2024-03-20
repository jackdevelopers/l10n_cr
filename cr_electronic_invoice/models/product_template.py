from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductElectronic(models.Model):
    _inherit = "product.template"

    # ==============================================================================================
    #                                          PRODUCT TEMPLATES
    # ==============================================================================================

    @api.model
    def _default_code_type_id(self):
        code_type_id = self.env['code.type.product'].search([('code', '=', '04')], limit=1)
        return code_type_id or False

    commercial_measurement = fields.Char(
        string="Commercial Unit"
    )
    code_type_id = fields.Many2one(
        comodel_name="code.type.product",
        string="Code Type",
        default=_default_code_type_id
    )
    tariff_head = fields.Char(
        string="Export Tax rate",
        help='Tax rate to apply for exporting invoices'
    )
    cabys_code = fields.Char(
        string="CAByS Code",
        help='CAByS code from Ministerio de Hacienda'
    )
    economic_activity_id = fields.Many2one(
        comodel_name="economic.activity",
        string="Economic Activity",
        help='Economic activity code from Ministerio de Hacienda'
    )
    non_tax_deductible = fields.Boolean(
        string='Is Non Tax Deductible',
        help='Indicates if this product is non-tax deductible'
    )

    iva_sales_type = fields.Selection([('s_goods','Bienes'),('s_services','Servicios')],
                                      string="Clasificacion Ventas")
    iva_purchase_type = fields.Selection([('c_goods','Compra Bien'),
                                       ('g_goods','Gasto Bien'),
                                       ('g_service','Gasto Servicio'),
                                       ('g_no_sujeto','Gasto no sujeto'),
                                       ('g_no_debu','Gasto no Deducible'),
                                       ('g_external','Gasto Exterior'),
                                       ('g_exo','Gasto Exonerado'),
                                       ('c_exo','Compra Exonerado')
                                       ], string="Clasificacion Compras")

    default_code = fields.Char(string='Internal Reference', index=True, copy=False)

    @api.constrains('default_code')
    def _check_default_code_length(self):
        for record in self:
            if record.default_code and len(record.default_code) > 20:  # Cambia 20 al máximo de longitud deseado
                raise ValidationError('El código por defecto debe tener como máximo 20 caracteres.')