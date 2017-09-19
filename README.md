# Identify-X-ray-beam

e.g.

in python:

## deliver an array in numpy format (.npy)

from fit_beam_library import Find_and_Fit_Beam

original_array, cleaned_array, fwhm_x, fwhm_y, max_x, max_y, centered_x, centered_y, ellipse_cm, line_x_cm, line_y_cm = Find_and_Fit_Beam(array).return_all_values()

