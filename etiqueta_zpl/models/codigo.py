from odoo import models, fields, api, _ # type: ignore

class Codigo(models.Model):
    _inherit = 'product.template' 
    _description = 'Código de Producto'
    
    cl_long_model = fields.Char(string="Codigo Largo", required=True)
    cl_short_model = fields.Char(string="Codigo Corto", required=True)
    
    @api.depends('cl_long_model')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.cl_long_model or 'Codigo Largo'

    @api.depends('cl_short_model')
    def _compute_display_name_short(self):
        for record in self:
            record.display_name_short = record.cl_short_model or 'Codigo Corto'