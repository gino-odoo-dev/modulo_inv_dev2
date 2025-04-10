from odoo import models, fields

class Numeracion(models.Model):
    _name = 'cl.product.numeracion'  
    _description = 'Numeracion de Productos'
    _rec_name = "numero" 

    name = fields.Char(string="Nombre")
    numero = fields.Integer(string="Numero de Talla", required=True)


