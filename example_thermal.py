import source.direct_binding as optris
import cv2
import numpy as np

DLL_path = "../irDirectSDK/sdk/x64/libirimager.dll"
optris.load_DLL(DLL_path)

# USB connection initialisation
optris.usb_init('20112117.xml')

w, h = optris.get_thermal_image_size()
print('{} x {}'.format(w, h))
#print(optris.set_radiation_parameters(100.0,1000.0,0.0))

while True:
    # Get the thermal frame (numpy array)
    thermal_frame = optris.get_thermal_image(w, h)
    # Conversion to temperature values are to be performed as follows:
    # t = ((double)data[x] - 1000.0) / 10.0;
    processed_thermal_frame = (thermal_frame - 1000.0) / 10.0
    
    #greyscale_frame = np.array(255/120 * ( processed_thermal_frame + 20), dtype = np.uint8)
    print(f"max: {processed_thermal_frame.max()} | min: {processed_thermal_frame.min()}")
    if processed_thermal_frame.max() != processed_thermal_frame.min():
        greyscale_frame = np.array(255/(processed_thermal_frame.max() - processed_thermal_frame.min()) * ( processed_thermal_frame - processed_thermal_frame.min()), dtype = np.uint8)
        #im_color = cv2.applyColorMap(greyscale_frame, cv2.COLORMAP_RAINBOW)
        #im_color = cv2.applyColorMap(processed_thermal_frame, cv2.COLORMAP_RAINBOW)
        #greyscale_frame = processed_thermal_frame
        cv2.imshow('IR streaming', greyscale_frame)
        #cv2.imshow('IR streaming', im_color)
        #cv2.imshow('IR streaming', processed_thermal_frame)
        print(processed_thermal_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        #print(processed_thermal_frame)
        #print(processed_thermal_frame.max())
        #print(processed_thermal_frame.min())


optris.terminate()
