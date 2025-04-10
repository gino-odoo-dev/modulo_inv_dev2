from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging
import requests
import base64

_logger = logging.getLogger(__name__)

class Codigo(models.Model):
    _name = 'product.codigo'
    _description = 'Código de Producto'
    name = fields.Char(string="Artículo", required=True)

class Numeracion(models.Model):
    _name = 'cl.product.numeracion'  
    _description = 'Numeración de Productos'
    _rec_name = "numero" 

    name = fields.Char(string="Nombre")
    numero = fields.Integer(string="Número de Talla", required=True)

class ProductExtensionWizard(models.TransientModel):
    _name = 'product.wizard'
    _description = 'impresion de Etiquetas para Productos'

    codigo = fields.Many2one('product.codigo', string="Código")
    numeracion = fields.Many2one('cl.product.numeracion', string="Numeración")
    cantidad = fields.Integer(string="Cantidad", default=0)
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

    @api.constrains('zpl_format', 'codigo', 'numeracion')
    def _check_required_fields(self):
        for record in self:
            if record.zpl_format in ['format1', 'format2'] and not record.codigo:
                raise ValidationError(_("El campo Codigo es requerido para el formato seleccionado"))
            if record.zpl_format in ['format2', 'format3'] and not record.numeracion:
                raise ValidationError(_("El campo Numeracion es requerido para el formato seleccionado"))

    def generate_zpl_label(self):
        self.ensure_one()
        
        # Validación de campos requeridos
        if not self._context.get('bypass_validation'):
            self._check_required_fields()

        codigo = self.codigo.name if self.codigo else ''
        numeracion = self.numeracion.name if self.numeracion else ''
        cantidad = self.cantidad

        format_templates = {
            'format1': """
                ^XA         
                ^FO50,170
                ^A0N,40,40
                ^FDCantidad: {cantidad}^FS
                ^FO50,230
                ^B3N,N,100,Y,N
                ^FD>: {codigo}^FS
                ^XZ
            """,
            'format2': """
                ^XA
                ^BY2,3,,
                ^PRD
                ^CI10
                ^LH0,0
                ^FO35,35^GB760,1170,5^FS
                ^FO45,45^GB740,1150,5^FS
                ^FO720,60^A0R,40,40^FDRemite :^FS
                ^FO720,850^A0R,40,40^FDFecha :
                07/03/2025
                ^FO550,60^A0R,50,50^FDNombre     :^FS
                ^FO500,60^A0R,50,50^FDDireccion :^FS
                ^FO450,60^A0R,50,50^FDCiudad      :^FS
                ^FO400,60^A0R,50,50^FDTemporada:^FS
                ^FO350,60^A0R,50,50^FDArticulo     :^FS
                ^FO305,60^A0R,40,40^FDCuero    :^FS
                ^FO255,60^A0R,40,40^FDColor :^FS
                ^FO110,60^A0R,45,45^FDPares :^FS
                ^FO215,60^A0R,40,40^FDNota de Venta:^FS
                ^FO215,500^A0R,40,40^FDO. Compra : ^FS
                ^FO160,60^A0R,50,50^FDO. Fabricacion:^FS
                ^FO500,960^A0R,35,35^FDguia de entrada:^FS
                ^FO720,320^A0R,50,50^FDFABRICA DE CALZADOS GINO SA^FS
                ^FO670,320^A0R,50,50^FDMIRAFLORES #8860 - RENCA^FS
                ^FO620,320^A0R,50,50^FDSANTIAGO - CHILE^FS
                ^FO550,320^A0R,50,50^FDFABRICA DE CALZADOS GINO SA ^FS
                ^FO500,320^A0R,50,50^FDAV MIRAFLORES 8860 RENCA^FS
                ^FO450,320^A0R,50,50^FDNUNOA^FS
                ^FO400,420^A0R,50,50^FDINV2025^FS
                ^FO350,320^A0R,50,50^FDL505AK3AF5CLK05 MING^FS
                ^FO305,320^A0R,40,40^FDKENT.^FS
                ^FO255,320^A0R,40,40^FDTANINO.^FS
                ^FO110,210^A0R,45,45^FD3^FS
                ^FO110,300^A0R,40,23^FD 36E 37E 38E^FS
                ^FO075,290^A0R,40,32^FD 1 1 1^FS
                ^FO215,320^A0R,40,40^FDOD30601^FS
                ^FO215,720^A0R,40,40^FD^FS
                ^FO160,370^A0R,50,50^FD642359 Suc. 505^FS
                ^FO400,980^A0R,80,50^FD00642359^FS
                ^FO70,950^B3N,N,100,Y^FD00642359^FS
                ^PQ1
                ^xz
                ^XA
                ^MCY
                ^XZ
            """,
            'format3': """
                ^XA
                ^FX 
                ^CF0,50
                ^FX
                ^FO90,40^FD
                BLUE                
                ^FS
                ^FX
                ^LRY
                ^FO290,20^GB290,90,90^FS
                ^CF0,90 ^FX
                ^FO340,30^FD
                179H                               
                ^FS
                ^FX 
                ^BY2,3,,^FO110,123^BCN,80,N,N,N^FD
                179HASUC3600A0035E       
                ^FS
                ^FX SKU.
                ^FO160,210^A0N,30,40^FD
                179HASUC3600A0035E      
                ^FS
                ^XZ
                ^XA
                ^FX 
                ^CF0,50
                ^FX 
                ^FO90,40^FD
                BLUE
                ^FS
                ^FX
                ^LRY
                ^FO290,20^GB290,90,90^FS
                ^CF0,90 ^FX
                ^FO340,30^FD
                179H
                ^FS
                ^FX 
                ^BY2,3,,^FO110,123^BCN,80,N,N,N^FD
                179HASUC3600A0035E
                ^FS
                ^FX SKU.
                ^FO160,210^A0N,30,40^FD
                179HASUC3600A0035E
                ^FS
                ^XZ
            """
        }

        zpl = format_templates.get(self.zpl_format, "").strip()
        return zpl.format(numeracion=numeracion, codigo=codigo, cantidad=cantidad)

    def generate_pdf_from_zpl(self):
        self.ensure_one()
        
        try:
            zpl = self.generate_zpl_label()
            if not zpl:
                raise UserError(_("Formato de etiqueta no válido"))

            url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
            headers = {'Accept': 'application/pdf'}
            files = {'file': zpl.encode('utf-8')}

            response = requests.post(url, headers=headers, files=files, stream=True, timeout=10)

            if response.status_code == 200:
                pdf_content = base64.b64encode(response.content)
                filename = f"Etiqueta_{self.codigo.name if self.codigo else ''}_{self.numeracion.name if self.numeracion else ''}.pdf"
                
                self.write({
                    'pdf_file': pdf_content,
                    'pdf_filename': filename
                })

                return {
                    'type': 'ir.actions.act_url',
                    'url': f"/web/content?model=product.wizard&id={self.id}&field=pdf_file&filename_field=pdf_filename&download=true",
                    'target': 'self',
                }
            else:
                raise UserError(_("Error al generar el PDF: %s") % response.text)
        except requests.exceptions.RequestException as e:
            raise UserError(_("Error de conexión: %s") % str(e))