from odoo import models, fields, api, _
import logging
import requests
import base64
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Codigo(models.Model):
    _name = 'product.codigo'
    _description = 'Código'
    name = fields.Char(string="Artículo")


class Cantidad(models.Model):
    _name = 'product.cantidad'
    _description = 'Cantidad'
    name = fields.Float(string="Cantidad", default=0.0)


class Numero(models.Model):
    _name = 'cl.product.tallas'
    _description = 'Tallas'
    name = fields.Char(string="Nro. Zapato")
    company_id = fields.Many2one('res.company', string="Compañía")


class ProductExtensionWizard(models.TransientModel):
    _name = 'product.extension.wizard'
    _description = 'Product Extension Wizard'

    id_codigo = fields.Many2one('product.codigo', string="Código", required=True)
    id_numero = fields.Many2one('cl.product.tallas', string="Tallas", required=True)
    cantidad = fields.Integer(string="Cantidad", default=0, required=True)
    pdf_file = fields.Binary(string="Etiqueta en PDF", readonly=True)
    pdf_filename = fields.Char(string="Nombre del Archivo")
    
    zpl_format = fields.Selection([
        ('format1', 'Formato 1'),
        ('format2', 'Formato 2'),
        ('format3', 'Formato 3'),
    ], string="Formato Etiqueta", default='format1', required=True)

    def generate_zpl_label(self):
        codigo = self.id_codigo.name if self.id_codigo else 'Desconocido'
        numero = self.id_numero.name if self.id_numero else 'Desconocido'
        cantidad = self.cantidad

        if self.zpl_format == 'format1':
            zpl = """
            ^XA
            ^FO50,50
            ^A0N,40,40
            ^FDNumero: {numero}^FS
            ^FO50,110
            ^A0N,40,40
            ^FDCodigo: {codigo}^FS
            ^FO50,170
            ^A0N,40,40
            ^FDCantidad: {cantidad}^FS
            ^FO50,230
            ^B3N,N,100,Y,N
            ^FD>: {codigo}^FS
            ^XZ
            """.format(numero=numero, codigo=codigo, cantidad=cantidad)
        elif self.zpl_format == 'format2':
            zpl = """
            ^XA
            ^FO50,50
            ^A0N,40,40
            ^FDFormato 2: {numero}^FS
            ^FO50,110
            ^A0N,40,40
            ^FDCodigo: {codigo}^FS
            ^FO50,170
            ^A0N,40,40
            ^FDCantidad: {cantidad}^FS
            ^FO50,230
            ^B3N,N,100,Y,N
            ^FD>: {codigo}^FS
            ^XZ
            """.format(numero=numero, codigo=codigo, cantidad=cantidad)
        elif self.zpl_format == 'format3':
            zpl = """
            ^XA
            ^FO50,50
            ^A0N,40,40
            ^FDFormato 3: {numero}^FS
            ^FO50,110
            ^A0N,40,40
            ^FDCodigo: {codigo}^FS
            ^FO50,170
            ^A0N,40,40
            ^FDCantidad: {cantidad}^FS
            ^FO50,230
            ^B3N,N,100,Y,N
            ^FD>: {codigo}^FS
            ^XZ
            """.format(numero=numero, codigo=codigo, cantidad=cantidad)
        else:
            zpl = ""

        return zpl.strip()

    def generate_pdf_from_zpl(self):
        zpl = self.generate_zpl_label()

        url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
        headers = {'Accept': 'application/pdf'}
        files = {'file': zpl.encode('utf-8')}

        response = requests.post(url, headers=headers, files=files, stream=True)

        if response.status_code == 200:
            pdf_content = base64.b64encode(response.content)
            pdf_filename = f"Etiqueta_{self.id_codigo.name}_{self.id_numero.name}.pdf"

            self.write({
                'pdf_file': pdf_content,
                'pdf_filename': pdf_filename
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f"/web/content?model=product.extension.wizard&id={self.id}&field=pdf_file&filename_field=pdf_filename&download=true",
                'target': 'self',
            }
        else:
            raise UserError(_("Error al generar el PDF: %s") % response.text)
        