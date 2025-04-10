{
    'name': 'Etiqueta ZPL',
    'version': '1.0',
    'summary': 'Modulo para generar etiquetas ZPL',
    'description': 'etiqueta ZPL.',
    'author': 'MarcoAG',
    'depends': ['product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/zpl_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'etiqueta_zpl/static/src/js/dynamic_fields.js',
            'etiqueta_zpl/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
}
