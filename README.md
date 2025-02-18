# Modulo impresion de etiquetas

## Alcance del modulo

Modulo extendido de modelo producto el cual genera etiquetas ZPL descargandolas en formato PDF para su impresion.

## Modelos 

### `product.codigo`
- Fields:
  - `name` (Char): Codigos de productos.

### `product.numero`
- Fields:
  - `name` (Char): Numero de productos.

### `product.cantidad`
- Fields:
  - `name` (Integer): Cantidad de productos.

### `pdf_file`
- Fields:
  - `name` (Binary): Etiqueta en PDF.

### `pdf_filename`
- Fields:
  - `name` (Char): Nombre del Archivo.

_________________________________________________

### `Funciones`

  - `Funcion` (generate_zpl_label)
  - `Funcion` (generate_pdf_from_zpl)
