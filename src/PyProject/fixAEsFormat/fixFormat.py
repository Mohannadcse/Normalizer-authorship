import os
import shutil
import glob




AE_directory = "/home/adv/Downloads/log"  #the path where allAEs of the untargetted attack results are stored
formated_ds_path = "/home/adv/Downloads/formated_dataset" #the path where the formated dataset of AEs will be stored

def fix_format():
    if not os.path.isdir(formated_ds_path):
        os.mkdir(formated_ds_path) 
    for root, directories, filenames in os.walk(AE_directory):
        if directories:
            for subfolder in directories:
                if "False" in subfolder:
                    main_path = os.path.join(root,subfolder)
                    print(main_path)
                    for f in os.listdir(main_path):
                        if f == "logs":
                            shutil.rmtree(os.path.join(main_path,f))
                            print("remove logs")
                        author_path = os.path.join(main_path,f)
                        author_path_formatted = os.path.join(formated_ds_path,f)
                        if not os.path.isdir(author_path_formatted):
                            os.mkdir(author_path_formatted)
                        for file in glob.glob(author_path+'/*_'+ f +'.cpp'):
                            shutil.copy2(file,author_path_formatted)


def main():
    fix_format()

if __name__ == '__main__':
    main()