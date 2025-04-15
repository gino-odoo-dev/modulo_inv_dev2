from odoo import models, fields, api, _ # type: ignore
from odoo.exceptions import ValidationError, UserError # type: ignore
import logging
import base64

_logger = logging.getLogger(__name__)
 
class ProductExtensionWizard(models.TransientModel):
    _name = 'product.wizard'
    _description = 'Impresión de Etiquetas para Productos'
    pdf_file = fields.Binary(string="PDF de Etiqueta", readonly=True)
    pdf_filename = fields.Char(string="Nombre del Archivo")

    codigo_corto = fields.Char(string="Codigo Corto", store=True)
    codigo_largo = fields.Char(string="Codigo Largo", store=True)
    codigo = fields.Many2one('product.template', string="Código", default=None, domain=[('cl_long_model', '!=', False)])
    numeracion = fields.Many2one('cl.product.numeraciones', string="Numeración", default=None)
    compañia = fields.Many2one('res.company', string="Compañia", default=lambda self: self.env.company)
    company_details = fields.Char(string="Compañia Detalles", default=lambda self: self.env.company.company_details)
    company1 = fields.Char(
        string="Compañia Línea 1",
        compute="_compute_company_details_formatted",
        store=True
    )
    company2 = fields.Char(
        string="Compañia Línea 2",
        compute="_compute_company_details_formatted",
        store=True
    )
    company3 = fields.Char(
        string="Compañia Línea 3",
        compute="_compute_company_details_formatted",
        store=True
    )
    company4 = fields.Char(
        string="Compañia Línea 4",
        compute="_compute_company_details_formatted",
        store=True
    )

    color = fields.Char(string="Color", compute="_compute_color", store=True)
    cantidad = fields.Integer(string="cantidad", default=0)

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

    @api.depends('company_details')
    def _compute_company_details_formatted(self):
        for record in self:
            if record.company_details:
                details = record.company_details
                details = details.replace("<p>", "").replace("</p>", "").replace("<br>", "").strip()
                lines = details.split("\n")
                record.company1 = lines[0] if len(lines) > 0 else ''
                record.company2 = lines[1] if len(lines) > 1 else ''
                record.company3 = lines[2] if len(lines) > 2 else ''
                record.company4 = lines[3] if len(lines) > 3 else ''
            else:
                record.company1 = ''
                record.company2 = ''
                record.company3 = ''
                record.company4 = ''

    @api.depends('codigo')
    def _compute_color(self):
        for record in self:
            if record.codigo and record.codigo.cl_long_model:
                record.color = record.codigo.cl_long_model[-2:]
            else:
                record.color = ''

    @api.constrains('zpl_format', 'codigo', 'numeracion', 'cantidad', 'compañia')
    def _check_required_fields(self):
        for record in self:
            if record.cantidad <= 0:
                raise ValidationError(_("La cantidad debe ser mayor a cero para cualquier formato"))

            if record.zpl_format == 'format1' and not record.codigo:
                raise ValidationError(_("El campo Codigo es requerido para el formato seleccionado"))
            
            if record.zpl_format == 'format2':
                if not record.numeracion:
                    raise ValidationError(_("El campo Numeracion es requerido para el formato seleccionado"))
                if not record.compañia:
                    raise ValidationError(_("El campo Compañia es requerido para el formato seleccionado"))
            
            if record.zpl_format == 'format3':
                if not record.codigo:
                    raise ValidationError(_("El campo Codigo es requerido para el formato seleccionado"))
                if not record.numeracion:
                    raise ValidationError(_("El campo Numeracion es requerido para el formato seleccionado"))
            
    def generate_zpl_label(self):
        self.ensure_one()
        
        if not self._context.get('bypass_validation'):
            self._check_required_fields()

        codigo = self.codigo.name if self.codigo else ''
        numeracion = self.numeracion.numero if self.numeracion else ''
        cantidad = self.cantidad if self.cantidad > 0 else 1
        color = self.color
        codigo_corto = self.codigo.cl_short_model if self.codigo else ''
        codigo_largo = self.codigo.cl_long_model if self.codigo else ''
        compañia = self.compañia.name if self.compañia else ''
        company_details = self.company_details if self.company_details else ''
        company1 = self.company1 if self.company1 else ''
        company2 = self.company2 if self.company2 else ''
        company3 = self.company3 if self.company3 else ''
        company4 = self.company4 if self.company4 else ''

        format_templates = {
            'format1': """
^XA         
^FO50,170
^A0N,40,40
^FDCantidad: {cantidad}
^FS
^FO50,230
^B3N,N,100,Y,N
^FD{codigo}
^FS
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
^FO720,320^A0R,50,50^FD{compañia}^FS
^FO670,320^A0R,50,50^FD{company2}^FS
^FO620,320^A0R,50,50^FD{company3}{company4}^FS
^FO550,320^A0R,50,50^FD{compañia} ^FS
^FO500,320^A0R,50,50^FDAV MIRAFLORES 8860 RENCA^FS
^FO450,320^A0R,50,50^FDNUNOA^FS
^FO400,320^A0R,50,50^FDINV2025^FS
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
{color}
^FS
^FX 
^LRY
^FO290,20^GB290,90,90^FS
^CF0,70 ^FX 
^FO290,30^FD
{codigo_corto}
^FS
^FX 
^BY2,3,,^FO110,123^BCN,80,N,N,N^FD
{codigo_largo}{numeracion}
^FS
^FX SKU.
^FO160,210^A0N,30,40^FD
{codigo_largo}{numeracion}
^FS
^XZ
            """
        }

        template = format_templates.get(self.zpl_format, "").strip()
        
        zpl_content = ""
        for i in range(cantidad):
            zpl_content += template.format(
                numeracion=numeracion, 
                codigo=codigo, 
                cantidad=cantidad,
                codigo_corto=codigo_corto,
                codigo_largo=codigo_largo,
                color=color,
                compañia=compañia,
                company_details=company_details,
                company1=company1,
                company2=company2,
                company3=company3,
                company4=company4
            ) + "\n" 
        
        return zpl_content.strip()

    def generador_txt_zpl(self):
        self.ensure_one()
        
        try:
            zpl = self.generate_zpl_label()
            if not zpl:
                raise UserError(_("Formato de etiqueta no valido"))

            filename = f"{self.codigo.cl_long_model if self.codigo else 'EtiquetaZPL'}.txt"
            txt_content = base64.b64encode(zpl.encode('utf-8'))

            self.write({
                'pdf_file': txt_content,
                'pdf_filename': filename
            })

            return {
                'type': 'ir.actions.act_url',
                'url': f"/web/content?model=product.wizard&id={self.id}&field=pdf_file&filename_field=pdf_filename&download=true",
                'target': 'self',
            }
        except Exception as e:
            raise UserError(_("Error: %s") % str(e))
        





