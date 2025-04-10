from odoo import models, fields

class Codigo(models.Model):
    _name = 'product.codigo'
    _description = 'Codigo de Producto'
    name = fields.Char(string="Articulo", required=True)