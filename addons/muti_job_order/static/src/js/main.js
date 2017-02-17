// Lib
function PrintElem(elem, script) {
    Popup($(elem).html(), script);
}

function Popup(data, script) {
    var mywindow = window.open();
    var style = typeof(style) == 'undefined' ? '' : style;
    mywindow.document.write
        ('<html>\
            <head>\
                <title>Barcode Printer</title>\
                ' + script + '\
            </head>\
            <body>' + data + '</body>' +
        '</html>');

    mywindow.document.close(); // necessary for IE >= 10
    mywindow.focus(); // necessary for IE >= 10

    mywindow.print();
    mywindow.close();

    return true;
}

String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{{'+i+'\\}}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[#?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
};

// CONFIG
var barcode_settings = {
    output: 'css',
    bgColor: '#FFFFFF',
    color: '#000000',
    barWidth: 1, //1
    barHeight: 50, //50
    moduleSize: 4, //4
    posX: 10, //10
    posY: 20, //20
    addQuietZone: 1 //1
};

// Barcode Template
var print_style =
    '<style type="text/css">\
        .barcode { \
            min-width: 26.90mm; \
            height: 100px; \
            vertical-align: middle;\
            display: table-cell;}\
        .product-label { \
            font-size: 10px; \
            margin-left: 10px;}\
        div.barcode :last-child { \
            margin-left: 9px;\
            width: 90px !important;\
            text-align: left !important;\
        @page {\
            width: 3in;\
            min-height: 1in;\
            margin: 0mm;\
        }\
        @media print {\
            html, body {\
                margin: 0mm;\
                width: 3in;\
                min-height: 1in;\
            }\
        }\
    </style>';

var print_barcode_img =
    '<div style="display: inline-block;"></div>\
    <div class="barcode">\
        <label class="product-label">{{0}}</label><br/>{{1}}\
    </div>';

var print_canvas =
        '<div id="barcode-canvas-container">\
            <div class="barcode-canvas">\
                <div class="barcode-images">{{0}}</div>\
            </div>\
        </div>';


var mrp_production_state = null;
var product_barcode = null;
var product_tmpl_name = null;
var get_new_barcode = false;

function insertCheckbox() {
    $('<span id="print_checkbox_container">\
        <input type="checkbox" name="auto_print_barcode" checked="checked">\
        <label for="auto_print_barcode">Print barcode upon confirmation</label>\
   </span>')
    .insertAfter($('.o_statusbar_buttons button.oe_button span:contains(Cancel Production):visible').parent());
}

$(document).ajaxComplete(function(event, request, settings) {
    // console.log(getParameterByName('view_type'), getParameterByName('model'));
    if (getParameterByName('view_type') == 'form' && getParameterByName('model') == 'mrp.production') {
        // For auto print
        if (settings.url.indexOf('call_kw/product.product/read') > -1) {
            mrp_production_state = request.responseJSON.result[0].state;
            var product_id = parseInt(request.responseJSON.result[0].product_id[0]);
            insertCheckbox();
            var params = {
                "jsonrpc":"2.0",
                "method":"call",
                "params":{
                    "model":"product.product",
                    "method": "read",
                    "args":[
                        product_id,
                        ["barcode", "product_tmpl_id"]
                    ]
                }
            };
            $.ajax({
                url: '/web/dataset/call',
                data: JSON.stringify(params),
                type: 'POST',
                contentType: "application/json",
                accepts: 'text/json',
                success: function(data) {
                    product_barcode = data.result.barcode;
                    product_tmpl_name = data.result.product_tmpl_id[1];
                    // console.log('product_barcode', product_barcode);
                }
            });

        } else if(settings.url.indexOf('call_kw/mrp.production/default_get') > -1) {
            get_new_barcode = true;
            insertCheckbox();
        } else if(settings.url.indexOf('dataset/exec_workflow') > -1) {
            if ($('input[type=checkbox][name=auto_print_barcode]').prop('checked')) {
                var settingsData = JSON.parse(settings.data);
                if (
                    settingsData.params.model == 'mrp.production' &&
                    settingsData.params.signal == 'button_confirm'
                ) {
                    if (get_new_barcode) {
                        product_barcode = $('td.oe_form_group_cell_label:contains(Product Barcode)').next()
                            .find('input').val().trim();
                        product_tmpl_name = $('td.oe_form_group_cell_label:contains(Product)').next().find('input').val();
                    }
                    if (product_barcode) {
                        var rendered_barcode = $('<span></span>').show()
                            .barcode(product_barcode, 'code128', barcode_settings).html();

                        var to_be_printed = print_barcode_img.format(product_tmpl_name, rendered_barcode);
                        to_be_printed += '<div class="clear-left"></div>';

                        var edited_print_canvas = print_canvas.format(to_be_printed);
                        PrintElem(edited_print_canvas, print_style);

                    } else {
                        alert('No defined barcode');
                    }
                    $('#print_checkbox_container').remove();
                }
            }

        }
    }
});