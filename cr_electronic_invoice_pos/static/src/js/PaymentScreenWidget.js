odoo.define('cr_electronic_invoice_pos.PaymentScreenWidget', function(require){
	'use strict';

	const PaymentScreen = require('point_of_sale.PaymentScreen');
	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	var models = require('point_of_sale.models');
	const { float_is_zero } = require('web.utils');
	const { Component } = owl;

	const PaymentScreenWidget = (PaymentScreen) =>
		class extends PaymentScreen {
			constructor() {
				super(...arguments);
			}
		async validateOrder(isForceValidate) {
            let currentOrder = this.env.pos.get_order();
            let client = currentOrder.get_client();
            const change = currentOrder.get_change();
            if(currentOrder.get_tipo_documento()){
                if(currentOrder.get_tipo_documento() == "FE"){
                    if(!client){
                        return this.showPopup('ErrorPopup',{
                        'title': this.env._t('Cliente'),
                        'body': this.env._t('El cliente es requerido para una factura electronica'),
                        });
                    }
                    if(!client.identification_id || client.vat == ""){
                        return this.showPopup('ErrorPopup',{
                        'title': this.env._t('Identificacion invalida'),
                        'body': this.env._t('El cliente no posee identificacion para facturar'),
                        });
                    }
                    if(client.identification_id[0]==1){
                        if(client.vat.length != 9){
                            return this.showPopup('ErrorPopup',{
                            'title': this.env._t('Identificacion invalida'),
                            'body': this.env._t('La identificacion no es valida'),
                            });
                        }
                    }else{
                        if(client.identification_id[0]==2){
                            if(client.vat.length != 13){
                                return this.showPopup('ErrorPopup',{
                                'title': this.env._t('Identificacion invalida'),
                                'body': this.env._t('La identificacion no es valida'),
                                });
                            }
                        }else{
                            if(client.identification_id[0]==3){
                                if(client.vat.length < 10){
                                    return this.showPopup('ErrorPopup',{
                                    'title': this.env._t('Identificacion invalida'),
                                    'body': this.env._t('La identificacion no es valida'),
                                    });
                                }
                            }
                        }
                    }
                    if(!client.email){
                        return this.showPopup('ErrorPopup',{
                        'title': this.env._t('Correo invalido'),
                        'body': this.env._t('El cliente no posee un correo para facturar'),
                        });
                    }
                }
                await super.validateOrder(isForceValidate);
                }else{
                    return this.showPopup('ErrorPopup',{
                    'title': this.env._t('Seleccione tipo documento'),
                            'body': this.env._t('Debe de seleccionar un tipo de documento'),
                        });
                    }
        }

		};
	Registries.Component.extend(PaymentScreen, PaymentScreenWidget);
	return PaymentScreen;
});