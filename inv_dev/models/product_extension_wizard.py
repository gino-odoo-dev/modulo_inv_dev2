from odoo import models, fields, _
import logging
import requests
import base64
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class Codigo(models.Model):
    _name = 'product.codigo'
    _description = 'Código de Producto'
    name = fields.Char(string="Artículo", required=True)

class Cantidad(models.Model):
    _name = 'product.cantidad'
    _description = 'Cantidad de Producto'
    name = fields.Float(string="Cantidad", default=0.0)

class Numeracion(models.Model):
    _name = 'cl.product.numeracion'  
    _description = 'Numeracion de Productos'
    _rec_name = "numero" 

    name = fields.Char(string="Nombre")
    numero = fields.Integer(string="Numero de Talla", required=True)

class ProductExtensionWizard(models.TransientModel):
    _name = 'product.extension.wizard'
    _description = 'Asistente de Etiquetas para Productos'

    id_codigo = fields.Many2one('product.codigo', string="Código", required=True)
    id_numeracion = fields.Many2one('cl.product.numeracion', string="Numeración", required=True) 
    cantidad = fields.Integer(string="Cantidad", default=0, required=True)
    pdf_file = fields.Binary(string="PDF de Etiqueta", readonly=True)
    pdf_filename = fields.Char(string="Nombre del Archivo")
    
    zpl_format = fields.Selection(
        selection=[
            ('format1', 'Formato 1'),
            ('format2', 'Formato 2'),
            ('format3', 'Formato 3'),
        ],
        string="Formato de Etiqueta",
        default='format1',
        required=True
    )

    def generate_zpl_label(self):
        codigo = self.id_codigo.name if self.id_codigo else 'Desconocido'
        numeracion = self.id_numeracion.name if self.id_numeracion else 'Desconocido'
        cantidad = self.cantidad

        if self.zpl_format == 'format1':
            zpl = """
            ^XA         
            ^FO50,170
            ^A0N,40,40
            ^FDCantidad: {cantidad}^FS
            ^FO50,230
            ^B3N,N,100,Y,N
            ^FD>: {codigo}^FS
            ^XZ
            """.format(numeracion=numeracion, codigo=codigo, cantidad=cantidad)
        elif self.zpl_format == 'format2':
            zpl = """
            ^XA
            ^FO50,50
            ^A0N,40,40
            ^FDFormato 2: {numeracion}^FS
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
            """.format(numeracion=numeracion, codigo=codigo, cantidad=cantidad)
        elif self.zpl_format == 'format3':
            zpl = """
            ^XA
            ^FO50,50
            ^A0N,40,40
            ^FDFormato 3: {numeracion}^FS
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
            """.format(numeracion=numeracion, codigo=codigo, cantidad=cantidad)
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
            pdf_filename = f"Etiqueta_{self.id_codigo.name}_{self.id_numeracion.name}.pdf"

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

        