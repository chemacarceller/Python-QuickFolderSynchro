# Python-QuickFolderSynchro

A fast folder synchronization utility written in python

It takes the source and destination folders as parameters.

Once their existence is verified and the intention to synchronize them is confirmed, it will quickly modify the contents of the second folder to exactly match the first, as it only checks the size and modification date of each file to determine if it needs to be replaced.

The script performs the following steps:
 - Create the destination directory if it doesn't exist.
 - For each directory, check for files of type other than directory. If they have content different from the destination, copy them.
 - It estimates the different content based on sizes and modification dates.
 - Check the list of regular files and directories different from the Destination that are not in the Source and delete them.
 - For each Source directory, recursively run the script.

The QuickFolderSynchro.run file is the Linux executable obtained from PyInstaller. It's not strictly necessary since the Python script has the shellbang that makes it inherently executable. The only advantage of the .run file over the .py file is that the source code isn't visible when editing it.

======================================================================

Utilidad de sincronización rápida de carpetas escrita en python

Recibe como parametros la carpeta de origen y la carpeta destino

Una vez comprobada su existencia y verificada la intención de sincronizarlas, modificará el contenido de la segunda carpeta para que sea exactamente el mismo que la primera de forma rápida, ya que únicamente comprueba el tamaño y la fecha de modificación de cada uno de los archivos para determinar si debe reemplazarse

El script realiza los siguientes pasos:
- Crea el directorio de destino si no existe.
- Para cada directorio, busca archivos de un tipo distinto al directorio. Si su contenido es diferente al del destino, cópialos.
- Calcula el contenido diferente según el tamaño y la fecha de modificación.
- Comprueba la lista de archivos y directorios normales, distintos del destino, que no están en el origen y los elimina.
- Ejecuta el script recursivamente para cada directorio de origen.

El fichero QuickFolderSynchro.run es el ejecutable para linux obtenido a partir de pyinstaller, realmente no es necesario ya que el script de python tiene el shellbang que lo hace intrinsecamente ejecutable, la única ventaja del fichero .run respecto al fichero .py es que al editarlo no aparace el codigo fuente

