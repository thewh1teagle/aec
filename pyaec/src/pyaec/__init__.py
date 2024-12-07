import ctypes
from ctypes import POINTER, c_size_t, c_int32, c_bool, c_int16
import platform
import os
import sys


def load_library():
    # Get the directory of the current file
    try:
        # Load the shared library based on the platform
        if platform.system() == "Windows":
            lib = ctypes.CDLL(os.path.join(sys.prefix, "libaec.dll"))
        elif platform.system() == "Linux":
            lib = ctypes.CDLL(os.path.join(sys.prefix, "libaec.so"))
        elif platform.system() == "Darwin":
            lib = ctypes.CDLL(os.path.join(sys.prefix, "libaec.dylib"))
        else:
            raise OSError("Unsupported platform")

        return lib
    except OSError as e:
        print(f"Error loading shared library: {e}")
        return None


# Load the shared library
lib = load_library()


# Define the Aec structure (opaque pointer)
class AecHandle(ctypes.Structure):
    pass


# Define argument and return types for the functions
lib.AecNew.argtypes = [c_size_t, c_int32, c_int32, c_bool]
lib.AecNew.restype = POINTER(AecHandle)

lib.AecCancelEcho.argtypes = [
    POINTER(AecHandle),
    POINTER(c_int16),
    POINTER(c_int16),
    POINTER(c_int16),
    c_size_t,
]
lib.AecCancelEcho.restype = None

lib.AecDestroy.argtypes = [POINTER(AecHandle)]
lib.AecDestroy.restype = None


# Python-friendly wrapper
class Aec:
    def __init__(self, frame_size, filter_length, sample_rate, enable_preprocess=True):
        self._aec = lib.AecNew(
            frame_size, filter_length, sample_rate, enable_preprocess
        )
        if not self._aec:
            raise RuntimeError("Failed to create AEC instance")

    def cancel_echo(self, rec_buffer, echo_buffer):
        if len(rec_buffer) != len(echo_buffer):
            raise ValueError("rec_buffer and echo_buffer must have the same length")

        frame_size = len(rec_buffer)
        out_buffer = (c_int16 * frame_size)()

        lib.AecCancelEcho(
            self._aec,
            (c_int16 * frame_size)(*rec_buffer),
            (c_int16 * frame_size)(*echo_buffer),
            out_buffer,
            frame_size,
        )
        return list(out_buffer)

    def __del__(self):
        if self._aec:
            lib.AecDestroy(self._aec)
            self._aec = None
