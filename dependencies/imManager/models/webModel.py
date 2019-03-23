import requests


class WebModel:

    def __init__(self):
        pass

    @staticmethod
    def get_request(url, get_content=False,  params={}):
        r = requests.get(url=url, params=params)
        if get_content:
            return r.content
        else:
            return r
