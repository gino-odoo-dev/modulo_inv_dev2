from odoo import models, fields

class Cantidad(models.Model):
    _name = 'product.cantidad'
    _description = 'Cantidad de Producto'
    name = fields.Float(string="Cantidad", default=0.0)