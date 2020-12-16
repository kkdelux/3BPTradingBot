# QoL utilities for Application

# API calling helper functions
from urllib.request import Request, urlopen
import json

def get_json_parsed_data(url):
    """
    Receive the content of ``url``, parse it as JSON and return the object.
    Parameters
    ----------
    url: str
    Returns
    -------
    dict
    """
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def get_json_parsed_data_with_headers(url, headers):
    """
    Receive the content of ``url`` with passed ``headers``, parse it as JSON and return the object.
    Parameters
    ----------
    url: str
    headers: dict
    Returns
    -------
    dict
    """
    req = Request(url, headers=headers)
    data = urlopen(req).read()
    return json.loads(data)
