openerp.muti_printer = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.barcode_printer = instance.Widget.extend({
        template: "barcode_printer",
        start: function() { }
    });

    instance.web.client_actions.add(
        'muti_printer.barcode_printer', 'instance.muti_printer.barcode_printer');

};