from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as build_ext_orig
import os
import subprocess
import glob
import time
import shutil
from pathlib import Path

class CTypesExtension(Extension):
    pass


class build_ext(build_ext_orig):
    def build_extension(self, ext):
        self._ctypes = isinstance(ext, CTypesExtension)
        return super().build_extension(ext)
    
    def get_export_symbols(self, ext):
        if self._ctypes:
            return ext.export_symbols
        return super().get_export_symbols(ext)

    def get_ext_filename(self, ext_name):
        if ext_name == 'visualnlp': # The ext_name defined below
            return ext_name + ".so"
        return super().get_ext_filename(ext_name)

    def run(self):
        # Ensure the build directory exists
        if not os.path.exists('./nlp-engine/build'):
            os.mkdir('./nlp-engine/build')
        if not os.path.exists('./nlp-engine/lib'):
            os.mkdir('./nlp-engine/lib')
        os.chdir('./nlp-engine/lib')

        # Compile the C library
        subprocess.check_call(['/usr/bin/cmake', '--no-warn-unused-cli','-DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE','-DCMAKE_BUILD_TYPE:STRING=Debug','-DCMAKE_C_COMPILER:FILEPATH=/usr/bin/gcc','-DCMAKE_CXX_COMPILER:FILEPATH=/usr/bin/g++','-S../','-B../build','-G','Ninja'])
        subprocess.check_call(['/usr/bin/cmake', '--build','../build','--config','Debug','--target','all'])
        # Change back to the root directory
        os.chdir('../..')
        path = Path(self.get_ext_fullpath('visualnlp'))
        
        shutil.copy('./nlp-engine/lib/libvisualnlp.so', os.path.join(path.parent.absolute(), 'pynlp'))
        # return super().run()


setup(
    name='visual-nlp',
    version='0.1',
    setup_requires=['wheel'],
    py_modules=['pynlp.nlp'],
    ext_modules=[
        # Having some issue compiling using this, so this just copies the library compiled using cmake
        CTypesExtension(
            name="visualnlp",
            sources=["nlp-engine/python-c-binding/wrapper.cpp"],
            include_dirs = ['nlp-engine/include/Api', 'nlp-engine/cs/include', 'nlp-engine/include/Api/lite' ],
            library_dirs = ['nlp-engine/lib'],
            extra_compile_args = ['-std=c++17'],
            libraries=[':libprim.a',':libkbm.a',':libconsh.a',':libwords.a',':liblite.a'],
            extra_objects=['-Wl,-Bstatic'],
            extra_link_args=['-Wl,-Bdynamic', '-licuuc', '-licui18n', '-licuio']
        ),
    ],
    cmdclass={"build_ext": build_ext},
)