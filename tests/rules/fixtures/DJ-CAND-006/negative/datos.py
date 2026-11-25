import json
import pickle
import yaml


def cargar(request):
    a = yaml.safe_load(request.body)
    b = yaml.load(request.body, Loader=yaml.SafeLoader)
    c = yaml.load(request.body, Loader=yaml.CSafeLoader)
    d = yaml.load(request.body, yaml.SafeLoader)
    e = json.loads(request.body)
    f = pickle.loads(b"\x80\x04N.")
    g = yaml.load("clave: valor")
    return a, b, c, d, e, f, g
