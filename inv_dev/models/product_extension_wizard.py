from odoo import models, fields, api  
import os 
import logging 
# se configura el logger
_logger = logging.getLogger(__name__) 

# se define el modelo
class Codigo(models.Model):
    # nombre del modelo en odoo
    _name = 'product.codigo'  
    _description = 'Codigo'  
    name = fields.Char(string="Articulo")


class Numero(models.Model):
    _name = 'cl.product.tallas'  
    _description = 'Tallas'   
    name = fields.Char(string="Nro. Zapato")
    company_id = fields.Many2one('res.company', string="Company") 


class Cantidad(models.Model):    
    _name = 'product.cantidad' 
    _description = 'Cantidad' 
    # campo Float con valor defecto 0
    name = fields.Float(string="Cantidad", default=0.0)  


# se define el modelo (wizard para la extension de productos)
class ProductExtensionWizard(models.TransientModel):
    _name = 'product.extension.wizard'  
    _description = 'Product Extension Wizard'  

    id_codigo = fields.Many2one('product.codigo', string="Codigo", required=True)  
    id_numero = fields.Many2one('cl.product.tallas', string="Tallas", required=True)  
    cantidad = fields.Integer(string="Cantidad", default=0, required=True)  # Fix default value
    # campo para almacenar el codigo zpl generado  
    zpl_content = fields.Text(string="ZPL Content", readonly=True)  

    # metodo para generar la etiqueta
    @api.model
    def generate_zpl_label(self, vals):
        # obtener los registros de los modelos
        codigo_record = self.env['product.codigo'].browse(vals.get('id_codigo'))
        numero_record = self.env['cl.product.tallas'].browse(vals.get('id_numero'))

        # extraer los valores de los registros o asignar 'Desconocido' si no existen
        codigo = codigo_record.name if codigo_record else 'Desconocido'
        numero = numero_record.name if numero_record else 'Desconocido'
        cantidad = vals.get('cantidad', 0)  # obtener la cantidad, por defecto 0

        # definir el contenido en formato zpl
        zpl = f"""
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
        ^CF0,90 ^FX
        ^FO340,30^FD
        {numero}
        ^FS
        ^FX
        ^BY2,3,,^FO110,123^BCN,80,N,N,N^FD
        {codigo}
        ^FS
        ^FX SKU.
        ^FO160,210^A0N,30,40^FD
        {codigo}
        ^FS
        ^XZ
        """
        # retornar el ZPL sin espacios en blanco
        return zpl.strip()  

    # metodo para generar la etiqueta
    def create_and_generate_zpl(self):
        # se crea un diccionario para los valores d elos campos
        vals = {
            'id_codigo': self.id_codigo.id if self.id_codigo else '',
            'id_numero': self.id_numero.id if self.id_numero else '',
            'cantidad': self.cantidad
        }
        
        # se genera el contenido zpl
        zpl = self.generate_zpl_label(vals)
        
        # se crear una instancia con los datos
        wizard = self.create({
            'id_codigo': self.id_codigo.id,
            'id_numero': self.id_numero.id,
            'cantidad': self.cantidad,
            'zpl_content': zpl
        })
        
        # se abre la vista del asistente
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.extension.wizard',
            'view_mode': 'form',
            'res_id': wizard.id, 
            'target': 'new',
        }

    # metodo para imprimir la etiqueta
    def print_zpl_label(self):
        # se registra en el log el contenido de la etiqueta para ver su contenido por consola
        _logger.info(f"Printing ZPL Label: {self.zpl_content}")
        
        printer_ips = ["10.10.1.16", "10.10.1.17", "10.10.1.18"]
        
        for printer_ip in printer_ips:
            _logger.info(f"Sending ZPL to printer at IP: {printer_ip}")
            try:
                import socket
                # Crear un socket de conexión
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((printer_ip, 9100))  # puerto 9100 puerto estandar 
                    s.sendall(self.zpl_content.encode('utf-8'))
                    _logger.info(f"ZPL sent to printer at IP: {printer_ip}")
            except Exception as e:
                _logger.error(f"Failed to send ZPL to printer at IP: {printer_ip} - {e}")
        # se retorna True indicando que el proceso finalizo correctamente  
        return True