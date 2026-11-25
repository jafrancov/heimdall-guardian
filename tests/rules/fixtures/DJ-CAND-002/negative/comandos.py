import os
import subprocess


def ejecutar(archivo):
    os.system("uptime")
    subprocess.run(["convert", archivo])
    subprocess.check_output("df -h", shell=True)
