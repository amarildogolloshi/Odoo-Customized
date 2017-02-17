# -*- coding: utf-8 -*-
from openerp import http
from vendor import barcode
import json, base64

class product_barcode(http.Controller):

    @http.route(
        ['/barcodes/index', '/barcodes', '/barcodes/'], auth='public')
    def index(self, **kwargs):
        return http.request.render('product_barcode.index', {
            'teachers': ["Diana Padilla", "Jody Caroll", "Lester Vaughn"],
        })

    @http.route(
        [
            '/barcode/images',
            '/barcode/images/<id>/<int:width>x<int:height>',
        ], auth='public', website=True, multilang=False
    )
    def images(self, id, width=None, height=None):

        return 'Hi there'

    def generate_barcode(self):
        record = self.read(['name'])
        bcode = barcode.get_barcode_class(self._barcode_type)
        filename = bcode(record[0]['name'], writer=barcode.writer.ImageWriter()).save('/tmp/'+record[0]['name'])
        binary_barcode = False
        with open(filename, "rb") as imageFile:
            binary_barcode = base64.b64encode(imageFile.read())


