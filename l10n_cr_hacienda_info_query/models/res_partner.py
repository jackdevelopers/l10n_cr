from odoo import models, api, _
from datetime import datetime
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def clean_vat(self, vat):
        if vat:
            return ''.join(i for i in vat if i.isdigit())

    def get_information(self, vat):
        set_param = self.env["ir.config_parameter"].sudo().set_param
        get_param = self.env["ir.config_parameter"].sudo().get_param

        url_base = get_param("url_base")
        get_tributary_information = get_param("get_tributary_information")
        is_gometa_api = get_param("is_gometa_api")

        if get_tributary_information:
            url_base = url_base.strip()
            end_point = url_base + vat
            headers = {
                "content-type": "application/json",
            }
            if is_gometa_api:
                end_point = end_point + '&key=' + get_param("url_key")

            try:
                response = requests.get(end_point, headers=headers, timeout=10)

                ultimo_mensaje = (
                        "Fecha/Hora: "
                        + str(datetime.now())
                        + ", Codigo: "
                        + str(response.status_code)
                        + ", Mensaje: "
                        + str(response._content.decode())
                )
                set_param("ultima_respuesta", ultimo_mensaje)
                if response.status_code in (200, 202) and len(response._content) > 0:
                    content = json.loads(str(response._content, "utf-8"))
                    if content.get("nombre") and content.get("tipoIdentificacion"):
                        self.name = content.get("nombre")
                        if "identification_id" in self._fields:
                            clasificacion = content.get("tipoIdentificacion")

                            self.identification_id = (
                                self.env["identification.type"].search([("code", "=", clasificacion)], limit=1).id
                            )
                    a_codes = list([])
                    if content.get('actividades') and 'activity_id' in self._fields:
                        for act in content.get('actividades'):
                            if act.get('estado') == 'A':
                                a_codes.append(act.get('codigo'))
                        economic_activities = (self.env['economic.activity'].with_context(active_test=False).
                                               search([('code', 'in', a_codes)]))
                        if len(economic_activities) >= 1:
                            self.activity_id = economic_activities[0]
                            self.economic_activities_ids = economic_activities
            except requests.RequestException:
                _logger.info(_("The name query service is unavailable at this moment"))

    @api.onchange('vat')
    def onchange_vat(self):
        if self.vat:
            self.get_information(self.vat)
