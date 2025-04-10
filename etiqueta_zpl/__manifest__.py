{
    'name': 'Etiquetas ZPL',
    'version': '1.0',
    'summary': 'Modulo para generar etiquetas ZPL',
    'description': ' etiquetas ZPL.',
    'author': 'MarcoAG',
    'depends': ['product', 'stock', 'web'],  
    'data': [
        'security/ir.model.access.csv',
        'views/etiqueta_zpl_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'etiqueta_zpl/static/src/css/style.css',
        ],
    },
    'installable': True,
    'application': True,
}