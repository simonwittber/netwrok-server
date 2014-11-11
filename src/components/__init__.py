import os
import glob
import sys



modules = {}

def load_all_components():
    for m in glob.glob(os.path.dirname(__file__)+"/*.py"):
        if not os.path.basename(m).startswith('_'):
            name = os.path.basename(m)[:-3]
            print("Importing: ", name)
            modules[name] = __import__("components.%s"%name, fromlist=[name])



def load(ns, cs):
    return getattr(modules[ns], cs)

