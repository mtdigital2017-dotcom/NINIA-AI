# Política de respaldo

## Alcance

Cada push a `main` genera un paquete de respaldo con archivos versionados, documentación y memoria operativa.

## Exclusiones

- credenciales;
- secretos;
- entornos virtuales;
- cachés;
- archivos `.pyc`;
- datos cargados por usuarios;
- objetos de conocimiento generados durante ejecución;
- resultados temporales.

## Integridad

El paquete incluye:

- `MANIFEST.json`;
- checksum SHA-256;
- nombre del repositorio;
- rama;
- commit;
- fecha UTC.

Después de subir el ZIP, el script compara el MD5 local con el `md5Checksum` reportado por Google Drive. Una diferencia produce error y el workflow falla.

## Retención

Los paquetes se nombran con commit y fecha. La eliminación o política de conservación se definirá después de observar el volumen real.
