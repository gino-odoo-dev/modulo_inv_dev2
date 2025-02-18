from odoo import models, fields, api, _
import os 
import logging 
import requests
import shutil
import base64
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__) 

class Codigo(models.Model):
    _name = 'product.codigo'  
    _description = 'Codigo'  
    name = fields.Char(string="Articulo")


class Cantidad(models.Model):    
    _name = 'product.cantidad' 
    _description = 'Cantidad' 
    name = fields.Float(string="Cantidad", default=0.0)  


class Numero(models.Model):
    _name = 'cl.product.tallas'  
    _description = 'Tallas'   
    name = fields.Char(string="Nro. Zapato")
    company_id = fields.Many2one('res.company', string="Company") 


class ProductExtensionWizard(models.TransientModel):
    _name = 'product.extension.wizard'
    _description = 'Product Extension Wizard'

    id_codigo = fields.Many2one('product.codigo', string="Codigo", required=True)
    id_numero = fields.Many2one('cl.product.tallas', string="Tallas", required=True)
    cantidad = fields.Integer(string="Cantidad", default=0, required=True)
    zpl_content = fields.Text(string="ZPL Content", readonly=True)
    pdf_file = fields.Binary(string="Etiqueta en PDF", readonly=True)
    pdf_filename = fields.Char(string="Nombre del Archivo")

    @api.model
    def generate_zpl_label(self, vals):
        codigo_record = self.env['product.codigo'].browse(vals.get('id_codigo'))
        numero_record = self.env['cl.product.tallas'].browse(vals.get('id_numero'))

        codigo = codigo_record.name if codigo_record else 'Desconocido'
        numero = numero_record.name if numero_record else 'Desconocido'
        cantidad = vals.get('cantidad', 0)

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

        return zpl.strip()

    def create_and_generate_zpl(self):
        vals = {
            'id_codigo': self.id_codigo.id if self.id_codigo else '',
            'id_numero': self.id_numero.id if self.id_numero else '',
            'cantidad': self.cantidad
        }

        zpl = self.generate_zpl_label(vals)

        wizard = self.create({
            'id_codigo': self.id_codigo.id,
            'id_numero': self.id_numero.id,
            'cantidad': self.cantidad,
            'zpl_content': zpl
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.extension.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
        }

    def generate_pdf_from_zpl(self):
        if not self.zpl_content:
            raise UserError(_("No hay contenido para generar etiqueta"))

        url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
        headers = {'Accept': 'application/pdf'}
        files = {'file': self.zpl_content.encode('utf-8')}

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