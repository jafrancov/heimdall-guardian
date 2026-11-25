import pickle
import cPickle
import marshal
import shelve
import yaml
import jsonpickle
import dill


def cargar(request, ruta):
    a = pickle.loads(request.body)
    b = pickle.load(open(ruta, "rb"))
    c = cPickle.loads(request.body)
    d = marshal.loads(request.body)
    e = shelve.open(ruta)
    f = yaml.load(request.body)
    g = yaml.load(request.body, Loader=yaml.Loader)
    h = yaml.unsafe_load(request.body)
    i = jsonpickle.decode(request.body)
    j = dill.loads(request.body)
    return a, b, c, d, e, f, g, h, i, j
