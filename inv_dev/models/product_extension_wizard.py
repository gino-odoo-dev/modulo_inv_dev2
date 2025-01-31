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
    
    name = fields.Char(string="Codigo")


class Numero(models.Model):
    _name = 'product.numero'  
    _description = 'Numero'  
    
    name = fields.Char(string="Numero")  


class Cantidad(models.Model):    
    _name = 'product.cantidad' 
    _description = 'Cantidad' 
    # campo Float con valor defecto 0.0
    name = fields.Float(string="Cantidad", default=0.0)  

# se define el modelo (wizard para la extension de productos)
class ProductExtensionWizard(models.TransientModel):
    _name = 'product.extension.wizard'  
    _description = 'Product Extension Wizard'  

    id_codigo = fields.Many2one('product.codigo', string="Codigo", required=True)  
    id_numero = fields.Many2one('product.numero', string="Numero", required=True)  
    cantidad = fields.Integer(string="Cantidad", default=0.0, required=True)
    # campo para almacenar el codigo zpl generado  
    zpl_content = fields.Text(string="ZPL Content", readonly=True)  

    # metodo para generar la etiqueta
    @api.model
    def generate_zpl_label(self, vals):
        # obtener los registros de los modelos
        codigo_record = self.env['product.codigo'].browse(vals.get('id_codigo'))
        numero_record = self.env['product.numero'].browse(vals.get('id_numero'))

        # extraer los valores de los registros o asignar 'Desconocido' si no existen
        codigo = codigo_record.name if codigo_record else 'Desconocido'
        numero = numero_record.name if numero_record else 'Desconocido'
        cantidad = vals.get('cantidad', 0)  # obtener la cantidad, por defecto 0

        # definir el contenido en formato zpl
        zpl = f"""
        ^XA
        ^FO50,50 
        ^B3N,N,100,Y,N
        ^FD>: {codigo}^FS 
        ^FO50,200
        ^A0N,50,50
        ^FDNumero: {numero}^FS  
        ^FO50,300
        ^A0N,50,50
        ^FDCantidad: {cantidad}^FS
        ^FO50,400
        ^GB800,3,3^FS            
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
        # se registra en el log el contenido de la etiqueta (para ver su contenido por consola)
        _logger.info(f"Printing ZPL Label: {self.zpl_content}")
        # se retorna True indicando que el proceso finalizo correctamente  
        return True  

