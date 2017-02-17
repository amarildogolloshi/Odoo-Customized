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

// MODEL
var Products = Backbone.Collection.extend({
    url: '/web/dataset/search_read'
});

// TEMPLATES
var mrp_production_template =
    '<table class="oe_list_content">\
        <thead>\
            <tr class="oe_list_header_columns">\
                <th><br /><input id="select-products" name="radiogroup" type="checkbox" {{0}}/></th>\
                <th data-id="name" class="oe_list_header_char oe_sortable"><div>Name</div></th>\
                <th data-id="type" class="oe_list_header_many2one oe_sortable"><div>Vehicle type</div></th>\
                <th data-id="barcode" class="oe_list_header_float oe_sortable"><div>Barcode</div></th>\
            </tr>\
        </thead>\
        <tfoot>\
            <tr>\
                <td></td>\
                <td class="oe_list_footer oe_number"></td>\
                <td class="oe_list_footer oe_number"></td>\
                <td class="oe_list_footer oe_number"></td>\
            </tr>\
        </tfoot>\
        <tbody>{{1}}</tbody>\
    </table>\
    ';

var print_barcode_img =
    '<div style="display: inline-block;"></div>\
    <div class="barcode">\
        <label class="product-label">{{0}}</label><br/>{{1}}\
    </div>';

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

// VIEW
var DataFilter = Backbone.View.extend({
    el: '#barcode-product-container',
    render: function() {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!

        var yyyy = today.getFullYear();
        if(dd < 10){
            dd='0'+dd
        }
        if(mm < 10){
            mm='0'+mm
        }
        today = yyyy+'-'+mm+'-'+dd;
        this.$el.find('input[name=search_key]').val('');
        this.$el.find('input[name=date_from]').val(today);
        this.$el.find('input[name=date_to]').val(today);
    },
    events: {
        'submit #data-filter': 'fetchProducts',
        'change #select-products': 'selectProducts',
        'change .select-product': 'selectProduct',
        'click #print-barcode': 'printBarcodes',
        'click #current_page': 'togglePageLimit',
        'click select[name=page_limit]': 'toggleCurrentPage',
        'click a[data-pager-action=previous]': 'previousPage',
        'click a[data-pager-action=next]': 'nextPage'
    },
    fetchProducts: function(e) {
        var that = this;
        var filterArgs = $(e.currentTarget).serializeObject();
        var page_limit = parseInt(filterArgs.page_limit);
        var current_page = 0;
        var page_offset = 0;
        if (page_limit) {
            current_page = parseInt($('select[name=page_limit]').data('current_page'));
            page_offset = (current_page * page_limit) - page_limit;
        }
        var domain = [];
        if (filterArgs.search_key) {
            domain.push(["name", 'ilike', filterArgs.search_key]);
        }
        if (filterArgs.date_from) {
            domain.push(["write_date", ">=", filterArgs.date_from + ' 00:00:00']);
        }
        if (filterArgs.date_to) {
            domain.push(["write_date", "<=", filterArgs.date_to + ' 23:59:59']);
        }
        if (typeof(filterArgs.with_barcode) != 'undefined' && filterArgs.with_barcode == 'on') {
            domain.push(["barcode", "!=", false]);
        }
        var params = {
            "jsonrpc":"2.0",
            "method":"call",
            "params":{
                "model":"product.product",
                "fields":['product_tmpl_id', 'barcode', 'type'],
                "domain": domain,
                "context":{
                    "lang":"en_US",
                    "tz":"Europe/Brussels",
                    "uid":1,
                    "params":{
                        "action":331
                    },
                    "bin_size":true
                },
                "offset":page_offset,
                "limit":page_limit,
                "sort":"name asc"
            }
        };

        var products = new Products();
        products.fetch({
            data: JSON.stringify(params),
            type: 'POST',
            contentType: "application/json",
            accepts: 'text/json',
            success: function(data) {
                if (typeof(data.models[0].attributes.result) == 'undefined') {
                    alert('Warning: Please report the following\n* ' + data.models[0].attributes.error.message);
                    return false;
                }

                var records = data.models[0].attributes.result.records;
                var total_records = data.models[0].attributes.result.length;
                var has_records = records.length > 0;
                var productList = '';
                var is_check_all = '';
                if (has_records) {
                    _.each(records, function (product) {
                        productList +=
                            '<tr data-id="106" class="" style="">\
                                <td data-value="name" title="" class="oe_list_field_cell oe_list_field_char">\
                                    <input class="select-product" checked="checked" name="radiogroup" type="checkbox" data-product=\'' + JSON.stringify(product) + '\'>\
                                </td>\
                                <td data-value="name" title="" class="oe_list_field_cell oe_list_field_char">' + product.product_tmpl_id[1] + '</td>\
                                <td data-value="type" title="" class="oe_list_field_cell oe_list_field_char">' + product.type + '</td>\
                                <td data-value="barcode" class="oe_list_field_cell oe_list_field_float oe_number">' +
                                    ((!product.barcode) ? '<i>none</i>' : product.barcode)
                                + '</td>\
                            </tr>';
                    });

                    is_check_all = 'checked="checked"'
                } else {
                    productList += '<tr><td colspan="4" style="text-align: center;">No products</td></tr>';
                }
                $('#print-barcode').attr('disabled', !(has_records));
                var product_template = mrp_production_template.format(is_check_all, productList);
                that.$el.find('#mrp-production-list').html(product_template);

                // Pagination
                if (isNaN(page_limit)) {
                    $('#current_page').html((page_offset + 1) + ' - ' + total_records);
                } else {
                    var page_item_count = page_offset + page_limit;
                    if (page_item_count > total_records) {
                        page_item_count = total_records;
                    }
                    if (page_item_count) {
                        $('#current_page').html((page_offset + 1) + ' - ' + page_item_count + ' / ' + total_records);
                    }
                }

                $('select[name=page_limit]').data('length', total_records);
            }
        });

        return false;
    },
    selectProducts: function(e) {
        $('table.oe_list_content input.select-product').prop('checked', $('#select-products').is(':checked'));
    },
    selectProduct: function(e) {
        $('#select-products').prop(
            'checked', (
                $('table.oe_list_content').find('input.select-product:checked').length ==
                $('table.oe_list_content').find('input.select-product').length
            )
        );
    },
    printBarcodes: function(e) {
        var to_be_printed = '';
        $('table.oe_list_content').find('input.select-product:checked').each(function() {
            if ($(this).data('product').barcode) {

                //barcode_settings
                var rendered_barcode = $('<span></span>').show().barcode(
                    $(this).data('product').barcode,
                    'code128',
                    barcode_settings
                ).html();
                //

                to_be_printed += print_barcode_img.format($(this).data('product').product_tmpl_id[1], rendered_barcode);
            }
        });
        if (to_be_printed) {
            to_be_printed += '<div class="clear-left"></div>';
            $('.barcode-images').html(to_be_printed);
            PrintElem($('#barcode-canvas-container').html(), print_style);
        } else {
            alert('No valid barcode found.');
        }
    },
    togglePageLimit: function(e) {
        $('select[name=page_limit]').toggle();
        $('#current_page').toggle();
    },
    toggleCurrentPage: function(e) {
        $('select[name=page_limit]').toggle();
        $('select[name=page_limit]').data('current_page_storage', '1');
        $('#current_page').toggle();
        $('#data-filter').trigger('submit');
    },
    previousPage: function(e) {
        var page_limit_selector = 'select[name=page_limit]';
        if (isNaN($(page_limit_selector).val())) {
            return false;
        }
        var current_page = parseInt($(page_limit_selector).data('current_page_storage'));
        if (current_page > 1) {
            var previous_page = current_page - 1;
            $(page_limit_selector).data('current_page', previous_page);
            $(page_limit_selector).data('current_page_storage', previous_page);
            if (previous_page == 1) {
                $(e).prop('disabled', 'disabled');
            }
            $('#data-filter').trigger('submit');
            $(page_limit_selector).data('current_page', 1);
        }
    },
    nextPage: function(e) {
        var page_limit_selector = 'select[name=page_limit]';
        if (isNaN($(page_limit_selector).val())) {
            return false;
        }
        var current_page = parseInt($(page_limit_selector).data('current_page_storage'));
        var data_length = parseInt($(page_limit_selector).data('length'));
        var next_page = current_page + 1;
        var page_limit = parseInt($(page_limit_selector).val());
        if (((next_page * page_limit) - page_limit) > data_length) {
            next_page = 1;
            if (next_page == current_page) return false;
        }
        $(page_limit_selector).data('current_page', next_page);
        $(page_limit_selector).data('current_page_storage', next_page);
        $('#data-filter').trigger('submit');
        $(page_limit_selector).data('current_page', 1);

    }
});

__init = function() {
    $('#print-barcode').attr('disabled', true);
    var dataFilter  = new DataFilter();
    dataFilter.render();
};

__init();