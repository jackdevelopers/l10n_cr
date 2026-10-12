from odoo.fields import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestFePrevalidation(AccountTestInvoicingCommon):
    """Validación previa al envío: datos que Hacienda rechazaría aunque el XML cumpla el XSD."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.id_fisica = env['identification.type'].search([('code', '=', '01')], limit=1)
        cls.id_extranjero = env['identification.type'].search([('code', '=', '05')], limit=1)
        cls.country_cr = env.ref('base.cr')
        cls.partner_cr = env['res.partner'].create({
            'name': 'Cliente CR',
            'vat': '192150558',
            'country_id': cls.country_cr.id,
            'identification_id': cls.id_fisica.id,
        })
        # CABYS de bien (prótesis dental) y de servicio (empieza con 5 a 9)
        cls.product_bien = env['product.product'].create({
            'name': 'Bien con CABYS de bien', 'type': 'consu', 'cabys_code': '4817106030500'})
        cls.product_servicio = env['product.product'].create({
            'name': 'Servicio con CABYS de servicio', 'type': 'service', 'cabys_code': '9331100000000'})
        cls.product_servicio_cabys_bien = env['product.product'].create({
            'name': 'Servicio con CABYS de bien', 'type': 'service', 'cabys_code': '4817106030500'})
        cls.product_bien_cabys_servicio = env['product.product'].create({
            'name': 'Bien con CABYS de servicio', 'type': 'consu', 'cabys_code': '9331100000000'})
        cls.product_cabys_corto = env['product.product'].create({
            'name': 'CABYS corto', 'type': 'consu', 'cabys_code': '12345'})

    def _invoice(self, product, partner=None, tipo='FE', move_type='out_invoice'):
        move = self.env['account.move'].create({
            'move_type': move_type,
            'partner_id': (partner or self.partner_cr).id,
            'invoice_line_ids': [Command.create({
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'price_unit': 30000.0,
                'quantity': 1,
            })],
        })
        move.tipo_documento = tipo
        return move

    def test_coherent_invoice_has_no_errors(self):
        self.assertFalse(self._invoice(self.product_bien)._get_einvoice_prevalidation_errors())
        self.assertFalse(self._invoice(self.product_servicio)._get_einvoice_prevalidation_errors())

    def test_zero_price_line(self):
        """Caso factura 39486 de Packlab: línea con precio unitario 0 (-150)."""
        move = self._invoice(self.product_bien)
        move.invoice_line_ids = [Command.create({
            'product_id': self.product_bien.id,
            'product_uom_id': self.product_bien.uom_id.id,
            'price_unit': 0.0,
            'quantity': 1,
        })]
        errors = move._get_einvoice_prevalidation_errors()
        self.assertEqual(len(errors), 1)
        self.assertIn('-150', errors[0])

    def test_invalid_cabys_format(self):
        errors = self._invoice(self.product_cabys_corto)._get_einvoice_prevalidation_errors()
        self.assertEqual(len(errors), 1)
        self.assertIn('13 dígitos', errors[0])

    def test_costa_rican_vat_with_foreign_id_type(self):
        """Caso factura 77712 de Munkel: cédula de CR con tipo 05 en una FE (-409)."""
        self.partner_cr.identification_id = self.id_extranjero
        errors = self._invoice(self.product_bien)._get_einvoice_prevalidation_errors()
        self.assertEqual(len(errors), 1)
        self.assertIn('-409', errors[0])
        # En un tiquete electrónico el tipo 05 no se rechaza
        self.assertFalse(self._invoice(self.product_bien, tipo='TE')._get_einvoice_prevalidation_errors())

    def test_credit_note_without_cabys_is_not_blocked(self):
        product = self.env['product.product'].create({'name': 'Sin CABYS', 'type': 'consu'})
        move = self._invoice(product, tipo='NC', move_type='out_refund')
        self.assertFalse(move._get_einvoice_prevalidation_errors())

    def test_prevalidation_sets_error_xsd_and_posts_message(self):
        move = self._invoice(self.product_cabys_corto)
        self.assertTrue(move._post_prevalidation_errors())
        self.assertEqual(move.state_tributacion, 'error_xsd')
        self.assertIn('13 dígitos', move.message_ids[0].body)
        # Corregido el dato, la validación pasa y no marca nada
        move.invoice_line_ids.product_id.cabys_code = '4817106030500'
        self.assertFalse(move._post_prevalidation_errors())

    def test_sent_currency_rate_uses_referenced_xml(self):
        """Caso NC 39464 de Packlab: la NC debe llevar el TipoCambio enviado en el documento
        de referencia (-511), no la tasa de la fecha de la factura."""
        import base64
        move = self._invoice(self.product_bien)
        self.assertFalse(move._get_sent_currency_rate(move))
        move.xml_comprobante = base64.b64encode(b'<R><TipoCambio>457.8</TipoCambio></R>')
        self.assertEqual(move._get_sent_currency_rate(move), 457.8)
