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
import signal
import psutil
from pathlib import Path


# Function to handle the signals, it is called when a signal is received, and it is responsible for cleaning up the child processes and saving the logs before exiting. 
# The function takes three arguments: the signal number, the frame, and a boolean variable that indicates if the script is being executed recursively. 
# If the script is not being executed recursively, it means that we are in the parent execution of the script, and we need to clean up the child processes and save the logs before exiting. If the script is being executed recursively, it means that we are in a child execution of the script, and we do not need to clean up the child processes or save the logs, since we are already in a child execution of the script, and we can just exit without doing anything else.

def signal_handler(sig, frame, isRecursiveExecution, sourceDirectory):

    # Disables the default behavior of the SIGINT signal, so that it is not captured twice 
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # Variable to check if the script is being executed in an interactive terminal
    is_interactive = sys.stdin.isatty()

    # We print a message indicating that a signal has been received and that we are starting the cleanup of the child processes
    # We also print a message indicating that we are saving the logs and exiting
    # This way, we can provide useful information to the user about what is happening when a signal is received, and we can also keep a record of the signals received and the actions taken in the log file, which can be useful for debugging and for understanding the behavior of the script when it receives signals.
    os.write(1, bytes(f"\nSource Directory : {sourceDirectory} --> Signal {signal.Signals(sig).name} ({sig}) received : Starting the children's cleanup on the parent process and saving logs and exiting on each process...",'utf-8'))


    # If we are in the parent process...
    # Only for SIGTERM or others, since SIGINT is usually sent by the user pressing Ctrl+C and the processes are cleaned up from farest child to the parent automatically by this function once they receive the CTRL+C command, so we do not need to clean them up manually
    # Or SIGINT if we are not receiving a CTRL+C
    if not isRecursiveExecution and (sig != signal.SIGINT or ( sig == signal.SIGINT and not is_interactive )) :
    
        # This code block is responsible for cleaning up the child processes, it is executed when a signal is received, and it is responsible for terminating the child processes gracefully, and if they do not terminate within a certain time, it forces their termination. 
        # This way, we can be sure that all the child processes are terminated before exiting the script, and we can avoid leaving any orphan processes running in the background after the script has exited. 
        # This is important to prevent resource leaks and to ensure that the system is not left in an inconsistent state after the script has exited.
        try:
    
            # Geting the current process, which is the parent process of all the child processes that we want to clean up
            father_process = psutil.Process()

            # Geting all the child processes of the current process, which are the processes that we want to clean up
            children_processes = father_process.children(recursive=True)

            # We print a message indicating the pid number of child processes that we are going to clean up
            for child_process in children_processes:
                if child_process.is_alive() :
                    os.write(1, bytes(f"Ending child PID: {child_process.pid}",'utf-8'))
                    child_process.terminate() 

            # Waiting for the child processes to terminate gracefully, with a timeout of 3 seconds
            gone, alive = psutil.wait_procs(children_processes, timeout=3)

            # For any child process that is still alive after the timeout, we print a message indicating that we are forcing its closure
            for straggler in alive:
                os.write(1, bytes(f"Forcing closure of rebellious child : {straggler.pid}",'utf-8'))
                straggler.kill()

        # If the current process does not exist, which can happen if the signal is received after the parent process has already terminated, we catch the NoSuchProcess exception, and we just exit with the appropriate code
        except psutil.NoSuchProcess:
            code = 128 + sig
            os._exit(code)
    
    try :
            
        # We print the message in the log file indicating that we are saving the logs and exiting
        with open(LOGFILE, 'a') as file :
            file.write(f"\nSource Directory : {sourceDirectory} --> Signal {signal.Signals(sig).name} ({sig}) received : Starting the children's cleanup on the parent process and saving logs and exiting on each process...")

    # If any exception occurs while trying to save the logs, we catch it and print an error message indicating that an error was detected while trying to save the logs
    except Exception as error :
        
        # We print the error message; all exceptions have this field.
        os.write(1, bytes("Error detected : " + str(error.args[0]),'utf-8'))
            
        # If the second argument contains an error code, we display it; otherwise, we display a message indicating the error.
        if len(error.args) > 1 and isinstance(error.args[1], int):
            os.write(1, bytes("  Error Code :" + str(error.args[1]),'utf-8'))
        else :
            os.write(1, b"\nNo numeric error code was found in the exception, exited with -1",'utf-8')

    finally :

        # The parent and the child processes exit with the appropriate code, which is 128 + the signal number, since this is the standard way to indicate that a process was terminated by a signal, and it allows us to distinguish between normal exits and exits caused by signals, which can be useful for debugging and for understanding the behavior of the script when it receives signals.
        code = 128 + sig
        os._exit(code)

# From here the script's task is carried out
# All the code will be inside a try block, so that if any command fails, the error is handled eficiently
try :

    # We initialize the variable that will hold the new environment with our custom brand name, which is used to check if the script is being executed recursively. 
    nuevo_env = None

    # Our custom brand name to check if the script is being executed recursively, it is stored in an environment variable that we will check at the beginning of the script
    VAR_RECURSION = "QUICKFOLDERSYNCHRO_RECURSION"
    # Boolean variable to indicate if the script is being executed recursively, it is initialized to False and will be set to True if the environment variable is detected
    isRecursiveExecution = False

    # How we should open the log file, w for parent, a for children
    fileMode='w'

    # If the environment variable is not detected, it means that we are in the parent execution of the script, and we need to create a new environment with our custom brand name to pass it to the child executions of the script. 
    # If the environment variable is detected, it means that we are in a child execution of the script
    if not os.environ.get(VAR_RECURSION) == "1":
        # We created a copy of the current environment and added our branding.
        nuevo_env = os.environ.copy()
        nuevo_env[VAR_RECURSION] = "1"
    else :
        # If the environment variable is detected, it means that we are in a child execution of the script
        fileMode='a'
        # We set the boolean variable to indicate that we are in a recursive execution
        isRecursiveExecution = True

    # LOGFILE is the name of the file where the log will be stored, it is created in the current directory and overwritten if it already exists
    # Taking from the script name changing the extension to .log
    LOGFILE = str(Path(sys.argv[0]).with_suffix(".log"))

    #The LOGFILE file is opened for writing during execution
    with open(LOGFILE, fileMode) as file :

        # Wrong arguments...
        if not isRecursiveExecution and len(sys.argv) != 3 :
            errorCode = 1
            errorText = "Wrong arguments"
            raise Exception(errorText, errorCode)
        
        # The source and target directories are extracted from the command line arguments, and they are stored in variables for later use. 
        # These variables are used throughout the script to refer to the source and target directories, and they are also used in the log messages to indicate which directories are being processed. 
        # This way, we can keep track of the source and target directories throughout the script, and we can provide useful information to the user about which directories are being processed at each step of the synchronization process.
        sourceDirectory = sys.argv[1]
        targetDirectory = sys.argv[2]

        # Showing the source and target directories, both in the console and in the log file 
        #print("SOURCE Directory :", sourceDirectory)
        file.write("SOURCE Directory : " + sourceDirectory + "\n")
        #print("TARGET Directory :", targetDirectory)
        file.write("TARGET Directory : " + targetDirectory + "\n")

        # Setting the signal handler function, passing him whether we are in the father or in one of its child processes and the sourceDirectory managed by the process
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler(s, f, isRecursiveExecution, sourceDirectory))
        signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, isRecursiveExecution, sourceDirectory))
        
        # It is detected that we are in the father process
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
                # If the destination directory does not exist, we print a message indicating that it does not exist and that it is being created, both in the console and in the log file, and then we create the destination directory, since it is necessary for the synchronization process to continue, and it is better to create the destination directory if it does not exist than to raise an error and stop the synchronization process
                print(f"The destination directory {targetDirectory} does not exist, it is created")
                file.write(f"\nThe destination directory {targetDirectory} does not exist, it is created\n")
                os.mkdir(targetDirectory)
            else :
                # If the destination directory does not exist, we print an error message and raise an exception with an appropriate error code, since the synchronization process cannot continue if the destination directory does not exist, and it is important to provide useful information to the user about what went wrong, so that they can fix the problem and run the script again successfully.
                errorCode = 4
                errorText = f"The destination directory {targetDirectory} does not exist" 
                raise Exception(errorText, errorCode)
        
        #print(f"\nSEARCHING FOR FILES IN {sourceDirectory} :" )
        file.write(f"\nSEARCHING FOR FILES IN {sourceDirectory} : \n")

        # If there are no files in the source directory, we print a message and skip to the next step, which is to check the destination directory for files that do not exist in the source directory. 
        # Otherwise, we continue with the synchronization process. 
        if len(os.listdir(sourceDirectory)) == 0 :
            #print(f"There are no files in {sourceDirectory} :" )
            file.write(f"There are no files in {sourceDirectory} : \n")     
        else:
            # For each file item in source directory
            for fileItem in os.listdir(sourceDirectory) :

                # Incrementing the total number of files and directories found in the source directory, including directories, which will be processed later in the script. 
                # This variable is used for statistics at the end of the script.
                foundFilesAndDir += 1

                # For each SOURCE file, the name, size, and modification date are extracted.
                sourceName = fileItem
                sourcePath = os.path.join(sourceDirectory, sourceName)
                sourceFileSize = os.path.getsize(sourcePath)
                sourceFileModificationTime = os.path.getmtime(sourcePath)

                # Files with square brackets cause problems, so they are replaced with hyphens. also applies to directories, since they will be processed later in the script, and if they have square brackets, they will cause problems when trying to access them. 
                # This is done before processing the files, so we are sure that all the files and directories that we process do not have square brackets, and we do not have to worry about them later in the script. 
                # If we did this after processing the files, we would have to worry about files and directories with square brackets that we have already processed, which would complicate the script and make it less efficient.
                table = str.maketrans("[]", "--")
                sourceNameModified = sourceName.translate(table)
                if sourceName != sourceNameModified :
                    print(f"File {sourceName} contains square brackets, it is renamed to {sourceNameModified}")
                    file.write(f"File {sourceName} contains square brackets, it is renamed to {sourceNameModified}\n")
                    os.rename(sourcePath, os.path.join(sourceDirectory, sourceNameModified))
                    sourceName = sourceNameModified
                    sourcePath = os.path.join(sourceDirectory, sourceName)

                # The path of the file in the destination directory is constructed, and it is checked if it exists. 
                # If it exists, the number of files found in the destination directory is incremented, and its size and modification date are compared with those of the source file. 
                # If they are the same, it is not copied, and the number of files not copied is incremented. 
                # If they are different, it is copied, and the number of files copied is incremented. 
                # If it does not exist, it is copied, and the number of files copied is incremented.
                targetPath = os.path.join(targetDirectory, sourceName)

                # If the file is not a directory, otherswise it will be processed later in the script
                if not os.path.isdir(sourcePath) :

                    # Incrementing the number of files found in the source directory, excluding directories, this variable is used for statistics at the end of the script.
                    foundFiles += 1

                    # If the file exists in the destination directory, we check if it has the same size and modification date as the source file. 
                    # If it does, it is not copied. 
                    # If it does not, it is copied. 
                    # In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
                    if os.path.exists(targetPath) :   
                        # If the file exists in the destination directory...
                        targetFileSize = os.path.getsize(targetPath)
                        targetFileModificationTime = os.path.getmtime(targetPath)

                        # If the file exists in the destination directory and has the same size and modification date as the source file...
                        if sourceFileSize == targetFileSize and sourceFileModificationTime == targetFileModificationTime :
                            #print(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory with the same size and modification time, it is not copied")
                            file.write(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory with the same size and modification time, it is not copied\n")
                            notCopiedFoundFiles += 1
                        else :
                            # The file exists in the destination directory but has a different size or modification date...
                            print(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory but with different size or modification time, it is copied")
                            file.write(f"{sourceDirectory.upper()} : File {sourcePath} already exists in the destination directory but with different size or modification time, it is copied\n")
                            shutil.copy2(sourcePath, targetPath)
                            copiedFoundFiles += 1
                    else :
                        # The file does not exist in the destination directory, it is copied, and a message is printed indicating that it does not exist in the destination directory, so it is copied. 
                        print(f"{sourceDirectory.upper()} : File {sourcePath} does not exist in the destination directory, it is copied")
                        file.write(f"{sourceDirectory.upper()} : File {sourcePath} does not exist in the destination directory, it is copied\n")
                        shutil.copy2(sourcePath, targetPath)
                        copiedNotFoundFiles += 1
                else :
                    # Incrementing the number of directories found in the source directory, excluding files, this variable is used for statistics at the end of the script.
                    foundDirectories += 1

        # Printing the statistics for the source directory, including the total number of files and directories found in the source directory, the number of files found in the source directory, the number of files found in the source directory that already exist in the destination directory, the number of files found in the source directory that already exist in the destination directory but are not copied because they have the same size and modification date, and the number of files found in the source directory that are copied to the destination directory. 
        # These statistics are printed only in the log file.
        file.write(f"\nSTATISTICS FOR {sourceDirectory} : \n")
        file.write(f"Number of total items found in source directory: {foundFilesAndDir}\n")
        file.write(f"Number of files found in source directory: {foundFiles}\n")
        file.write(f"Number of directories found in source directory: {foundDirectories}\n")
        file.write(f"Number of source files found in target directory: {copiedFoundFiles + notCopiedFoundFiles}\n")
        file.write(f"Number of source files copied to target directory: {copiedFoundFiles + copiedNotFoundFiles}\n")
        file.write(f"Number of source files found in target not copied to target directory: {notCopiedFoundFiles}\n")
            
         
        # The destination is traversed to remove files that do not exist in the source.
        #print(f"\nSEARCHING FOR FILES IN {targetDirectory} : " )
        file.write(f"\nSEARCHING FOR FILES IN {targetDirectory} : \n")

        # If there are no files in the destination directory, we print a message and skip to the end of the script, which is to print the statistics. 
        # Otherwise, we continue with the synchronization process.
        if len(os.listdir(targetDirectory)) == 0 :
            #print(f"There are no files in {targetDirectory} : " )
            file.write(f"There are no files in {targetDirectory} : \n")  
        else:
            # For each file item in the destination directory, the name is extracted, and it is checked if it exists in the source directory. 
            # If it does not exist, it is deleted. 
            # If it exists, it is not deleted. 
            # In both cases, a message is printed indicating what happened, and the corresponding statistics are updated.
            for fileItem in os.listdir(targetDirectory) :

                # Printing a message indicating that the file is being processed, both in the console and in the log file.
                #print(f"Processing {targetDirectory.upper()} : {fileItem}")
                file.write(f"Processing {targetDirectory.upper()} : {fileItem}\n")

                # Incrementing the total number of files and directories found in the destination directory, including directories, which will be processed later in the script. 
                # This variable is used for statistics at the end of the script.
                targetFoundFilesAndDir += 1

                # Changing variables for statistics
                if not os.path.isdir(targetPath) :
                    targetFoundFiles += 1
                else :
                    targetFoundDirectories += 1

                # For each TARGET file, the name is extracted
                targetName = fileItem
                targetPath = os.path.join(targetDirectory, targetName)

                # The path of the file in the source directory is constructed...
                sourcePath = os.path.join(sourceDirectory, targetName)

                # If the file does not exist in the source directory...
                if not os.path.exists(sourcePath) :

                    # Incrementing the number of files and directories deleted from the destination directory, this variable is used for statistics at the end of the script.
                    targetDeletedFilesAndDir += 1

                    # If the file is not a directory, otherwise it will be processed later in the script, it is checked if it exists in the source directory.
                    if not os.path.isdir(targetPath) :

                        # Incrementing the number of files found in the destination directory but not in the source directory, this variable is used for statistics at the end of the script.
                        targetFoundFilesNotInSource += 1

                        # Printing a message indicating that the file exists in the destination directory but does not exist in the source directory, so it is deleted, both in the console and in the log file.
                        print(f"{targetDirectory.upper()} : File {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted")
                        file.write(f"{targetDirectory.upper()} : File {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted\n")

                        # Deleting the file in the destination directory, since it does not exist in the source directory
                        os.remove(targetPath)

                    else :

                        # Incrementing the number of directories found in the destination directory but not in the source directory, this variable is used for statistics at the end of the script.
                        targetFoundDirNotInSource += 1

                        # Printing a message indicating that the directory exists in the destination directory but does not exist in the source directory, so it is deleted
                        print(f"Directory {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted")
                        file.write(f"{targetDirectory.upper()} : Directory {targetPath} exists in the destination directory but does not exist in the source directory, it is deleted\n")

                        # Deleting the directory in the destination directory
                        shutil.rmtree(targetPath)

                        

        # Printing the statistics for the destination directory, including the total number of files and directories found in the destination directory, the number of files found in the destination directory, the number of files found in the destination directory but not in the source directory, the number of directories found in the destination directory but not in the source directory, and the number of files and directories deleted from the destination directory. 
        # These statistics are printed only in the log file.
        file.write(f"\nSTATISTICS FOR {targetDirectory} : \n")
        file.write(f"Total files and directories in target directory: {targetFoundFilesAndDir}\n")
        file.write(f"Files found in target directory: {targetFoundFiles}\n")
        file.write(f"Directories found in target directory: {targetFoundDirectories}\n")
        file.write(f"Files found in target directory but not in source directory then deleted : {targetFoundFilesNotInSource}\n")
        file.write(f"Directories found in target directory but not in source directory then deleted : {targetFoundDirNotInSource}\n")
        file.write(f"Files and directories deleted from source directory: {targetDeletedFilesAndDir}\n")


    # We trace the origin in search of directories
    # The directory exists in Destination, already verified
    # This is done after processing the files, so we are sure that the directories in the destination directory that do not exist in the source directory have already been deleted, so we can be sure that all the directories that exist in the destination directory also exist in the source directory, and we can process them without worrying about deleting them later. 
    # If we did this before processing the files, we would have to worry about deleting directories that do not exist in the source directory but exist in the destination directory, which would complicate the script and make it less efficient.
    # The recursive execution of the script for the directories is done at the end of the script, so we have already processed all the files in the source and destination directories
    # It has been taken outside the with statement because we want to be sure that the log file is closed before we start the recursive execution of the script for the directories, since the recursive execution of the script for the directories will also write to the log file, and if we do not close the log file before starting the recursive execution of the script for the directories, we may have problems with concurrent access to the log file, which could cause errors or inconsistencies in the log file. 
    # By closing the log file before starting the recursive execution of the script for the directories, we can be sure that there are no problems with concurrent access to the log file, and we can be sure that all the log messages are written correctly to the log file.
    for fileItem in os.listdir(sourceDirectory) :

        # For each SOURCE file, the name is extracted
        sourceName = fileItem
        sourcePath = os.path.join(sourceDirectory, sourceName)

        # If the file is a directory, we call the script recursively for that directory. 
        # If it is not a directory, it has already been processed in the previous steps of the script, so it is skipped.
        if os.path.isdir(sourcePath) :

            with open(LOGFILE, 'a') as file :
    
                # The next directory is going to be processed
                #print(f"The directory {sourcePath} is going to be processed")
                file.write(f"\nThe directory {sourcePath} is going to be processed\n")

                # The path of the directory in the destination directory is constructed
                targetPath = os.path.join(targetDirectory, sourceName)

                # Important: Empty the buffer before launching the child
                file.flush() 
                os.fsync(file.fileno())

            # We call the script recursively for the directory blocking the execution until it finishes, so that we can be sure that the synchronization of the directory is finished before continuing with the next directory, and we can be sure that the statistics are printed at the end of the script, and we do not have to worry about printing them for each recursive execution, which would complicate the script and make it less efficient. 
            # If we did this without blocking the execution, we would have to worry about printing the statistics for each recursive execution, which would complicate the script and make it less efficient.
            # The call to subprocess.run is done outside the with statement, so we can be sure that the log file is closed before we start the recursive execution of the script for the directories, since the recursive execution of the script for the directories will also write to the log file, and if we do not close the log file before starting the recursive execution of the script for the directories, we may have problems with concurrent access to the log file, which could cause errors or inconsistencies in the log file. 
            # By closing the log file before starting the recursive execution of the script for the directories, we can be sure that there are no problems with concurrent access to the log file, and we can be sure that all the log messages are written correctly to the log file.
            # And in a new environment with our custom brand name, so that we can check if the script is being executed recursively in the child execution, and we can skip the confirmation of the destination directory and the printing of the statistics in the child execution, since they are only printed at the end of the script, and we want to print them only once at the end of the script, not for each recursive execution.
            # Depending on whether the script is running as an executable (PyInstaller) or as a normal .py script, we call it with the appropriate arguments. 
            # If it is running as an executable, we call it with sys.executable, which is the path to the executable, and the source and target paths as arguments. 
            # If it is running as a normal .py script, we call it with sys.executable, which is the path to the Python interpreter, and sys.argv[0], which is the path to the script, and the source and target paths as arguments. 
            # In both cases, we pass the new environment with our custom brand name to indicate that it is a recursive execution, so that we can skip the confirmation of the destination directory and the printing of the statistics in the child execution.
            if getattr(sys, 'frozen', False):
                # It is running as an executable (PyInstaller)
                subprocess.run([sys.executable, sourcePath, targetPath], env=nuevo_env, stderr=subprocess.DEVNULL)
            elif "__compiled__" in globals() :
                # It is running as an executable (Niutka)
                subprocess.run([sys.argv[0], sourcePath, targetPath], env=nuevo_env, stderr=subprocess.DEVNULL)
            else:
                # It's running as a normal .py script
                subprocess.run([sys.executable, sys.argv[0], sourcePath, targetPath], env=nuevo_env, stderr=subprocess.DEVNULL)


except Exception as error :

    # We print the error message; all exceptions have this field.
    print("Error detected : ", error.args[0], end='')
            
    # If the second argument contains an error code, we display it; otherwise, we display a message indicating the error.
    if len(error.args) > 1 and isinstance(error.args[1], int):
        print("  Error Code :", error.args[1])
    else :
        print("\nNo numeric error code was found in the exception, exited with -1")

    try :
        # We added error messages to the file
        with open(LOGFILE, 'a') as file :

            # Append errorText to file
            file.write(f"Error detected : {error.args[0]}")

            # If the second argument contains an error code, we use it to exit; otherwise, use -1
            if len(error.args) > 1 and isinstance(error.args[1], int):
                file.write(f"  Error Code : {error.args[1]}\n")
                sys.exit(error.args[1])
            else :
                file.write("\nNo numeric error code was found in the exception, exited with -1\n")
                sys.exit(-1)

    except Exception as error :

        # If it cannot print in the file
        # We print the error message
        print("Error detected : ", error.args[0], end='')
            
        # If the second argument contains an error code, we display it; otherwise, we display a message indicating the error.
        # And finally we exit
        if len(error.args) > 1 and isinstance(error.args[1], int):
            print("  Error Code :", error.args[1])
            sys.exit(error.args[1])
        else :
            print("\nNo numeric error code was found in the exception, exited with -1")
            sys.exit(-1)