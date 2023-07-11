from ctypes import *
import pathlib
import os

# path of the shared library
libfile = pathlib.Path(__file__).parent / "libvisualnlp.so"
nlplib = CDLL(str(libfile))

nlplib.NLP_ENGINE_create.argtypes = [c_char_p]
nlplib.NLP_ENGINE_create.restype = c_void_p

nlplib.NLP_ENGINE_delete.argtypes = [c_void_p]
nlplib.NLP_ENGINE_delete.restype = c_void_p

nlplib.NLP_ENGINE_analyze.argtypes = [c_void_p, c_char_p, c_char_p]
nlplib.NLP_ENGINE_analyze.restype = None

nlplib.delete_char_p.argtypes = [c_char_p]
nlplib.delete_char_p.restype = c_void_p


class NLP:
    def __init__(self, workingFolder : str = os.getcwd()) -> None:
        self.ptr = nlplib.NLP_ENGINE_create(workingFolder.encode())
    
    def analyze(self, analyzer : bytes, input : bytes):
        output: Array[c_char] = create_string_buffer(2000)
        nlplib.NLP_ENGINE_analyze(self.ptr, analyzer, input, output)
        result = output.value
        return result

        