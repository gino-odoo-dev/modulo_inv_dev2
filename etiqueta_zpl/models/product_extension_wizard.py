from odoo import models, fields, _, api
import logging
import requests
import base64
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ZplExtensionWizard(models.TransientModel):
    _name = 'product.wizard'
    _description = 'Asistente de Etiquetas para Productos'

    id_codigo = fields.Many2one('product.codigo', string="Codigo", required=True)
    id_numeracion = fields.Many2one('cl.product.numeracion', string="Numeracion", required=True) 

    cantidad = fields.Integer(string="Cantidad", default=0, required=True)
    pdf_file = fields.Binary(string="PDF de Etiqueta", readonly=True)
    pdf_filename = fields.Char(string="Nombre del Archivo")

    show_cantidad = fields.Boolean(compute='_compute_visibility')
    show_id_codigo = fields.Boolean(compute='_compute_visibility')
    show_id_numeracion = fields.Boolean(compute='_compute_visibility')

    @api.depends('zpl_format')
    def _compute_visibility(self):
        for record in self:
            record.show_cantidad = record.zpl_format in ['format1', 'format3']
            record.show_id_codigo = record.zpl_format in ['format2', 'format3', 'format4']
            record.show_id_numeracion = record.zpl_format in ['format2', 'format3']
    
    zpl_format = fields.Selection(
        selection=[
            ('format1', 'Formato 01'),
            ('format2', 'Formato 02'),
            ('format3', 'Formato 03'),
            ('format4', 'Formato 04'),
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
            ^FO500,960^A0R,35,35^FDicia de entrada:^FS
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
            ^XA^MCY
            ^XZ
            """.format(numeracion=numeracion, 
                       codigo=codigo,
                       cantidad=cantidad, 
                       nombre=nombre, 
                       direccion=direccion, 
                       ciudad=ciudad, 
                       temporada=temporada, 
                       articulo=articulo, 
                       cuero=cuero, 
                       color=color
                       )
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
        elif self.zpl_format == 'format4':
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

        