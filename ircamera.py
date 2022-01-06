import source.direct_binding as optris
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
#import cv2
import os
import yaml
from datetime import datetime
from time import time



class Camera:
    def __init__(self, config_file) -> None:
        assert isinstance(config_file, str)
        
        optris.usb_init(config_file)
        
        self._image_counter = 0
        self._format = "jpeg"
        self._sample_rate = 1.0


    def read_settings(self, name, setup_file):
        assert isinstance(setup_file, str)
        assert os.path.exists(setup_file)

        with open(setup_file) as file:
            settings = yaml.safe_load(file)[name]

        if "dir" in settings.keys():
            self.set_dir(settings["dir"])

        if "format" in settings.keys():
            self.set_format(settings["format"])
            
        if "emissivity" in settings.keys() and "transmissivity" in settings.keys() and "ambientTemperature" in settings.keys():
            self.set_radiation_parameters(settings["emissivity"], settings["transmissivity"], settings["ambientTemperature"])

        if "sample rate" in settings.keys():
            self._sample_rate = settings["sample rate"]
            assert isinstance(self._sample_rate, (int, float)) and self._sample_rate > 0.0
    
    def set_radiation_parameters(self, emissivity: float, transmissivity: float, ambientTemperature: float):
        res = optris.set_radiation_parameters(emissivity, transmissivity, ambientTemperature)
        #print(res)
    
    def set_dir(self, dir):
        assert isinstance(dir, str)

        self._dir = dir

        if not os.path.exists(self._dir):
            os.mkdir(self._dir)

    @property
    def dir(self):
        assert hasattr(self, "_dir")
        return self._dir

    def _save_img(self, **kwargs):
        assert hasattr(self, "_dir")

        img_name = None

        if "name" in kwargs.keys():
            img_name = kwargs["name"]
            assert isinstance(img_name, str)
        else:
            self._image_counter += 1

        if img_name is None:
            self._fig.savefig(
                f"{self._dir}/img_{str(self._image_counter).zfill(4)}.{self._format}",
                format=self._format,
                bbox_inches='tight', 
                pad_inches = 0
            )
        else:
            self._fig.savefig(
                f"{self._dir}/{img_name}",
                format=self._format,
                bbox_inches='tight', 
                pad_inches = 0
            )
    
    def _save_csv(self, **kwargs):
        assert hasattr(self, "_dir")
        
        img_name = None

        if "name" in kwargs.keys():
            img_name = kwargs["name"]
            assert isinstance(img_name, str)

        if img_name is None:
            np.savetxt(f"{self._dir}/img_{str(self._image_counter).zfill(4)}.csv",
                (self._thermal_frame - 1000.0) / 10.0, delimiter=';', fmt='%1.2f'
            )
        else:
            np.savetxt(f"{self._dir}/{img_name}.csv",
                (self._thermal_frame - 1000.0) / 10.0, delimiter=';', fmt='%1.2f'
            ) 

    def set_format(self, format):
        assert isinstance(format, str)
        assert format in ["tiff", "jpeg", "png"]

        self._format = format

    @property
    def format(self):
        return self._format

    def reset_image_counter(self):
        self._image_counter = 0

    def show(self, **kwargs):
        print("Commands are not working!!! Recording is starting immediately! To stop use Ctrl+C!")
        # print("Start/stop recording by pressing the 'r' key.")
        # print("Quit the recording by pressing the 'q' key.")

        if "use_colorbar" in kwargs.keys():
            use_colorbar = kwargs["use_colorbar"]
            assert isinstance(use_colorbar, bool)
        else:
            use_colorbar = False
        
        if "save_csv" in kwargs.keys():
            save_csv = kwargs["save_csv"]
            assert isinstance(save_csv, bool)
        else:
            save_csv = False

        if "sample_rate" in kwargs.keys():
            self._sample_rate = kwargs["sample_rate"]    

        assert isinstance(self._sample_rate, (int, float))
        assert self._sample_rate >= 0.0

        # is_recording = False
        starttime = -1
        
        w, h = optris.get_thermal_image_size()
        
        plt.ion()

        self._fig, self._ax = plt.subplots()
        self._ax.axis('off')
        self._line = self._ax.imshow(np.random.rand(h,w), extent=[1,w,1,h], cmap='jet', aspect='equal')
        
        if use_colorbar:
            divider = make_axes_locatable(self._ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            self._fig.colorbar(self._line, cax=cax)

        while True:
            # Get the thermal frame (numpy array)
            self._thermal_frame = optris.get_thermal_image(w, h)
            # Conversion to temperature values are to be performed as follows:
            # t = ((double)data[x] - 1000.0) / 10.0;
            processed_thermal_frame = (self._thermal_frame - 1000.0) / 10.0
            
            #print(f"max: {processed_thermal_frame.max()} | min: {processed_thermal_frame.min()}")
            if processed_thermal_frame.max() != processed_thermal_frame.min():
                self._line.set_data(processed_thermal_frame)
                self._line.autoscale()
                #line.set_clim(vmin=processed_thermal_frame.min(), vmax=processed_thermal_frame.max())
                self._fig.canvas.draw()
                
                if (time() - starttime) >= (1 / self._sample_rate):
                    self._save_img(**kwargs)
                    if save_csv:
                        self._save_csv(**kwargs)
                    starttime = time()
                self._fig.canvas.flush_events()
                
        plt.ioff()
        optris.terminate()
