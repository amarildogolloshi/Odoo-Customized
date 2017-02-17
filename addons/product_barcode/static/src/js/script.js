openerp.product_barcode = function(instance, local) {
    local.homepage = instance.Widget.extend({
        start: function() {
            console.log("home page loaded");
        },
    });
    instance.web.client_actions.add('barcode.printing', 'instance.product_barcode.homepage')
};