#!/usr/bin/env python3 

import sys
import os
import shutil
import subprocess


# All the code will be inside a try block, so that if any command fails, the error is displayed and the process finishes
try :

    # LOGFILE is the name of the file where the log will be stored, it is created in the current directory and overwritten if it already exists
    LOGFILE = "QuickFolderSynchro.log"

    #The QuickFolderSynchro file is opened for writing during execution
    with open(LOGFILE, 'w') as file :

        # Wrong arguments...
        if len(sys.argv) != 3 :
            errorCode = 1
            errorText = "Wrong arguments"
            raise Exception(errorText, errorCode)
        
        # The number of arguments is ok, getting the info
        sourceDirectory = sys.argv[1]
        targetDirectory = sys.argv[2]

        # Showing the source and target directories, both in the console and in the log file 
        print("SOURCE Directory :", sourceDirectory)
        print("SOURCE Directory :", sourceDirectory, file=file)
        print("TARGET Directory :", targetDirectory)
        print("TARGET Directory :", targetDirectory, file=file)
        
        # Our custom brand name to check if the script is being executed recursively, it is stored in an environment variable that we will check at the beginning of the script
        VAR_RECURSION = "QUICKFOLDERSYNCHRO_RECURSION"
        # Boolean variable to indicate if the script is being executed recursively, it is initialized to False and will be set to True if the environment variable is detected
        isRecursiveExecution = False

        # It is detected that this is not a recursive execution
        if not os.environ.get(VAR_RECURSION) == "1":
            # We created a copy of the current environment and added our branding.
            nuevo_env = os.environ.copy()
            nuevo_env[VAR_RECURSION] = "1"
        
            # We request confirmation that the destination directory is correct.
            resp = input(f"Confirm that {targetDirectory} is correct? Answer Yes to continue, No to cancel : ");
            while resp != "Yes" :
                if resp == "No" : 
                    errorCode = 2
                    errorText = "Aborted by the user does not confirm that the destination directory is correct."
                    raise Exception(errorText, errorCode)
                resp = input(f"Confirm that {targetDirectory} is correct? Answer Yes to continue, No to cancel : ")
        else :
             isRecursiveExecution = True

        # Variables for folder task statistics
        foundFilesAndDir=0
        foundFiles=0
        copiedFoundFiles=0
        notCopiedFoundFiles=0
        copiedNotFoundFiles=0

        targetFoundFilesAndDir=0
        targetFoundFiles=0
        targetFoundFilesNotInSource=0
        targetFoundDirNotInSource=0
        targetDeletedFilesAndDir=0

        # The source directory does not exist.
        if not os.path.exists(sourceDirectory) :
            errorCode = 3
            errorText = f"The source directory {sourceDirectory} does not exist" 
            raise Exception(errorText, errorCode)
        
        # The destination directory does not exist.
        if not os.path.exists(targetDirectory) :
            if isRecursiveExecution :
                print(f"The destination directory {targetDirectory} does not exist, it is created")
                print(f"The destination directory {targetDirectory} does not exist, it is created", file=file)
                os.mkdir(targetDirectory)
            else :
                errorCode = 4
                errorText = f"The destination directory {targetDirectory} does not exist" 
                raise Exception(errorText, errorCode)
        
        print(f"SEARCHING FOR FILES IN {sourceDirectory} : " )
        print(f"SEARCHING FOR FILES IN {sourceDirectory} : ", file=file )

        # If there are no files in the source directory, we print a message and skip to the next step, which is to check the destination directory for files that do not exist in the source directory. Otherwise, we continue with the synchronization process. 
        if len(os.listdir(sourceDirectory)) == 0 :
            print(f"There are no files in {sourceDirectory} : " )
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

                # Files with square brackets cause problems, so they are replaced with hyphens.
                tabla = str.maketrans("[]", "--")
                sourceNameModified = sourceName.translate(tabla)
                if sourceName != sourceNameModified :
                    print(f"File {sourceName} contains square brackets, it is renamed to {sourceNameModified}")
                    print(f"File {sourceName} contains square brackets, it is renamed to {sourceNameModified}", file=file)
                    os.rename(sourcePath, os.path.join(sourceDirectory, sourceNameModified))
                    sourceName = sourceNameModified
                    sourcePath = os.path.join(sourceDirectory, sourceName)

                # If the file is not a directory, otherswise it will be processed later in the script, it is checked if it exists in the destination directory. If it does not exist, it is copied. If it exists, its size and modification date are compared with those of the source file. If they are the same, it is not copied. If they are different, it is copied.
                if not os.path.isdir(sourcePath) :
                    # Incrementing the number of files found in the source directory, excluding directories, this variable is used for statistics at the end of the script.
                    foundFiles += 1

                    # The path of the file in the destination directory is constructed, and it is checked if it exists. If it exists, the number of files found in the destination directory is incremented, and its size and modification date are compared with those of the source file. If they are the same, it is not copied, and the number of files not copied is incremented. If they are different, it is copied, and the number of files copied is incremented. If it does not exist, it is copied, and the number of files copied is incremented.
                    targetPath = os.path.join(targetDirectory, sourceName)

                    # If the file exists in the destination directory, we check if it has the same size and modification date as the source file. If it does, it is not copied. If it does not, it is copied. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                    if os.path.exists(targetPath) :
                        targetFoundFiles += 1                        
                        targetFileSize = os.path.getsize(targetPath)
                        targetFileModificationTime = os.path.getmtime(targetPath)

                        # If the file exists in the destination directory and has the same size and modification date as the source file, it is not copied, and a message is printed indicating that it already exists with the same size and modification date. If it exists but has a different size or modification date, it is copied, and a message is printed indicating that it already exists but with different size or modification date, so it is copied. In both cases, the corresponding statistics are updated.
                        if sourceFileSize == targetFileSize and sourceFileModificationTime == targetFileModificationTime :
                            #print(f"File {sourceName} already exists in the destination directory with the same size and modification time, it is not copied")
                            print(f"File {sourceName} already exists in the destination directory with the same size and modification time, it is not copied", file=file)
                            notCopiedFoundFiles += 1
                        else :
                            print(f"File {sourceName} already exists in the destination directory but with different size or modification time, it is copied")
                            print(f"File {sourceName} already exists in the destination directory but with different size or modification time, it is copied", file=file)
                            subprocess.run(["cp", sourcePath, targetPath])
                            copiedFoundFiles += 1
                    else :
                        print(f"File {sourceName} does not exist in the destination directory, it is copied")
                        print(f"File {sourceName} does not exist in the destination directory, it is copied", file=file)
                        shutil.copy2(sourcePath, targetPath)
                        copiedNotFoundFiles += 1

            # Printing the statistics for the source directory, including the total number of files and directories found in the source directory, the number of files found in the source directory, the number of files found in the source directory that already exist in the destination directory, the number of files found in the source directory that already exist in the destination directory but are not copied because they have the same size and modification date, and the number of files found in the source directory that are copied to the destination directory. These statistics are printed both in the console and in the log file.
            print(f"STATISTICS FOR {sourceDirectory} : ", file=file)
            print(f"Total files in source directory: {foundFilesAndDir}", file=file)
            print(f"Files found in source directory: {foundFiles}", file=file)
            print(f"Files already in target directory: {targetFoundFiles}", file=file)
            print(f"Files copied to target directory: {copiedFoundFiles + copiedNotFoundFiles}", file=file)
            print(f"Files not copied to target directory: {notCopiedFoundFiles}", file=file)
         
            # The destination is traversed to remove files that do not exist in the source.
            print(f"SEARCHING FOR FILES IN {targetDirectory} : " )
            print(f"SEARCHING FOR FILES IN {targetDirectory} : ", file=file )

            # If there are no files in the destination directory, we print a message and skip to the end of the script, which is to print the statistics. Otherwise, we continue with the synchronization process.
            if len(os.listdir(targetDirectory)) == 0 :
                print(f"There are no files in {targetDirectory} : " )
                print(f"There are no files in {targetDirectory} : ", file=file )  
            else:

                # For each file item in the destination directory, the name is extracted, and it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                for fileItem in os.listdir(targetDirectory) :
                    # Incrementing the total number of files and directories found in the destination directory, including directories, which will be processed later in the script. This variable is used for statistics at the end of the script.
                    targetFoundFilesAndDir += 1

                    # For each TARGET file, the name is extracted, and it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                    targetName = fileItem
                    targetPath = os.path.join(targetDirectory, targetName)

                    # If the file is not a directory, otherwise it will be processed later in the script, it is checked if it exists in the source directory. If it does not exist, it is deleted. If it exists, it is not deleted. In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                    if not os.path.isdir(targetPath) :
                        # Incrementing the number of files found in the destination directory, excluding directories, this variable is used for statistics at the end of the script.
                        targetFoundFiles += 1

                        # The path of the file in the source directory is constructed, and it is checked if it exists. If it does not exist, it is deleted, and a message is printed indicating that it exists in the destination directory but not in the source directory, so it is deleted. If it exists, it is not deleted, and a message is printed indicating that it exists in both directories, so it is not deleted. In both cases, the corresponding statistics are updated.
                        sourcePath = os.path.join(sourceDirectory, targetName)

                        # If the file exists in the destination directory but does not exist in the source directory, it is deleted, and a message is printed indicating that it exists in the destination directory but not in the source directory, so it is deleted. If it exists in both directories, it is not deleted, and a message is printed indicating that it exists in both directories, so it is not deleted. In both cases, the corresponding statistics are updated.
                        if not os.path.exists(sourcePath) :
                            print(f"File {targetName} exists in the destination directory but does not exist in the source directory, it is deleted")
                            print(f"File {targetName} exists in the destination directory but does not exist in the source directory, it is deleted", file=file)

                            # deleting the file in the destination directory, since it does not exist in the source directory, and incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                            os.remove(targetPath)

                            # Incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                            targetDeletedFilesAndDir += 1
                            targetFoundFilesNotInSource += 1
                    else :
                        # It is a directory, so we check if it exists in the source directory. If it does not exist, it is deleted, and a message is printed indicating that it exists in the destination directory but not in the source directory, so it is deleted. If it exists, it is not deleted, and a message is printed indicating that it exists in both directories, so it is not deleted. In both cases, the corresponding statistics are updated.
                        sourcePath = os.path.join(sourceDirectory, targetName)

                        # If the directory exists in the destination directory but does not exist in the source directory, it is deleted, and a message is printed indicating that it exists in the destination directory but not in the source directory, so it is deleted. If it exists in both directories, it is not deleted, and a message is printed indicating that it exists in both directories, so it is not deleted. In both cases, the corresponding statistics are updated.
                        if not os.path.exists(sourcePath) :
                            print(f"Directory {targetName} exists in the destination directory but does not exist in the source directory, it is deleted")
                            print(f"Directory {targetName} exists in the destination directory but does not exist in the source directory, it is deleted", file=file)

                            # deleting the directory in the destination directory, since it does not exist in the source directory, and incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                            shutil.rmtree(targetPath)

                            # Incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.   
                            targetDeletedFilesAndDir += 1
                            targetFoundDirNotInSource += 1

            # Printing the statistics for the destination directory, including the total number of files and directories found in the destination directory, the number of files found in the destination directory, the number of files found in the destination directory but not in the source directory, the number of directories found in the destination directory but not in the source directory, and the number of files and directories deleted from the destination directory. These statistics are printed both in the console and in the log file.
            print(f"STATISTICS FOR {targetDirectory} : ", file=file)
            print(f"Total files in target directory: {targetFoundFilesAndDir}", file=file)
            print(f"Files found in target directory: {targetFoundFiles}", file=file)
            print(f"Files found in target directory but not in source directory: {targetFoundFilesNotInSource}", file=file)
            print(f"Directories found in target directory but not in source directory: {targetFoundDirNotInSource}", file=file)
            print(f"Files and directories deleted from target directory: {targetDeletedFilesAndDir}", file=file)

            # We trace the origin in search of directories
            # The directory exists in Destination, already verified
            # This is done after processing the files, so we are sure that the directories in the destination directory that do not exist in the source directory have already been deleted, so we can be sure that all the directories that exist in the destination directory also exist in the source directory, and we can process them without worrying about deleting them later. If we did this before processing the files, we would have to worry about deleting directories that do not exist in the source directory but exist in the destination directory, which would complicate the script and make it less efficient.
            # The recursive execution of the script for the directories is done at the end of the script, so we have already processed all the files in the source and destination directories, and we can be sure that all the directories that exist in the destination directory also exist in the source directory, so we can process them without worrying about deleting them later. If we did this before processing the files, we would have to worry about deleting directories that do not exist in the source directory but exist in the destination directory, which would complicate the script and make it less efficient.           
            for fileItem in os.listdir(sourceDirectory) :
                # For each SOURCE file, the name is extracted, and it is checked if it is a directory. If it is a directory, the script is called recursively for that directory. If it is not a directory, it has already been processed in the previous steps of the script, so it is skipped.
                sourceName = fileItem
                sourcePath = os.path.join(sourceDirectory, sourceName)

                # If the file is a directory, we call the script recursively for that directory. If it is not a directory, it has already been processed in the previous steps of the script, so it is skipped.
                if os.path.isdir(sourcePath) :

                    # The path of the directory in the destination directory is constructed, and the script is called recursively for that directory. The environment variable is passed to indicate that it is a recursive execution, so that the confirmation of the destination directory is not requested again, and the statistics are not printed again, since they are only printed at the end of the script, and we want to print them only once at the end of the script, not for each recursive execution.
                    targetPath = os.path.join(targetDirectory, sourceName)
                    
                    # We call the script recursively for the directory
                    subprocess.run([sys.executable, __file__, sourcePath, targetPath], env=nuevo_env)

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