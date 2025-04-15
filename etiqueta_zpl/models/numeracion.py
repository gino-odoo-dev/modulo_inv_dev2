from odoo import models, fields, _, api # type: ignore

class Numeracion(models.Model):
    _name = 'cl.product.numeraciones'
    _description = 'Numeracion de Productos'
    _order = 'id asc'

    numero = fields.Char(string="Numero", required=True)
    name = fields.Char(string="Nombre", compute='_compute_name', store=True)
    
    @api.depends('numero')
    def _compute_name(self):
        for record in self:
            record.name = f"Num: {record.numero}"