from ircamera import Camera

ircamera = Camera('20112117.xml')
ircamera.set_dir("./images")
ircamera.set_format("png")
ircamera.set_radiation_parameters(0.01, 1.0, -2000.0) # is not working
ircamera.show(use_colorbar=True, save_csv=True)
