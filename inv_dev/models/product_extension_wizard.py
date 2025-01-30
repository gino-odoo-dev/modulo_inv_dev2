from odoo import models, fields, api
import os
import logging

_logger = logging.getLogger(__name__)

class Codigo(models.Model):
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

    name = fields.Float(string="Cantidad", default=0.0)

class ProductExtensionWizard(models.TransientModel):
    _name = 'product.extension.wizard'
    _description = 'Product Extension Wizard'

    id_codigo = fields.Many2one('product.codigo', string="Codigo", required=True)
    id_numero = fields.Many2one('product.numero', string="Numero", required=True)
    cantidad = fields.Float(string="Cantidad", default=0.0, required=True)
    name = fields.Char(string="Nombre")
    zpl_content = fields.Text(string="ZPL Content", readonly=True)
    active = fields.Boolean(string="Active", default=True)
   

    @api.model
    def generate_zpl_label(self, vals):
        if isinstance(vals, int):  
            vals = {}

        if isinstance(vals, models.BaseModel):
            vals = vals.read()[0]
        elif isinstance(vals, list):
            vals = vals[0]

        codigo = vals.get('id_codigo', 'Desconocido')  
        numero = vals.get('id_numero', 'Desconocido') 
        cantidad = vals.get('cantidad', 0.0)  

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
        return zpl


    @api.model
    def create_and_generate_zpl(self, vals):
        if isinstance(vals, list):
            vals = vals[0] 
        if isinstance(vals, models.BaseModel):
            vals = vals.read()[0] 
        zpl = self.generate_zpl_label(vals) 
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.extension.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_zpl_content': zpl},
        }
