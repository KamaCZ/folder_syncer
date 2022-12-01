# veeam_syncer
Synchronizing a source folder with a replica folder


This program synchronizes a source folder with a replica folder in this way:
1) When the replica folder does not exist, it creates one, and copies all 
the files and subfolders from the source folder into the replica folder.
2) When a new file is created or changed in the source folder, it is copied into the replica folder 
including any of new subfolders created.
3) When a file is deleted from the source folder, then it is deleted from the replica folder as well.

Constraints of the program: 
1) The program will not copy into the replica folder any empty subfolders created in the source folder until a new file is saved into them
2) The program will not delete any empty subfolders from the replica folder, that had previously been deleted from the source folder

To run the program perform following:
1) clone the project:
git clone https://github.com/KamaCZ/folder_syncer.git

2) create a virtual environment:
python3 -m venv .venv

3) activate the virtual environment:
source .venv/bin/activate

4) install requirements.txt:
pip install -r requirements.txt

5) run the program from the terminal using command line arguments:
to see the help about command line arguments, run:
python3 sync.py -h

en example command to run the program using command line arguments:

python3 sync.py -s /Users/home/Desktop/source_folder -r /Users/home/Desktop/replica_folder -l /Users/home/Desktop/logs -t 60

The above command will:

sync the folder in this path: /Users/home/Desktop/source_folder with the folder located in this path: /Users/home/Desktop/replica_folder, 
the log file will be saved into this path: /Users/home/Desktop/logs, and the sync will be performed every 60 seconds. 


