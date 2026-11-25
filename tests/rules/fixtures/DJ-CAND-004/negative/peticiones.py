import requests
import urllib.request


def traer():
    requests.get("https://api.example.com/estado")
    requests.post("https://api.example.com/eventos", data={})
    urllib.request.urlopen("https://api.example.com/datos")
