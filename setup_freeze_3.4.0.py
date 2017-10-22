from cx_Freeze import setup, Executable

 setup(
    name = "YProg Rastreio",
    version = "0.1",
    description = "Rastrear objetos nacionais",
    executables = [Executable("codigo_rastreio_correios,py")])
