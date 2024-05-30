import os
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
