# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    ultima_respuesta = fields.Text(string="Latest API response",
                                   help="Last API Response, this allows debugging errors if they exist")
    url_base = fields.Char(string="URL Base",
                           help="URL Base of the END POINT",
                           default="https://apis.gometa.org/cedulas/")
    is_gometa_api = fields.Boolean(default=True)

    url_key = fields.Char(string="Api Key Gometa",
                           help="apis.gometa.org project",
                           default="ibOeujS0AIoRUVN")

    get_tributary_information = fields.Boolean(default=True)
    @api.model
    def get_values(self):
        res = super().get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            ultima_respuesta=get_param('ultima_respuesta'),
            url_base=get_param('url_base'),
            is_gometa_api=get_param('is_gometa_api'),
            url_key= get_param('url_key'),
            get_tributary_information= get_param('get_tributary_information'),
        )
        return res

    @api.model
    def set_values(self):
        super().set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('ultima_respuesta', self.ultima_respuesta)
        set_param('url_base', self.url_base)
        set_param('is_gometa_api', self.is_gometa_api)
        set_param('url_key', self.url_key)
        set_param('get_tributary_information', self.get_tributary_information)
