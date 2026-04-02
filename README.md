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

Everything in the root directory is the tool exclusively programmed in python

The Basic, Advanced and Advanced Plus folders incorporate a C++ LogFileWriter class to store logs in a file

Basic: The class used is a Basic version 

Advanced: The class used is an advanced version that implements a singleton, the class was developed to store games in Godot and has been adapted to this Python script
Problem: Although it is a singleton, it is at the process level, but in this case processes are launched recursively so a different singleton class is instantiated for each process

Advanced plus: The class used in Advanced is adapted to generate a singleton between processes, establishing a memory region where the only singleton instance is stored and accessible by any process, this implies a level jump in the C++ class

Testing:

After testing all four versions, I obtained the following data:

Compared to the version without C++ (Python only), the Basic version improves performance by 4.75%, the Advanced version by 6.03%, and the Advanced Plus version by 6.74%.

Compared to the Basic (C++) version, the Advanced version improves performance by 1.16%, and the Advanced Plus version by 2.11%.

Compared to the Advanced (C++) version, the Advanced Plus version improves performance by 0.96%.


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

Todo lo que hay en el directorio raiz es la herramienta exclusivamente programada en python

Las carpetas Basic, Advanced y Advanced Plus incorporan una clase C++ LogFileWriter para almacenar logs en fichero

Basic : La clase utilizada es una version Basic 

Advanced : La clase utilizada es una version avanzada que implementa un singleton, la clase se desarrolló para almacenar los juegos en Godot y ha sido adaptada a este script de Python
Problema : Aunque es un singleton, lo es a nivel de proceso, pero en este caso se lanzan procesos de forma recursiva por lo que se instancia una clase singleton distinta para cada proceso

Advanced Plus : Se adapta la clase utilizada en Advanced para generar un singleton entre procesos, estableciendo una región de memoria donde se almacena la única instancia singleton siendo accesible por cualquier proceso, esto implica un salto de nivel en la clase C++

Testing :

Una vez testeadas las 4 versiones he obtenido los siguientes datos :

Respecto a la version sin C++ (python only) la version Basic mejora el rendimiento en un 4.75%, la version Advanced en un 6.03% y la version Advanced Plus en un 6.74%

Respecto a la version Basic (C++) la version Advanced mejora el rendimiento en un 1,16%, la versión Advanced Plus 2.11%

Respecto a la version Advanced (C++) la version Advanced Plus mejora el rendimiento en un 0.96%
