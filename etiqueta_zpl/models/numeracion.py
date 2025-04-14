from odoo import models, fields, _

class Numeracion(models.Model):
    _name = 'cl.product.numeraciones'
    _description = 'Numeracion de Productos'
    _order = 'id asc'

    numero = fields.Char(string="Numero", required=True) 