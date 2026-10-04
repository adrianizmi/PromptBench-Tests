# Dataset de evaluacion

Cada linea de `v1.jsonl` es un objeto JSON independiente. El dataset contiene cinco casos pequenos: paridad, normalizacion de texto, limites numericos, eliminacion de duplicados conservando el orden y conteo de vocales.

Campos iniciales:

- `id`: identificador unico y estable.
- `description`: comportamiento que los tests deben comprobar.
- `source_filename`: nombre con el que se escribira el codigo temporalmente.
- `source_code`: implementacion Python bajo prueba.
- `test_filename`: nombre esperado para el archivo generado por el modelo.
- `tags`: categorias para segmentar resultados despues.

Los casos deben ser pequenos, deterministas y sinteticos. Los nombres de archivo deben ser nombres simples como `module.py`, sin directorios. No incluyas secretos, datos personales ni codigo corporativo.
