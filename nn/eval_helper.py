
import sys
from os import path

import os
SINGLE_CORE = True
if SINGLE_CORE:
    os.environ['TF_NUM_INTEROP_THREADS'] = '1'
    os.environ['TF_NUM_INTRAOP_THREADS'] = '1'
    print("########## SINGLE CORE MODE ##############")

import json

import src.models.NNWrapper as NNW

if __name__=='__main__':
    if len(sys.argv) == 1:
        print("Call this script via")
        print("# python eval_helper.py <json-settings-file> <project-root-path>")
    else:
        json_path = sys.argv[1]
        proj_root = sys.argv[2]
        print("> Loading setting from "+json_path)
        with open(json_path, "r") as f:
            setting = json.load(f)
            print(json.dumps(setting, indent=2))

        setting_name = path.splitext(path.basename(json_path))[0]
        
        NNW.eval_wrapper(setting_name=setting_name, 
                        proj_root=proj_root, 
                        train_files=setting['training_data'],
                        test_files=setting['test_data'],
                        label_column=setting['general_setup']['target_label'],
                        text_vars=setting['general_setup']['text_vars'], 
                        categ_vars=setting['general_setup']['categ_vars'], 
                        num_vars=setting['general_setup']['num_vars'],
                        bin_vars=setting['general_setup']['bin_vars'],
                        nn_settings=setting['nn_setup'])

