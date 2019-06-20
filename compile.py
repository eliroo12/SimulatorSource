from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from DNCgui import main
import pyximport
pyximport.install(setup_args={"script_args":["--compiler=mingw32"]}, reload_support=True)
ext_modules = [
    Extension("ability",  ["ability.py"]),
    Extension("action",  ["action.py"]),
	Extension("astmodule",  ["astmodule.py"]),
    Extension("buff",  ["buff.py"]),
	Extension("card",  ["card.py"]),
    Extension("DNCgui",  ["DNCgui.py"]),
	Extension("job",  ["job.py"]),
    Extension("scheduler",  ["scheduler.py"]),
	Extension("sim",  ["sim.py"]),
    Extension("simdictionary",["simdictionary.py"]),
	Extension("stats",  ["stats.py"]),
#   ... all your modules that need be compiled ...
]
setup(
    name = 'Dancer Simulation',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)

main()