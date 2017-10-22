from distutils.core import setup
import py2exe
#setup(console=['codigo_rastreio_correios.py'])
setup(windows=['codigo_rastreio_correios.py'],
      data_files=[("icones", ["icones/Site.ico"])],
      name="YProg Rastreio",
      version=1.0,
      author="Israel Gomes",
      fullname="YPRastreio",
      author_email="modelador.criar3d@gmail.com",
      description="Rastrear objetos nacionais",
      platforms="windows")

