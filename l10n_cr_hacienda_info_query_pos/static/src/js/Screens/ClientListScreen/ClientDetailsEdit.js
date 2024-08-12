odoo.define('l10n_cr_hacienda_info_query_pos.ClientDetailsEdit', function (require) {
    'use strict';

    const ClientDetailsEdit = require("point_of_sale.ClientDetailsEdit");
    const Registries = require("point_of_sale.Registries");

    const PosClientDetailsEdit = (ClientDetailsEdit) =>
        class extends ClientDetailsEdit {
            constructor() {
                super(...arguments);
            }

            mounted() {
                super.mounted();
                this.initVatField();
            }

            initVatField() {
                let vatInput = document.querySelector('input[name="vat"]');
                let identificationSelect = document.getElementsByName("identification_id")[0];
                if (identificationSelect && vatInput) {
                    this.toggleVatField(identificationSelect.value);
                    identificationSelect.addEventListener("change", (e) => {
                        this.toggleVatField(e.target.value);
                    });
                }
            }

            toggleVatField(identificationIdValue) {
                let vatInput = document.querySelector('input[name="vat"]');
                if (vatInput) {
                    vatInput.disabled = !identificationIdValue;
                    if (!identificationIdValue) {
                        vatInput.value = '';
                    }
                }
            }

            onchange_county(event) {
                let district = this.env.pos.districts;
                let canton = document.getElementsByName("county_id")[0];
                let str_html = "";
                for (let i = 0; i < district.length; i++) {
                    if (district[i].county_id[0] == canton.options[canton.selectedIndex].value) {
                        str_html += "<option value='" + district[i]['id'] + "'>" + district[i]['name'] + "</option>";
                    }
                }
                let select = document.getElementsByName("district_id")[0];
                select.innerHTML = str_html;
                this.changes[event.target.name] = event.target.value;
            }

            onchange_state(event) {
                let district_id = document.getElementsByName("district_id")[0];
                let str_html = "";
                district_id.innerHTML = str_html;
                let county = this.env.pos.counties;
                let provincia = document.getElementsByName("state_id")[0];
                for (let i = 0; i < county.length; i++) {
                    if (county[i].state_id[0] == provincia.options[provincia.selectedIndex].value) {
                        str_html += "<option value='" + county[i]['id'] + "'>" + county[i]['name'] + "</option>";
                    }
                }
                let select = document.getElementsByName("county_id")[0];
                select.innerHTML = str_html;
                this.changes[event.target.name] = event.target.value;
            }

            onchange_country(event) {
                let state_id = document.getElementsByName("state_id")[0];
                let district_id = document.getElementsByName("district_id")[0];
                let county_id = document.getElementsByName("county_id")[0];
                // Reseteamos los otros combobox para que no se genere confusión
                state_id.innerHTML = "";
                county_id.innerHTML = "";
                district_id.innerHTML = "";
                let states = this.env.pos.states;
                let pais = document.getElementsByName("country_id")[0];
                let str_html = "";
                for (let i = 0; i < states.length; i++) {
                    if (pais.options[pais.selectedIndex].value == 50) {
                        if ((states[i].country_id[0] == pais.options[pais.selectedIndex].value) && !isNaN(states[i]['code'])) {
                            str_html += "<option value='" + states[i]['id'] + "'>" + states[i]['name'] + "</option>";
                        }
                    }
                    else {
                        if ((states[i].country_id[0] == pais.options[pais.selectedIndex].value)) {
                            str_html += "<option value='" + states[i]['id'] + "'>" + states[i]['name'] + "</option>";
                        }
                    }
                }
                let select = document.getElementsByName("state_id")[0];
                select.innerHTML = str_html;
                this.changes[event.target.name] = event.target.value;
            }
            obtener_nombre(event) {
                let vat = this.changes.vat;
                let partner_found = false;
                for (let partner in this.env.pos.db.partner_by_id) {
                    if (this.env.pos.db.partner_by_id[partner].vat === vat) {
                        partner_found = true;
                        this.showPopup('ErrorPopup', {
                            'title': this.env._t('Cliente ya registrado'),
                            'body': this.env._t('Ya se encuentra un cliente con cedula: ' + vat),
                        });
                        setTimeout(() => {
                            let vatInput = document.querySelector('input[name="vat"]');
                            if (vatInput) {
                                vatInput.value = '';
                            }
                        }, 0);
                        break;
                    }
                }
                if (!partner_found) {
                    let host = "https://api.hacienda.go.cr/fe/ae?"
                    let endpoint = host + "identificacion=" + vat
                    fetch(endpoint)
                        .then(response => {
                            if (response.status === 404) {
                                console.log('The request returned a 404 status code.');
                            } else {
                                response.json().then(result => {
                                    let vatInput = document.querySelector('input[name="name"]');
                                    vatInput.value = result['nombre'];
                                    this.changes[event.target.name] = event.target.value;
                                    this.changes['name'] = result['nombre'];
                                    // Check if no option is selected in identification_id and set it to option number 1
                                    let identificationSelect = document.getElementsByName("identification_id")[0];
                                    if (identificationSelect && !identificationSelect.value) {
                                        this.changes['identification_id'] = 1;
                                        identificationSelect.value = 1;
                                    }
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                        });
                }
            }

            saveChanges() {
                const processedChanges = {};
                for (const [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        processedChanges[key] = value;
                    }
                }
                this.props.partner.country_id = processedChanges.country_id
                this.props.partner.state_id = processedChanges.state_id;
                this.props.partner.county_id = processedChanges.county_id;
                this.props.partner.district_id = processedChanges.district_id;
                this.props.partner.identification_id = processedChanges.identification_id;
                this.props.partner.vat = processedChanges.vat;
                super.saveChanges();
            }

            captureChange(event) {
                var vat = document.getElementsByName("vat");
                vat.forEach(element => {
                    element.addEventListener("input", (e) => {
                        this.changes.vat = e.target.value;
                        this.obtener_nombre(e);
                    });
                });
                super.captureChange(event);
            }

        };
    Registries.Component.extend(ClientDetailsEdit, PosClientDetailsEdit);
    return ClientDetailsEdit;
});
