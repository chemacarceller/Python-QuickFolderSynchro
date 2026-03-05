# Python-QuickFolderSynchro

A fast folder synchronization utility written in python

It takes the source and destination folders as parameters.

Once their existence is verified and the intention to synchronize them is confirmed, it will quickly modify the contents of the second folder to exactly match the first, as it only checks the size and modification date of each file to determine if it needs to be replaced.

The script performs the following steps:
 - Create the destination directory if it doesn't exist.
 - For each directory, it looks for files that are not directories. If their contents are different from the destination, they are copied.
 - Determine if the content differs based on size and modification date for an ultra-fast check
 - In the destination directory, it checks the list of files and directories that are not in the source and removes them.
 - For each Source directory, recursively run the script.

The QuickFolderSynchro.run file is the Linux executable compiled by Niutka. It's not strictly necessary since the Python script has the shellbang that makes it inherently executable. The only advantage of the .run file over the .py file is that the source code isn't visible when editing it.

For Windows, it could be run using    python QuickFolderSynchto.py   (since shellbang doesn't work on Windows).

However, the script has also been compiled using Niutka, creating both an .exe file (using the --onefile option) and a .zip file (using the --standalone option). The .zip file must be extracted to the desired folder before it can be run.

The Pro version is an optimized version because it passes the code for accessing log files to be developed in a C++ module that is accessible from the Python code.

The LogFileWriter···.so and LogFileWrite···.pyd files are the result of compiling the LogFileWriter.cpp file on Linux and Windows; if you want to run the script from the source file, these binaries must be located in the same directory as the source file.

======================================================================

Utilidad de sincronización rápida de carpetas escrita en python

Recibe como parametros la carpeta de origen y la carpeta destino

Una vez comprobada su existencia y verificada la intención de sincronizarlas, modificará el contenido de la segunda carpeta para que sea exactamente el mismo que la primera de forma rápida, ya que únicamente comprueba el tamaño y la fecha de modificación de cada uno de los archivos para determinar si debe reemplazarse

El script realiza los siguientes pasos:
- Crea el directorio de destino si no existe.
- Para cada directorio, busca archivos que no seas directorios. Si su contenido es diferente al del destino, se copia.
- Determina si el contenido es diferente según el tamaño y la fecha de modificación para que sea una comprobación ultrarápida
- En el directorio destino comprueba la lista de archivos y directorios que no están en el origen y los elimina.
- Ejecuta el script recursivamente para cada directorio de origen.

El fichero QuickFolderSynchro.run es el ejecutable para linux compilado con Niutka, realmente no es necesario ya que el script de python tiene el shellbang que lo hace intrinsecamente ejecutable, la única ventaja del fichero .run respecto al fichero .py es que al editarlo no aparace el codigo fuente

Para windows se podría ejecutar mediante     python QuickFolderSynchto.py    (ya que el shellbang no funciona en windows)

Sin embargo, también mediante Niutka se ha compilado el script y se ha creado un .exe (opcion --onefile) y un .zip (opcion --standalone), este ultimo debe descomprimirse en la carpeta deseada para poder ejecutarlo.

La version Pro es una version optimizada porque se pasa el codigo de acceso a ficheros de logs a ser desarrollado en un modulo de C++ que es accesible desde el código de Python

Los archivos LogFileWriter···.so y LogFileWrite···.pyd son los archivos resultantes de compilar el fichero LogFileWriter.cpp en Linux y en Windows; si se desea ejecutar el script desde el fichero fuente es necesario que estos archivos binarios esten ubicados en el mismo directorio que el fichero fuente
