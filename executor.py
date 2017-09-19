

from fit_beam_library import Find_and_Fit_Beam
import numpy as np

def execute_find_beam(file_beam_np):

    array = np.load(file_beam_np)
    original_array, cleaned_array, fwhm_x, fwhm_y, max_x, max_y, centered_x, centered_y, ellipse_cm, line_x_cm, line_y_cm = Find_and_Fit_Beam(array).return_all_values()
    print 'fwhm x: %i fwhm y: %i'%(fwhm_x,fwhm_y)
    print 'max_x: %i max_y: %i'%(max_x, max_y)
    print 'centered_x: %f, centered_y:%f'%(centered_x,centered_y)
    

execute_find_beam('strong_squared_beam.npy')
