import ctypes
import cv2
from typing import Tuple
import numpy as np
import sys

DEFAULT_WIN_PATH = "..//..//irDirectSDK//sdk//x64//libirimager.dll"
DEFAULT_LINUX_PATH = "/usr/lib/libirdirectsdk.so"
lib = None

# Function to load the DLL accordingly to the OS
def load_DLL(dll_path: str):
    global lib
    if (sys.platform == "linux"):
        path = dll_path if dll_path is not None else DEFAULT_LINUX_PATH
        lib = ctypes.CDLL(DEFAULT_LINUX_PATH)

    elif (sys.platform == "win32"):
        path = dll_path if dll_path is not None else DEFAULT_WIN_PATH
        lib = ctypes.CDLL(path)

def usb_init(xml_config: str, formats_def: str = None, log_file: str = None) -> int:
    return lib.evo_irimager_usb_init(xml_config.encode(), None if formats_def is None else formats_def.encode(), None if log_file is None else log_file.encode())

def get_thermal_image_size() -> Tuple[int, int]:
    width = ctypes.c_int()
    height = ctypes.c_int()
    _ = lib.evo_irimager_get_thermal_image_size(ctypes.byref(width), ctypes.byref(height))
    return width.value, height.value

def get_thermal_image(width: int, height: int) -> np.ndarray:
    w = ctypes.byref(ctypes.c_int(width))
    h = ctypes.byref(ctypes.c_int(height))
    thermalData = np.empty((height, width), dtype=np.uint16)
    thermalDataPointer = thermalData.ctypes.data_as(ctypes.POINTER(ctypes.c_ushort))
    _ = lib.evo_irimager_get_thermal_image(w, h, thermalDataPointer)
    return thermalData

def set_radiation_parameters(emissivity: float, transmissivity: float, ambientTemperature: float) -> int:
    return lib.evo_irimager_set_radiation_parameters(ctypes.c_double(emissivity), ctypes.c_double(transmissivity), ctypes.c_double(ambientTemperature))

def terminate() -> int:
    return lib.evo_irimager_terminate(None)

#################################################################################################################


DLL_path = "../irDirectSDK/sdk/x64/libirimager.dll"
load_DLL(DLL_path)

# USB connection initialisation
usb_init('20112117.xml') #'config_file_linux.xml')

w, h = get_thermal_image_size()
print('{} x {}'.format(w, h))

set_radiation_parameters(.001, 1.0, -10000.)
while True:
    # Get the thermal image (np.array)
    thermal_frame = get_thermal_image(w, h)
    
    processed_termal_frame = (thermal_frame - 1000.0) / 10.0
    print(processed_termal_frame.mean())
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

terminate()


