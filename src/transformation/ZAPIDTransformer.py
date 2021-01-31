from os import path
import pandas as pd

class ZAPIDTransformer():
    """A helper class to lookup information based on a `X-ZAP-SCAN-ID`.
    Information taken from table at https://www.zaproxy.org/docs/alerts/.
    """
    def __init__(self, proj_root):
        self.proj_root = proj_root
        file_path = path.join(proj_root, "references", "ZAP_ids.csv")
        self.df = pd.read_csv(file_path, sep=";", index_col="Id")

    def id_to_rule(self, id):
        """Looks up an ID and returns the corresponding Rule string.
        If Id cannot be found, returns `unknown id( id )`

        Args:
            id (str/int): ZAP Id to be looked up

        Returns:
            str: Rule String
        """
        id = str(id)
        df = self.df

        try:
            return df.at[id, 'Alert']
        except KeyError:
            return f"unknown id ({id})"
    
    def lookup_id(self, id):
        """Looks up a ZAP-ID and returns a dictionary with all information.
        In case the ID is not found, an dictionary of format `{'Alert': 'unknown id (123)', 'Id': '123'}` is returned.

        Args:
            id (int/str): ZAP id to be looked up

        Returns:
            dict: information on said Id
        """
        id = str(id)
        df = self.df
        try:
            d = dict(df.loc[id])
        except KeyError:
            d = {'Alert': f'unknown id ({id})'}
        d['Id'] = id
        return d