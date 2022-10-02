# from re import search

import Configuration as Config
from evasion.Transformers.BasicTransformer import BasicTransformer
from evasion.Transformers.TemplateTransformers.VarFctNameTransformer import VarFctNameTransformer
from evasion.Author import Author
from evasion.AttackMode import AttackMode
import classification.utils_load_learnsetup
import evasion.utils_attack_workflow as uaw
from evasion.BBAttackInstance import BBAttackInstance
import os
import sys
import shutil
import csv
import pandas
import typing

seed = 10
original_transformations = Config.transformercsvfile
dataset = Config.datasetpath
transformersdir = Config.transformersdir
resultsdir = None
normalized_transformeroptions = None
testfilein = None
required_trans = all

# settings for template transformations
source_author_str = ""
PROBLEM_ID = 0


def load_transformations(transformations, author, author_dir, author_dir_orig, PROBLEM_ID) -> typing.List['TransformerBase']:
    # load
    df = pandas.read_csv(normalized_transformeroptions)
    df = df.fillna("")

    # Reads the possible (compiled) clang-based transformers that we can call
    transformerdict = {}
    for root, directories, filenames in os.walk(transformersdir):
        for filename in filenames:
            if filename.endswith("transformer"):
                # check
                if filename in transformerdict:
                    raise Exception(
                        "Two transformers (maybe in different dir's) with same name?")
                transformerdict[filename] = root

    # convert to python objects
    transformerobjects = []
    for index, row in df.iterrows():
        if row['Python-class'] == "base":
            transformerobjects.append(BasicTransformer(transformer=row['transformer'],
                                                       option=row['option'], uniqueid=row['uniqueid'],
                                                       fillcmdlineoption=row['fillcmdlineoptions'],
                                                       transformersdir=transformerdict[row['transformer']]))
        elif row['Python-class'].endswith("/VarFctNameTransformer"):
            testlearnsetup: classification.LearnSetups.LearnSetup.LearnSetup = classification.utils_load_learnsetup.load_learnsetup(
                learnmodelspath=Config.learnmodelspath,
                feature_method=Config.feature_method,
                learn_method=Config.learn_method,
                problem_id=PROBLEM_ID,
                threshold_sel=Config.threshold_sel)
            sourceauthor = Author(author=author,
                                  learnsetup=testlearnsetup)
            tr: VarFctNameTransformer = VarFctNameTransformer(transformer=row['transformer'],
                                                              option=row['option'],
                                                              uniqueid=row['uniqueid'],
                                                              fillcmdlineoption=row['fillcmdlineoptions'],
                                                              transformersdir=transformerdict[row['transformer']],
                                                              sourceauthor=sourceauthor,
                                                              targetauthor=sourceauthor,
                                                              attack_mode=AttackMode.DODGING,
                                                              attackdir=author_dir_orig,
                                                              logger="/home/adv/Downloads/RobustAuthorshipAttribution/data/dataset_2017/logger.txt",
                                                              includeinfopath=os.path.join(Config.codeinfodir,
                                                                                           row['Specific-Arguments']))

            transformerobjects.append(tr)

    return transformerobjects


def pre_transformation(transformer_dir, source_file_of_interest, author, authiid):
    testfilein = os.path.join(transformer_dir, "A-small-practice.in")
    testfileout = os.path.join(transformer_dir, "A-small-practice.out")

    reduced_testfile: bool = uaw.check_if_author_needs_reduced_testfile(authiid=authiid,
                                                                        author=author,
                                                                        call_instructions_csv_path=Config.call_instructions_csv_path)

    uaw.copytestfile(testfilesdir=Config.testfilesdir, authiid=authiid,
                     targettestfile=testfilein, reduced=reduced_testfile)

    pre_ifofstream = uaw.ifofstreampreprocesser(source_file=source_file_of_interest,
                                                inputstreampath=testfilein,
                                                outputstreampath=testfileout,  # os.path.basename
                                                ifopreppath=Config.ifostreampreppath, flags=Config.flag_list)

    # Create the A-small-practice.out file.
    source_file_exe = uaw.compileclang(
        source_file=source_file_of_interest, compilerflags=Config.compilerflags_list)
    uaw.executecontestfile(source_file_executable=source_file_exe, testfilein=testfilein,
                           testfileout=testfileout, ifofstream=pre_ifofstream)
    os.remove(source_file_exe)

    # Compute the hash of the output file. We will check that output is not changed by a transformation
    originaloutputhash = uaw.computeHash(source_file=testfileout)
    os.remove(testfileout)

    return originaloutputhash


def applied_trans(my_list, trans):   
    index = 0
    print("\t", end= " ")
    for items in my_list:
        if items == 1:
            print(trans[index].uniqueid, end= " >> ")
        index += 1
    print()

def run_normalized_transformations_single_file(src_file_path):
    filepath, filename = os.path.split(src_file_path)
    base_file_name_no_extension = os.path.splitext(filename)[0]
    norm_file_path = os.path.join(filepath, "normalized_" + base_file_name_no_extension)
    if os.path.exists(norm_file_path):
        shutil.rmtree(norm_file_path)

    print("create tmp dir for file: " + base_file_name_no_extension)
    os.mkdir(norm_file_path)
    print("start performing the transformations for: " + filename)
    author = "test"
    authiid = filename
    tmp_transform_dir = norm_file_path
    original_source_file = tmp_transform_dir + "/" + base_file_name_no_extension + "_original" + ".cpp"
    shutil.copyfile(src_file_path, original_source_file)
    author_dir = filepath
    author_dir_orig = ""
    normalized_trans, tranfromation_results = run_transformers(
                    original_source_file, base_file_name_no_extension, tmp_transform_dir, author_dir, author_dir_orig,
                    author, authiid, PROBLEM_ID)
    print("total normalized_trans = ", len(normalized_trans))
    print("# of applied trans= ", tranfromation_results.count(1))
    print("List of applied trans: ")
    applied_trans(tranfromation_results, normalized_trans)


def run_normalized_transformations(original_ds, normalized_ds):
    for root, directories, _ in os.walk(original_ds):
        for directory in directories:
            print("create tmp dir")
            os.mkdir(os.path.join(normalized_ds, directory))
            author_dir = os.path.join(normalized_ds, directory)
            author_dir_orig = os.path.join(original_ds, directory)
            for filename in os.listdir(os.path.join(root, directory)):
                print("create tmp dir for file: " + filename)
                src_file_path = os.path.join(root, directory, filename)
                source_file_forattack_splitext = os.path.splitext(filename)
                base_file_name_no_extension = source_file_forattack_splitext[0]
                tmp_transform_dir = os.path.join(
                    normalized_ds, directory, base_file_name_no_extension)
                os.mkdir(tmp_transform_dir)
                original_source_file = tmp_transform_dir + "/" + \
                    base_file_name_no_extension + "_original" + \
                    source_file_forattack_splitext[1]
                shutil.copyfile(src_file_path, original_source_file)
                print("perform transformations for: " + original_source_file)
                author = directory
                problem_ID_split = base_file_name_no_extension.split("_")
                PROBLEM_ID = problem_ID_split[0] + "_" + problem_ID_split[1]
                authiid = filename
                run_transformers(
                    original_source_file, base_file_name_no_extension, tmp_transform_dir, author_dir, author_dir_orig,
                    author, authiid, PROBLEM_ID)


def verify_after_trans(trans, transformer_dir, source_file_of_interest, author, authiid, file, source_file_modified, file_base_name, counter):
    print("Start Transforemr Verification: " + trans.uniqueid)
    try:
        # pre-transformation
        print("\tPre-trans...")
        originaloutputhash = pre_transformation(
            transformer_dir, source_file_of_interest, author, authiid)

        # Clang-Format:
        source_file_format = uaw.do_clang_format(
            source_file=source_file_modified)

        testfilein = os.path.join(
            transformer_dir, "A-small-practice.in")
        testfileout_test = os.path.join(os.path.dirname(
            source_file_format), "A-small-practice_transformation.out")
        ifofstream = uaw.ifofstreampreprocesser(source_file=source_file_format,
                                                inputstreampath=testfilein,
                                                outputstreampath=testfileout_test,
                                                ifopreppath=Config.ifostreampreppath, flags=Config.flag_list)

        source_file_format_exe = uaw.compileclang(
            source_file=source_file_format, compilerflags=Config.compilerflags_list)

        print("\tPost-trans...")
        uaw.executecontestfile(source_file_executable=source_file_format_exe, testfilein=testfilein,
                            testfileout=testfileout_test, ifofstream=ifofstream)

        transformedhash = uaw.computeHash(
            source_file=testfileout_test)
        if transformedhash != originaloutputhash:
            raise Exception("Output file has changed!!")

        trans_flag = 1
        meta_file = transformer_dir + "/" + \
            file_base_name + "_meta" + str(counter) + ".cpp"
        shutil.copyfile(source_file_modified, meta_file)
        file = meta_file

    except Exception as e:
        err = "FailedTransformer"
        print("FailedTransformer")
        os.remove(source_file_modified)
        source_file_format_exe = None
        trans_flag = 0

    finally:
        print("Finally block")
        os.remove(source_file_format)
        if source_file_format_exe is not None and os.path.exists(source_file_format_exe):
            os.remove(source_file_format_exe)
    
    return trans_flag, file


def run_transformers(file, file_base_name, transformer_dir, author_dir, author_dir_orig, author, authiid, PROBLEM_ID):
    tranfromation_results = [[]]
    tranfromation_results_single_cpp = []
    count_transformer_results = {}
    transformers = load_transformations(
        normalized_transformeroptions, author, author_dir, author_dir_orig, PROBLEM_ID)

    counter = 0
    for trans in transformers:
        res = []
        trans_flag = 0
        source_file_modified = file + trans.uniqueid + "_after_t.cpp"
        source_file_of_interest = file

        _, err = trans.dotransformercall(
            file, source_file_modified, seed=seed)

        if err is not None:
            print(trans.uniqueid + " " + err)
            os.remove(source_file_modified)
        else:
            if Config.verify == 1:
                print()
                trans_flag, file = verify_after_trans(trans, transformer_dir, source_file_of_interest, author, authiid, file, source_file_modified, file_base_name, counter)
            else:
                print("No Transformer verification: " + trans.uniqueid)
                trans_flag = 1
                meta_file = transformer_dir + "/" + \
                    file_base_name + "_meta" + str(counter) + ".cpp"
                shutil.copyfile(source_file_modified, meta_file)
                file = meta_file

        counter += 1

        res.append(os.path.basename(source_file_of_interest))
        res.append(trans.uniqueid)
        res.append(trans_flag)
        if Config.single == 1:
            tranfromation_results_single_cpp.append(trans_flag)
        res.append(err)

        tranfromation_results.append(res)

    # preparing final results and clean temp files/directories
    print("Move the last transformed to main dir: ")
    normalized_file = author_dir + "/normalized_" + file_base_name + ".cpp"
    shutil.copyfile(file, normalized_file)

    # check if single file
    if Config.single == 1:
        print("Please check the final normalized CPP at: ", normalized_file)
        return transformers, tranfromation_results_single_cpp

    print("Remove trans dir: " + transformer_dir)
    shutil.rmtree(transformer_dir)

    df = pandas.DataFrame(
        tranfromation_results, columns=['FileName', 'Transformer', 'Applied', 'Msg'])

    count_trans = []
    count_trans.append(str(len(df[df['Applied'] == 0])))
    count_trans.append(str(len(df[df['Applied'] == 1])))

    count_transformer_results[os.path.basename(
        source_file_of_interest)] = count_trans

    # if file does not exist write header
    if not os.path.isfile('tranfromation_results.csv'):
        df.to_csv('tranfromation_results.csv', index=False, header=True)
    else:  # else it exists so append without writing the header
        df.to_csv('tranfromation_results.csv',
                  index=False, mode='a', header=False)

    with open('count_results.csv', 'a') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in count_transformer_results.items():
            writer.writerow([key, ','.join(value)])
    csv_file.close()


def main():
    run_normalized_transformations(dataset, resultsdir)


if __name__ == '__main__':    
    # i can add this content later to handle applying various normalized trnaformations
    n = len(sys.argv)
    if n == 2:
        print("Selected Transformation Category: " + sys.argv[1])
        if sys.argv[1] == "API":
            normalized_transformeroptions = Config.normalizedtransformercsvfile_APITrans
            resultsdir = Config.normalizedresultspath_APITrans
        elif sys.argv[1] == "Control":
            normalized_transformeroptions = Config.normalizedtransformercsvfile_ControlTrans
            resultsdir = Config.normalizedresultspath_ControlTrans
        elif sys.argv[1] == "Misc":
            normalized_transformeroptions = Config.normalizedtransformercsvfile_MiscTrans
            resultsdir = Config.normalizedresultspath_MiscTrans
        elif sys.argv[1] == "Declaration":
            normalized_transformeroptions = Config.normalizedtransformercsvfile_DeclarationTrans
            resultsdir = Config.normalizedresultspath_DeclarationTrans
        elif sys.argv[1] == "Template":
            normalized_transformeroptions = Config.normalizedtransformercsvfile_TempTrans
            resultsdir = Config.normalizedresultspath_TempTrans
    else:
        resultsdir = Config.normalizedresultspath_AllTrans
        normalized_transformeroptions = Config.normalizedtransformercsvfile_AllTrans

    # for testing
    resultsdir = "/nobackup/code-imitator-normalizer/data/testing_dataset/normalized_results_AllTrans"
    dataset = "/nobackup/code-imitator-normalizer/data/testing_dataset/dataset"
    normalized_transformeroptions = Config.normalizedtransformercsvfile_AllTrans
    if os.path.exists("/nobackup/code-imitator-normalizer/src/PyProject/tranfromation_results.csv"):
        os.remove(
            "/nobackup/code-imitator-normalizer/src/PyProject/tranfromation_results.csv")
    if os.path.exists("/nobackup/code-imitator-normalizer/src/PyProject/count_results.csv"):
        os.remove(
            "/nobackup/code-imitator-normalizer/src/PyProject/count_results.csv")
    if os.path.exists(resultsdir):
        shutil.rmtree(resultsdir)
    ####
    if Config.single == 1:
        run_normalized_transformations_single_file(sys.argv[1])
    else:
        os.mkdir(resultsdir)
        main()
    # run_normalized_transformations_single_file("/nobackup/code-imitator-normalizer/data/testing_dataset/testing_single_file/3264486_5654742835396608_yosss.cpp")
