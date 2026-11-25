import requests
import urllib.request


def traer(url, host):
    requests.get(url)
    requests.post("https://" + host + "/datos", data={})
    urllib.request.urlopen(url)
