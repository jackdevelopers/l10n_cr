/****************************************************************************
 *
 *    OpenERP, Open Source Management Solution
 *    Copyright (C) 2016 Aselcis Consulting (http://www.aselcis.com). All Rights Reserved
 *    Copyright (C) 2016 David Gómez Quilón (http://www.aselcis.com). All Rights Reserved
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU Affero General Public License as
 *    published by the Free Software Foundation, either version 3 of the
 *    License, or (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU Affero General Public License for more details.
 *
 *    You should have received a copy of the GNU Affero General Public License
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 ******************************************************************************/

odoo.define('cr_electronic_invoice_pos.models', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var models = require('point_of_sale.models');
    var _sequence_next = function(seq){
        var idict = {
            'year': moment().format('YYYY'),
            'month': moment().format('MM'),
            'day': moment().format('DD'),
            'y': moment().format('YY'),
            'h12': moment().format('hh')
        };
        var format = function(s, dict){
            s = s || '';
            $.each(dict, function(k, v){
                s = s.replace('%(' + k + ')s', v);
            });
            return s;
        };
        function pad(n, width, z) {
            z = z || '0';
            n = n + '';
            if (n.length < width) {
                n = new Array(width - n.length + 1).join(z) + n;
            }
            return n;
        }
        var num = seq.number_next_actual;
        var prefix = format(seq.prefix, idict);
        var suffix = format(seq.suffix, idict);
        seq.number_next_actual += seq.number_increment;        
        return prefix + pad(num, seq.padding) + suffix;
    };

    var PosModelParent = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function(){
            var self = this;
            console.log(self.models);
            // Load POS sequence object
            self.models.push({
                model: 'ir.sequence',
                fields: [],
                ids:    function(self){ 
                    return [
                        self.config.FE_sequence_id[0],
                        self.config.TE_sequence_id[0],
                        self.config.NC_sequence_id[0]
                    ]; 
                },
                loaded: function(self, sequence){
                    self.FE_sequence = sequence[0];
                    self.TE_sequence = sequence[1];
                    self.NC_sequence = sequence[2];
                },
            });
            return PosModelParent.load_server_data.call(this, arguments);
        },
        push_single_order: function (order, opts) {
            opts = opts || {};
            const self = this;
            console.log('Push single order');
            console.log(order);
            console.log(self);
            if (order.get_client() && order.get_client().vat && order.total_paid > 0 ) {
                order.set_sequence(self.FE_sequence.number_next_actual);
                order.set_number_electronic(_sequence_next(self.FE_sequence));
                order.set_tipo_documento('FE');
            } else if (order.total_paid > 0) {
                order.set_sequence(self.TE_sequence.number_next_actual);
                order.set_number_electronic(_sequence_next(self.TE_sequence));
                order.set_tipo_documento('TE');
            } else{
                order.set_sequence(self.NC_sequence.number_next_actual);
                order.set_number_electronic(_sequence_next(self.NC_sequence));
                order.set_tipo_documento('NC');
            }
            const order_id = self.db.add_order(order.export_as_JSON());
    
            return new Promise((resolve, reject) => {
                self.flush_mutex.exec(async () => {
                    const order = self.db.get_order(order_id);
                    try {
                        resolve(await self._flush_orders([order], opts));
                    } catch (error) {
                        reject(error);
                    }
                });
            });
        }
    });

    var _super = models.Order;
    models.Order = models.Order.extend({
         /* initialize: function
         * Declare
         * sequence: Stores the last electronic sequence
         * number_electronic: Stores the last number electronic
         * tipo_documento: Stores the doc type
         */
         initialize: function(attr,options){

            _super.prototype.initialize.call(this, attr, options);

            // Initialize the variables
            this.sequence;
            this.number_electronic;
            this.tipo_documento;
        },
        export_for_printing: function(){
            var result = _super.prototype.export_for_printing.call(this, arguments);
            var sequence = this.get_sequence();
            var number_electronic = this.get_number_electronic();
            var tipo_documento = this.get_tipo_documento();

            if (sequence && number_electronic && tipo_documento) {
                result.sequence = sequence;
                result.number_electronic = number_electronic;
                result.tipo_documento = tipo_documento;
            }

            return result;
        },
        export_as_JSON: function () {
            var json = _super.prototype.export_as_JSON.call(this, arguments);
            console.log(json);
            console.log(this.number_electronic);
            console.log(this.get_number_electronic());
            if (this.sequence && this.number_electronic && this.tipo_documento) {
                json.sequence = this.get_sequence();
                json.number_electronic = this.get_number_electronic();
                json.tipo_documento = this.get_tipo_documento();
            }

            return json;
        },
        set_number_electronic: function (number_electronic) {
            this.number_electronic = number_electronic;
        },
        get_number_electronic: function () {
            return this.number_electronic;
        },
        set_sequence: function (sequence) {
            this.sequence = sequence;
        },
        get_sequence: function () {
            return this.sequence;
        },
        set_tipo_documento: function (tipo_documento) {
            this.tipo_documento = tipo_documento;
        },
        get_tipo_documento: function () {
            return this.tipo_documento;
        }
    });

});
