import source.direct_binding as optris
#import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import time

DLL_path = "../irDirectSDK/sdk/x64/libirimager.dll"
optris.load_DLL(DLL_path)

# USB connection initialisation
optris.usb_init('20112117.xml')

w, h = optris.get_thermal_image_size()
print('{} x {}'.format(w, h))
#print(optris.set_radiation_parameters(100.0,1000.0,0.0))

plt.ion()

fig, ax = plt.subplots()
ax.axis('off')
line = ax.imshow(np.random.rand(h,w), extent=[1,w,1,h], cmap='jet', aspect='equal')
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.05)
fig.colorbar(line, cax=cax)


while True:
    # Get the thermal frame (numpy array)
    thermal_frame = optris.get_thermal_image(w, h)
    # Conversion to temperature values are to be performed as follows:
    # t = ((double)data[x] - 1000.0) / 10.0;
    processed_thermal_frame = (thermal_frame - 1000.0) / 10.0
    
    
    #greyscale_frame = np.array(255/120 * ( processed_thermal_frame + 20), dtype = np.uint8)
    print(f"max: {processed_thermal_frame.max()} | min: {processed_thermal_frame.min()}")
    if processed_thermal_frame.max() != processed_thermal_frame.min():
        line.set_data(processed_thermal_frame)
        line.autoscale()
        #line.set_clim(vmin=processed_thermal_frame.min(), vmax=processed_thermal_frame.max())
        fig.canvas.draw()
        
        fig.canvas.flush_events()
        
plt.ioff()
optris.terminate()

#for i in range(50):
    #new_data = np.random.rand(h,w)
    
    #line.set_data(new_data)
    
    #fig.canvas.draw()
    
    #fig.canvas.flush_events()
    #time.sleep(0.1)


#optris.terminate()
