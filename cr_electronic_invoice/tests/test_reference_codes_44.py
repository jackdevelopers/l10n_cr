import os

from lxml import etree

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.cr_electronic_invoice.models import api_facturae
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestReferenceCodes44(AccountTestInvoicingCommon):
    """Ajustes al Anexo 4.4 de Hacienda (bitácora 22/04/2026, obligatorios desde 01/11/2026)."""

    def test_reference_codes_loaded(self):
        codes = set(self.env['reference.code'].search([]).mapped('code'))
        self.assertTrue({'13', '14', '15', '16', '17'} <= codes)

    def test_reference_documents_loaded(self):
        codes = set(self.env['reference.document'].search([]).mapped('code'))
        self.assertTrue({'19', '20'} <= codes)

    def test_xsd_accepts_new_codes(self):
        for xsd_file in api_facturae.XSD_FILES.values():
            xsd = os.path.join(api_facturae.XSD_DIR, xsd_file)
            tree = etree.parse(xsd)
            ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
            for type_name, expected in (('CodigoReferenciaType', {'13', '14', '15', '16', '17'}),
                                        ('TipoDocReferenciaType', {'19', '20'})):
                values = set(tree.xpath(
                    '//xs:simpleType[@name="%s"]//xs:enumeration/@value' % type_name, namespaces=ns))
                if values:
                    self.assertTrue(expected <= values, '%s: %s sin %s' % (xsd_file, type_name, expected - values))

    def test_clean_identification(self):
        self.assertEqual(api_facturae.clean_identification('3-101-123456', '02'), '3101123456')
        self.assertEqual(api_facturae.clean_identification('a1b-2c3', '02'), 'A1B2C3')
        self.assertEqual(api_facturae.clean_identification('1-0192-0558', '01'), '101920558')
        self.assertTrue(api_facturae.valid_juridica_length('3101123456'))
        self.assertTrue(api_facturae.valid_juridica_length('A1B2C3'))
        self.assertFalse(api_facturae.valid_juridica_length('A1B2'))
