import os
import subprocess


def ejecutar(cmd, archivo):
    os.system(cmd)
    subprocess.run(cmd, shell=True)
    subprocess.check_output("convert " + archivo, shell=True)
