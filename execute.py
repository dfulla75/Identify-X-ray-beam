

from fit_beam_library import Find_and_Fit_Beam
import numpy as np

def give_array(file_to_open, image):

    array_np = np.load(file_to_open)
    array = array_np[image]

    return array

i = 0
array = give_array('/home/p24user/dfm_tests/Controllator/image_processing/plotter_files/fit_beam/image_processing_sebastien/data_images/oh_mot09_measurement_6361_images_Tue_25_15h_46min_49sec_camera_6.npy', i)

example = '/home/p24user/dfm_tests/Controllator/image_processing/images_motors/mot28_measurement_56035_images_Tue_27_18h_33min_56sec_camera_4.npy' # very small squared beam -- well fitted

#example = '/home/p24user/dfm_tests/Controllator/image_processing/images_motors/mot28_measurement_56035_images_Tue_27_18h_33min_56sec_camera_4.npy' # very faint beam --- not well fitted

#
example = '/home/p24user/dfm_tests/Controllator/image_processing/images_motors/mot28_measurement_55875_images_Tue_27_18h_31min_30sec_camera_8.npy'# very faint beam --- not well fitted

#array = give_array(example,i)

a,b,c,d,e,f,g,d,x9,x10,x11 = Find_and_Fit_Beam(array).return_all_values()


print 'fwhm x: %i fwhm y: %i'%(c,d)
print 'max_x: %i max_y: %i'%(e, f)
print 'centered_x: %f, centered_y:%f'%(g,d)
#print 'line_x_cm: %i, line_y_cm: %i'%(x10,x11)
