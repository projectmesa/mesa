import glob
import os

file_list = glob.glob("**/*.pytemplate", recursive=True)

for file_path in file_list:
    # Check if the file is a regular file
    if not os.path.isfile(file_path):
        continue
    # Rename the file
    os.rename(file_path, file_path.replace(".pytemplate", ".py"))
