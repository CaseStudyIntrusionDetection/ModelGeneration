from os import path

import numpy as np

from src.data.DataLoaderJSON import DataLoaderJSON
from src.data.MultiDataLoader import MultiLoaderJSON

class BalancedData():

    def __init__(self, dataset=None, proj_root=".", file_paths=[]):
        self.proj_root = proj_root
        file_collections = {
            "cms": [
                "cms_1_zap.json", "cms_2_zap.json", "cms_3_zap.json",
                "cms_1_selenium.json", "cms_2_selenium.json", "cms_3_selenium.json"
            ],
            "gms": [
                "gms_1_zap.json", "gms_2_zap.json",
                "gms_2_selenium.json", "gms_3_selenium.json"
            ]
        }

        if len(file_paths) > 0:
            self.files = file_paths
        else:
            try:
                self.files = file_collections[dataset]
            except KeyError:
                raise Exception(f"Did not find dataset '{dataset}' in specified collections.\nAvailable keys: {list(file_collections.keys())}")

    
    def load_data(self, common_path_prefix = path.join('data', "raw")):
        #path_to_data= path.join(self.proj_root, 'data')
        self.loaders = []
        for file in self.files:
            self.loaders.append(
                DataLoaderJSON(path.join(common_path_prefix, file), self.proj_root)
            )

        self.multi_loader = MultiLoaderJSON(self.loaders)
        self.multi_loader.load_wrapper()
        print(">> Loaded data. Now merging..")
        self.multi_loader.merge_loaded_data()
        print(">> Merging done.")


    def get_all_data(self):
        return self.multi_loader.all_data

    def get_all_data_df(self):
        return self.multi_loader.data_to_dataframe()
