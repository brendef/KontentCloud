import os
import shutil
import zipfile


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory. " + directory)


def zipFolder(pathToZip, folderToZip):
    with zipfile.ZipFile(pathToZip, "w") as zipf:
        for root, _, files in os.walk(folderToZip):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), folderToZip),
                )


def deleteFolder(folder):
    print("Deleting folder " + folder)
    try:
        shutil.rmtree(folder, ignore_errors=True)
    except OSError as error:
        print(f"Error: Deleting directory {folder}: {error}")
