import os.path
import sys

from cx_Freeze import setup, Executable

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

# dependencies that are automatically detected, but might need fine tuning
build_exe_options = {"packages": ["os", 'cx_Freeze'], "include_files": ['tcl86t.dll', 'tk86t.dll']}

base = None

if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Aleph_custom4",
      version='0.1',
      description='create table for importing empty records via custom04',
      executables=[Executable('run.py', base=N, requires=['pandas'])])

# setup(
#     name='Aleph_custom4',
#     version='0.1',
#     url='https://blog.nli.org.il/culture_and_art/',
#     license='NLI',
#     author='Yael Vardina Gherman',
#     author_email='Yael.VardinaGherman@nli.org.ol',
#     description='this script makes a table for custom04 in Aleph - creating new records with minimal data.',
#     executables=[Executable("run.py", base = base)],
#     options= ["build_exe": build_exe_options]
# )
