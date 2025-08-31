from datetime import datetime
import json
import requests

from odoo import http, _
from odoo.http import request, logging
_logger = logging.getLogger(__name__)


class ActualizarPosApi(http.Controller):
    # https://api.thunder.com.ve/control_rig/84:F3:EB:22:6E:D9
    @http.route(['/cedula/<vat>', ], type='http', auth="user", website=True)
    def index(self, vat):
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
                # Respuesta de la API
                if response.status_code in (200, 202) and len(response._content) > 0:
                    content = json.loads(str(response._content, 'utf-8'))

                    if 'nombre' in content:
                        identification_id = ''
                        res_partner = http.request.env['res.partner']

                        if 'activity_id' in res_partner._fields:
                            actividades = content.get('actividades')
                            act = []
                            for actividad in actividades:
                                activity = http.request.env['economic.activity'].sudo().search([(
                                    'code', '=', actividad.get('codigo')),
                                    ('active', 'in', [False, True])])
                                acti = {'id': activity.id, 'name': activity.name}
                                act.insert(len(act), acti)

                        if 'identification_id' in res_partner._fields:

                            if 'tipoIdentificacion' in content:
                                clasificacion = content.get('tipoIdentificacion')
                                # Cedula Fisica
                                type_identification_id = request.env['identification.type'].search([('code',
                                                                                                '=',
                                                                                                clasificacion)],
                                                                                              limit=1).id
                        if content.get('nombre') is not None:
                            name = content.get('nombre')
                            if 'activity_id' in res_partner._fields:
                                respose = {"name": str(name),
                                           "type_identification_id": str(type_identification_id),
                                           "activity": act}
                            else:
                                respose = {"nombre": str(name)}
                        return '%s' % str(respose).replace("'", "\"")
            except requests.RequestException:
                _logger.info(_("The name query service is unavailable at this moment"))
