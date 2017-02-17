$.fn.serializeObject = function() {
  var o = {};
  var a = this.serializeArray();
  $.each(a, function() {
      if (o[this.name] !== undefined) {
          if (!o[this.name].push) {
              o[this.name] = [o[this.name]];
          }
          o[this.name].push(this.value || '');
      } else {
          o[this.name] = this.value || '';
      }
  });
  return o;
};

String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{{'+i+'\\}}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};


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