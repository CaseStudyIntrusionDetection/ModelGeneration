from os import path
import random
from time import time
import json
from email.utils import formatdate


class DataFaker(object):

    def __init__(self, data_loader, proj_root):
        #self.path = path.join(proj_root, "data", "dummy", "csic")
        self.path = data_loader.path.replace("external", "dummy")
        self.data_loader = data_loader

    def create_fake_data(self):
        """Creates the fake data for the given data loader.
        """
        # 1. Load real data
        if not self.data_loader.data_loaded:
            self.data_loader.load_wrapper()

        # 2. Transform & save requests
        for key in self.data_loader.requests:
            our_format = self.requests_to_our_format(self.data_loader.requests[key])
            file_name = path.splitext(path.basename(self.data_loader.file_names[key]))[0] + ".json"
            file_path = path.join(self.path, file_name)
            with open(file_path, "w") as f:
                f.write(our_format)
            print(f"DataFaker: Writing to {file_path}")

    def requests_to_our_format(self, requests, indents = None):
        """Transforms a list of request objects into our specified JSON format.

        Args:
            requests ([Request]): List of HTTPRequest objects
            indents (int, optional): number of indent spaces in the json. Defaults to None.

        Returns:
            str: json string
        """
        objs = []
        for id, request in enumerate(requests):
            obj = {}
            # id         
            obj['id'] = id
            # timestamp
            obj['timestamp'] = int(time())
            # connection-id
            obj['connection-id'] = id
            # request
            obj['request'] = {
                "method": request.method,
                "uri": request.uri,
                "protocol": request.protocol,
                "body": request.body if request.body else ""
            }
            # header
            obj['header'] = request.headers

            # sender
            obj['sender'] = {
                "ip": "localhost"
            }
            # honeypot
            obj['honeypot'] = {
                "used-emulator": random.choice(['rfi', 'sqli', 'lfi', 'xss', 'cmd_exec', 'php_code_injection', 'php_object_injection', 'crlf']),
                "response-hash": "2F078FF4F34A3C1D59A3DD1EAC85E629C92800814BB442E81AA366849E59F0088B880AF3AB2E1FF1DFC2E5C15217044BEC27B61A15D259A7FCB413E5067AA5E8",
                "response-size": random.randint(1000,50000),
                "response-status-code" : random.choice([500,404,403,200,200,200,301]), 
                "response-header": {
                    "Server": random.choice(["nginx", "Apache"]),
                    "Date": formatdate(timeval=None, localtime=False, usegmt=True),
                    "Content-Type": "text/html; charset=utf-8",
                    "X-Powered-By": "PHP/7.4.11",
                    "Expires": formatdate(timeval=0, localtime=False, usegmt=True),
                    "Cache-Control": "no-store, no-cache, must-revalidate",
                    "Pragma": "no-cache"
                }
            }
            objs.append(obj)
        
        return json.dumps(objs, indent=indents)

