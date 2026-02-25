#!/usr/bin/env python3 

# QuickFolderSynchro.py
# This script synchronizes two folders, the source and the destination, making the destination folder identical to the source folder. 
# It copies files from the source to the destination if they do not exist in the destination or if they exist but have a different size or modification date. It also deletes files from the destination if they do not exist in the source. 
# The script is designed to be efficient and to handle large folders with many files and directories. 
# It also handles errors gracefully, printing error messages and exiting with appropriate error codes. 
# The script is designed to be run from the command line, and it takes two arguments: the source directory and the destination directory. 
# The script also creates a log file in the current directory, where it logs the actions taken and the statistics of the synchronization process. 
# The script is designed to be run on Windows and Linux, and it uses the same code for both platforms, since it uses the os and shutil modules, which are cross-platform.
import sys
import os
import shutil
import subprocess


# All the code will be inside a try block, so that if any command fails, the error is handled eficiently, printing an error message and exiting with an appropriate error code. This way, we can be sure that any error that occurs during the execution of the script is handled gracefully, and we can provide useful information to the user about what went wrong, without crashing the script or leaving it in an inconsistent state.

try :

    # We initialize the variable that will hold the new environment with our custom brand name, which is used to check if the script is being executed recursively. This variable is initialized to None, and it will be assigned a value if the script is not being executed recursively, which means that we are in the parent execution of the script, and we need to create a new environment with our custom brand name to pass it to the child executions of the script. If the script is being executed recursively, this variable will remain None, since we do not need to create a new environment, since we are already in a child execution of the script, and we can use the same environment as the parent execution.
    nuevo_env = None

    # Our custom brand name to check if the script is being executed recursively, it is stored in an environment variable that we will check at the beginning of the script
    VAR_RECURSION = "QUICKFOLDERSYNCHRO_RECURSION"
    # Boolean variable to indicate if the script is being executed recursively, it is initialized to False and will be set to True if the environment variable is detected
    isRecursiveExecution = False

    # How we should open the log file, w for parent, a for children
    fileMode='w'

    # If the environment variable is not detected, it means that we are in the parent execution of the script, and we need to create a new environment with our custom brand name to pass it to the child executions of the script. If the environment variable is detected, it means that we are in a child execution of the script, and we can use the same environment as the parent execution, since we are already in a child execution of the script, and we do not need to create a new environment.
    if not os.environ.get(VAR_RECURSION) == "1":
        # We created a copy of the current environment and added our branding.
        nuevo_env = os.environ.copy()
        nuevo_env[VAR_RECURSION] = "1"
    else :
        # If the environment variable is detected, it means that we are in a child execution of the script, and we can use the same environment as the parent execution, since we are already in a child execution of the script, and we do not need to create a new environment. We also set the file mode to append, since we want to append to the log file instead of overwriting it, since we are in a child execution of the script, and we want to keep the log of the parent execution and all the child executions in the same log file.
        fileMode='a'
        # We set the boolean variable to indicate that we are in a recursive execution, since we have detected the environment variable that indicates that we are in a child execution of the script, which means that we are in a recursive execution of the script, and we can use this variable to skip the confirmation of the destination directory, since we are already in a child execution of the script, and we do not want to ask for confirmation again, since it has already been confirmed in the parent execution of the script.
        isRecursiveExecution = True

    # LOGFILE is the name of the file where the log will be stored, it is created in the current directory and overwritten if it already exists
    LOGFILE = "QuickFolderSynchro.log"

    #The QuickFolderSynchro file is opened for writing during execution
    with open(LOGFILE, fileMode) as file :

        # Wrong arguments...
        if not isRecursiveExecution and len(sys.argv) != 3 :
            errorCode = 1
            errorText = "Wrong arguments"
            raise Exception(errorText, errorCode)
        
        # The source and target directories are extracted from the command line arguments, and they are stored in variables for later use. These variables are used throughout the script to refer to the source and target directories, and they are also used in the log messages to indicate which directories are being processed. This way, we can keep track of the source and target directories throughout the script, and we can provide useful information to the user about which directories are being processed at each step of the synchronization process.
        sourceDirectory = sys.argv[1]
        targetDirectory = sys.argv[2]

        # Showing the source and target directories, both in the console and in the log file 
        #print("SOURCE Directory :", sourceDirectory)
        print("SOURCE Directory :", sourceDirectory, file=file)
        #print("TARGET Directory :", targetDirectory)
        print("TARGET Directory :", targetDirectory, file=file)

        # It is detected that this is not a recursive execution
        if not isRecursiveExecution :
            # We request confirmation that the destination directory is correct.
            resp = input(f"Confirm that {targetDirectory} is correct? Answer Yes to continue, No to cancel : ");
            while resp != "Yes" :
                if resp == "No" : 
                    errorCode = 2
                    errorText = "Aborted by the user does not confirm that the destination directory is correct."
                    raise Exception(errorText, errorCode)
                resp = input(f"Confirm that {targetDirectory} is correct? Answer Yes to continue, No to cancel : ")

        # Variables for task statistics

        # In source Directory
        foundFilesAndDir=0
        foundFiles=0
        foundDirectories=0

        # In source Directory and target directory
        copiedFoundFiles=0
        notCopiedFoundFiles=0
        copiedNotFoundFiles=0

        # In target Directory
        targetFoundFilesAndDir=0
        targetFoundFiles=0
        targetFoundDirectories=0

        # In target Directory but not in source Directory
        targetFoundFilesNotInSource=0
        targetFoundDirNotInSource=0
        targetDeletedFilesAndDir=0

        # The source directory does not exist.
        if not os.path.exists(sourceDirectory) :
            # If the source directory does not exist, we print an error message and raise an exception with an appropriate error code, since the synchronization process cannot continue if the source directory does not exist, and it is important to provide useful information to the user about what went wrong, so that they can fix the problem and run the script again successfully.
            errorCode = 3
            errorText = f"The source directory {sourceDirectory} does not exist" 
            raise Exception(errorText, errorCode)
        
        # The destination directory does not exist.
        if not os.path.exists(targetDirectory) :
            if isRecursiveExecution :
                # If the destination directory does not exist, we print a message indicating that it does not exist and that it is being created, both in the console and in the log file, and then we create the destination directory, since it is necessary for the synchronization process to continue, and it is better to create the destination directory if it does not exist than to raise an error and stop the synchronization process, since the user may have made a mistake when entering the destination directory, and it is better to create it than to stop the process and make them fix the mistake and run the script again.
                print(f"The destination directory {targetDirectory} does not exist, it is created")
                print(f"\nThe destination directory {targetDirectory} does not exist, it is created", file=file)
                os.mkdir(targetDirectory)
            else :
                # If the destination directory does not exist, we print an error message and raise an exception with an appropriate error code, since the synchronization process cannot continue if the destination directory does not exist, and it is important to provide useful information to the user about what went wrong, so that they can fix the problem and run the script again successfully.
                errorCode = 4
                errorText = f"The destination directory {targetDirectory} does not exist" 
                raise Exception(errorText, errorCode)
        
        #print(f"\nSEARCHING FOR FILES IN {sourceDirectory} : " )
        print(f"\nSEARCHING FOR FILES IN {sourceDirectory} : ", file=file )

        # If there are no files in the source directory, we print a message and skip to the next step, which is to check the destination directory for files that do not exist in the source directory. Otherwise, we continue with the synchronization process. 
        if len(os.listdir(sourceDirectory)) == 0 :
            #print(f"There are no files in {sourceDirectory} : " )
            print(f"There are no files in {sourceDirectory} : ", file=file )     
        else:
            # For each file item in source directory
            for fileItem in os.listdir(sourceDirectory) :

                # Incrementing the total number of files and directories found in the source directory, including directories, which will be processed later in the script. This variable is used for statistics at the end of the script.
                foundFilesAndDir += 1

                # For each SOURCE file, the name, size, and modification date are extracted.
                sourceName = fileItem
                sourcePath = os.path.join(sourceDirectory, sourceName)
                sourceFileSize = os.path.getsize(sourcePath)
                sourceFileModificationTime = os.path.getmtime(sourcePath)

                # Files with square brackets cause problems, so they are replaced with hyphens. also applies to directories, since they will be processed later in the script, and if they have square brackets, they will cause problems when trying to access them. This is done before processing the files, so we are sure that all the files and directories that we process do not have square brackets, and we do not have to worry about them later in the script. If we did this after processing the files, we would have to worry about files and directories with square brackets that we have already processed, which would complicate the script and make it less efficient.
                tabla = str.maketrans("[]", "--")
                sourceNameModified = sourceName.translate(tabla)
                if sourceName != sourceNameModified :
                    print(f"File {sourceName} contains square brackets, it is renamed to {sourceNameModified}")
                    print(f"File {sourceName} contains square brackets, it is renamed to {sourceNameModified}", file=file)
                    os.rename(sourcePath, os.path.join(sourceDirectory, sourceNameModified))
                    sourceName = sourceNameModified
                    sourcePath = os.path.join(sourceDirectory, sourceName)

                # The path of the file in the destination directory is constructed, and it is checked if it exists. If it exists, the number of files found in the destination directory is incremented, and its size and modification date are compared with those of the source file. If they are the same, it is not copied, and the number of files not copied is incremented. If they are different, it is copied, and the number of files copied is incremented. If it does not exist, it is copied, and the number of files copied is incremented.
                targetPath = os.path.join(targetDirectory, sourceName)

                # If the file is not a directory, otherswise it will be processed later in the script, it is checked if it exists in the destination directory. If it does not exist, it is copied. If it exists, its size and modification date are compared with those of the source file. If they are the same, it is not copied. If they are different, it is copied.
                if not os.path.isdir(sourcePath) :

                    # Incrementing the number of files found in the source directory, excluding directories, this variable is used for statistics at the end of the script.
                    foundFiles += 1

                    # If the file exists in the destination directory, we check if it has the same size and modification date as the source file. If it does, it is not copied. If it does not, it is copied. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                    if os.path.exists(targetPath) :   
                        # If the file exists in the destination directory, we check if it has the same size and modification date as the source file. If it does, it is not copied. If it does not, it is copied. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.                     
                        targetFileSize = os.path.getsize(targetPath)
                        targetFileModificationTime = os.path.getmtime(targetPath)

                        # If the file exists in the destination directory and has the same size and modification date as the source file, it is not copied, and a message is printed indicating that it already exists with the same size and modification date. If it exists but has a different size or modification date, it is copied, and a message is printed indicating that it already exists but with different size or modification date, so it is copied. In both cases, the corresponding statistics are updated.
                        if sourceFileSize == targetFileSize and sourceFileModificationTime == targetFileModificationTime :
                            #print(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory with the same size and modification time, it is not copied")
                            print(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory with the same size and modification time, it is not copied", file=file)
                            notCopiedFoundFiles += 1
                        else :
                            # The file exists in the destination directory but has a different size or modification date, it is copied, and a message is printed indicating that it already exists but with different size or modification date, so it is copied. In both cases, the corresponding statistics are updated.
                            print(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory but with different size or modification time, it is copied")
                            print(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory but with different size or modification time, it is copied", file=file)
                            shutil.copy2(sourcePath, targetPath)
                            copiedFoundFiles += 1
                    else :
                        # The file does not exist in the destination directory, it is copied, and a message is printed indicating that it does not exist in the destination directory, so it is copied. In both cases, the corresponding statistics are updated.
                        print(f"{sourceDirectory.upper()} : File {sourcePath} does not exist in the destination directory, it is copied")
                        print(f"{sourceDirectory.upper()} : File {sourcePath} does not exist in the destination directory, it is copied", file=file)
                        shutil.copy2(sourcePath, targetPath)
                        copiedNotFoundFiles += 1
                else :
                    # Incrementing the number of directories found in the source directory, excluding files, this variable is used for statistics at the end of the script.
                    foundDirectories += 1

        # Printing the statistics for the source directory, including the total number of files and directories found in the source directory, the number of files found in the source directory, the number of files found in the source directory that already exist in the destination directory, the number of files found in the source directory that already exist in the destination directory but are not copied because they have the same size and modification date, and the number of files found in the source directory that are copied to the destination directory. These statistics are printed both in the console and in the log file.
        print(f"\nSTATISTICS FOR {sourceDirectory} : ", file=file)
        print(f"Number of total items found in source directory: {foundFilesAndDir}", file=file)
        print(f"Number of files found in source directory: {foundFiles}", file=file)
        print(f"Number of directories found in source directory: {foundDirectories}", file=file)
        print(f"Number of source files found in target directory: {copiedFoundFiles + notCopiedFoundFiles}", file=file)
        print(f"Number of source files copied to target directory: {copiedFoundFiles + copiedNotFoundFiles}", file=file)
        print(f"Number of source files found in target not copied to target directory: {notCopiedFoundFiles}", file=file)
            
         
        # The destination is traversed to remove files that do not exist in the source.
        #print(f"\nSEARCHING FOR FILES IN {targetDirectory} : " )
        print(f"\nSEARCHING FOR FILES IN {targetDirectory} : ", file=file )

        # If there are no files in the destination directory, we print a message and skip to the end of the script, which is to print the statistics. Otherwise, we continue with the synchronization process.
        if len(os.listdir(targetDirectory)) == 0 :
            #print(f"There are no files in {targetDirectory} : " )
            print(f"There are no files in {targetDirectory} : ", file=file )  
        else:
            # For each file item in the destination directory, the name is extracted, and it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
            for fileItem in os.listdir(targetDirectory) :

                # Printing a message indicating that the file is being processed, both in the console and in the log file.
                #print(f"Processing {targetDirectory.upper()} : {fileItem}")
                print(f"Processing {targetDirectory.upper()} : {fileItem}", file=file)

                # Incrementing the total number of files and directories found in the destination directory, including directories, which will be processed later in the script. This variable is used for statistics at the end of the script.
                targetFoundFilesAndDir += 1

                # If the file is not a directory, otherwise it will be processed later in the script, it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.     
                if not os.path.isdir(targetPath) :
                    targetFoundFiles += 1
                else :
                    targetFoundDirectories += 1

                # For each TARGET file, the name is extracted, and it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                targetName = fileItem
                targetPath = os.path.join(targetDirectory, targetName)

                # The path of the file in the source directory is constructed, and it is checked if it exists. If it does not exist, it is deleted, and a message is printed indicating that it exists in the destination directory but not in the source directory, so it is deleted. If it exists, it is not deleted, and a message is printed indicating that it exists in both directories, so it is not deleted. In both cases, the corresponding statistics are updated.
                sourcePath = os.path.join(sourceDirectory, targetName)

                # If the file does not exist in the source directory, it is deleted, and a message is printed indicating that it exists in the destination directory but not in the source directory, so it is deleted. If it exists in both directories, it is not deleted, and a message is printed indicating that it exists in both directories, so it is not deleted. In both cases, the corresponding statistics are updated.
                if not os.path.exists(sourcePath) :

                    # Incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                    targetDeletedFilesAndDir += 1

                    # If the file is not a directory, otherwise it will be processed later in the script, it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                    if not os.path.isdir(targetPath) :

                        # Incrementing the number of files found in the destination directory but not in the source directory, this variable is used for statistics at the end of the script.
                        targetFoundFilesNotInSource += 1

                        # Printing a message indicating that the file exists in the destination directory but does not exist in the source directory, so it is deleted, both in the console and in the log file.
                        print(f"{targetDirectory.upper()} : File {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted")
                        print(f"{targetDirectory.upper()} : File {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted", file=file)

                        # Deleting the file in the destination directory, since it does not exist in the source directory, and incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                        os.remove(targetPath)

                    else :

                        # Incrementing the number of directories found in the destination directory but not in the source directory, this variable is used for statistics at the end of the script.
                        targetFoundDirNotInSource += 1

                        # Printing a message indicating that the directory exists in the destination directory but does not exist in the source directory, so it is deleted, both in the console and in the log file.
                        print(f"Directory {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted")
                        print(f"{targetDirectory.upper()} : Directory {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted", file=file)

                        # deleting the directory in the destination directory, since it does not exist in the source directory, and incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                        shutil.rmtree(targetPath)

                        

        # Printing the statistics for the destination directory, including the total number of files and directories found in the destination directory, the number of files found in the destination directory, the number of files found in the destination directory but not in the source directory, the number of directories found in the destination directory but not in the source directory, and the number of files and directories deleted from the destination directory. These statistics are printed both in the console and in the log file.
        print(f"\nSTATISTICS FOR {targetDirectory} : ", file=file)
        print(f"Total files and directories in target directory: {targetFoundFilesAndDir}", file=file)
        print(f"Files found in target directory: {targetFoundFiles}", file=file)
        print(f"Directories found in target directory: {targetFoundDirectories}", file=file)
        print(f"Files found in target directory but not in source directory then deleted : {targetFoundFilesNotInSource}", file=file)
        print(f"Directories found in target directory but not in source directory then deleted : {targetFoundDirNotInSource}", file=file)
        print(f"Files and directories deleted from source directory: {targetDeletedFilesAndDir}", file=file)


    # We trace the origin in search of directories
    # The directory exists in Destination, already verified
    # This is done after processing the files, so we are sure that the directories in the destination directory that do not exist in the source directory have already been deleted, so we can be sure that all the directories that exist in the destination directory also exist in the source directory, and we can process them without worrying about deleting them later. If we did this before processing the files, we would have to worry about deleting directories that do not exist in the source directory but exist in the destination directory, which would complicate the script and make it less efficient.
    # The recursive execution of the script for the directories is done at the end of the script, so we have already processed all the files in the source and destination directories, and we can be sure that all the directories that exist in the destination directory also exist in the source directory, so we can process them without worrying about deleting them later. If we did this before processing the files, we would have to worry about deleting directories that do not exist in the source directory but exist in the destination directory, which would complicate the script and make it less efficient.           
    # It has been taken outside the with statement because we want to be sure that the log file is closed before we start the recursive execution of the script for the directories, since the recursive execution of the script for the directories will also write to the log file, and if we do not close the log file before starting the recursive execution of the script for the directories, we may have problems with concurrent access to the log file, which could cause errors or inconsistencies in the log file. By closing the log file before starting the recursive execution of the script for the directories, we can be sure that there are no problems with concurrent access to the log file, and we can be sure that all the log messages are written correctly to the log file.
    for fileItem in os.listdir(sourceDirectory) :

        # For each SOURCE file, the name is extracted, and it is checked if it is a directory. If it is a directory, the script is called recursively for that directory. If it is not a directory, it has already been processed in the previous steps of the script, so it is skipped.
        sourceName = fileItem
        sourcePath = os.path.join(sourceDirectory, sourceName)

        # If the file is a directory, we call the script recursively for that directory. If it is not a directory, it has already been processed in the previous steps of the script, so it is skipped.
        if os.path.isdir(sourcePath) :

            with open(LOGFILE, 'a') as file :
            
                # The next directory is going to be processed
                #print(f"The directory {sourcePath} is going to be processed")
                print(f"\nThe directory {sourcePath} is going to be processed\n", file=file)

                # The path of the directory in the destination directory is constructed, and the script is called recursively for that directory. The environment variable is passed to indicate that it is a recursive execution, so that the confirmation of the destination directory is not requested again, and the statistics are not printed again, since they are only printed at the end of the script, and we want to print them only once at the end of the script, not for each recursive execution.
                targetPath = os.path.join(targetDirectory, sourceName)

                # Importante: Vacía el búfer antes de lanzar el hijo
                file.flush() 
                os.fsync(file.fileno())

            # We call the script recursively for the directory blocking the execution until it finishes, so that we can be sure that the synchronization of the directory is finished before continuing with the next directory, and we can be sure that the statistics are printed at the end of the script, and we do not have to worry about printing them for each recursive execution, which would complicate the script and make it less efficient. If we did this without blocking the execution, we would have to worry about printing the statistics for each recursive execution, which would complicate the script and make it less efficient.
            # The call to subprocess.run is done outside the with statement, so we can be sure that the log file is closed before we start the recursive execution of the script for the directories, since the recursive execution of the script for the directories will also write to the log file, and if we do not close the log file before starting the recursive execution of the script for the directories, we may have problems with concurrent access to the log file, which could cause errors or inconsistencies in the log file. By closing the log file before starting the recursive execution of the script for the directories, we can be sure that there are no problems with concurrent access to the log file, and we can be sure that all the log messages are written correctly to the log file.
            # and in a new environment with our custom brand name, so that we can check if the script is being executed recursively in the child execution, and we can skip the confirmation of the destination directory and the printing of the statistics in the child execution, since they are only printed at the end of the script, and we want to print them only once at the end of the script, not for each recursive execution.
            # Depending on whether the script is running as an executable (PyInstaller) or as a normal .py script, we call it with the appropriate arguments. If it is running as an executable, we call it with sys.executable, which is the path to the executable, and the source and target paths as arguments. If it is running as a normal .py script, we call it with sys.executable, which is the path to the Python interpreter, and sys.argv[0], which is the path to the script, and the source and target paths as arguments. In both cases, we pass the new environment with our custom brand name to indicate that it is a recursive execution, so that we can skip the confirmation of the destination directory and the printing of the statistics in the child execution.
            if getattr(sys, 'frozen', False):
                # It is running as an executable (PyInstaller)
                subprocess.run([sys.executable, sourcePath, targetPath], env=nuevo_env)
            else:
                # It's running as a normal .py script
                subprocess.run([sys.executable, sys.argv[0], sourcePath, targetPath], env=nuevo_env)


except Exception as error :
        # We print the error message; all exceptions have this field.
        print("Error detected : ", error.args[0], end='')
            
        # If the second argument contains an error code, we display it; otherwise, we display a message indicating the error.
        if len(error.args) > 1 and isinstance(error.args[1], int):
            print("  Error Code :", error.args[1])
        else :
            print("\nNo numeric error code was found in the exception, exited with -1")

        # We added error messages to the file
        with open(LOGFILE, 'a') as file :

            # Append errorText to file
            print("Error detected : ", error.args[0], end='', file=file)

            # If the second argument contains an error code, we use it to exit; otherwise, use -1
            if len(error.args) > 1 and isinstance(error.args[1], int):
                print("  Error Code :", error.args[1], file=file)
                sys.exit(error.args[1])
            else :
                print("\nNo numeric error code was found in the exception, exited with -1", file=file)
                sys.exit(-1)