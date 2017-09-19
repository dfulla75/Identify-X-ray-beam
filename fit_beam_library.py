'''
daniel.fulla.marsa@desy.de
'''





import sys, math
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from matplotlib.patches import Ellipse



class Find_Beam(object):

    '''
    - given an array without spikes and with the presence of a beam:
    - returns location of the beam, peak intensity, fwhm x and y

    '''

    def __init__(self,array):

        self.array = array
        self.max_x, self.max_y, self.array_shape, self.peak_intensity = self.give_max_array()
        self.horizontal_line, self.vertical_line = self.max_cross_lines()
        # improve with asymmetry of beam
        self.fwhm_x = self.calculate_fwhm(self.horizontal_line, self.max_y) # attention horizontal and y !
        self.fwhm_y = self.calculate_fwhm(self.vertical_line, self.max_x)
        
    def give_max_array(self):

        '''
        - finds and returns the maximum of the array and the coordinates
        - the array comes from a numpy file
        
        '''
        
        self.peak_intensity = self.array.max()
        coordinates = np.argwhere(self.array.max() == self.array)
        self.max_x = coordinates[0][0] # coordinates x maximum
        self.max_y = coordinates[0][1] # coordinates y maximum
        self.array_shape = self.array.shape

        return self.max_x, self.max_y, self.array_shape, self.peak_intensity


    def max_cross_lines(self):
                        
            horizontal_line = self.array[self.max_x][:]
            vertical_line = self.array[:, self.max_y] # numpy expression 

            return horizontal_line, vertical_line

    

    def calculate_fwhm(self, line_cross_section, coordinates_max):

            '''
            - given one line cross section (x or y) and the coordintes of the max (x or y) measures the fwhm 

            '''
            
            half_value = (self.peak_intensity/2)
            
            array_left = line_cross_section[:coordinates_max]
            array_right = line_cross_section[coordinates_max:]
            
            average_line_cross_section = np.average(line_cross_section)
            ratio_peak_average_line = self.peak_intensity/average_line_cross_section
            
            closest_left =  min(array_left, key=lambda x:abs(x-half_value))
            closest_right =  min(array_right, key=lambda x:abs(x-half_value))
            index_fwhm_left = np.where(array_left == closest_left)[0]
            index_fwhm_right = np.where(array_right == closest_right)[0]

            left_pixel = len(array_left) - index_fwhm_left + 1 # check this one
            right_pixel = index_fwhm_right

            if len(left_pixel) > 1:
        
                #print 'ERROR: many pixels with the same half maximum. Assuming the closes one'
                left_pixel = left_pixel[0]

            if len(right_pixel) > 1:
        
                #print 'ERROR, many pixels with the same value of half maximum, assuming the closest one'
                right_pixel = right_pixel[-1]

            size_fwhm = (left_pixel) + right_pixel

            if ratio_peak_average_line < 5:  ######################### Attention, arbitrary threshold for very weak beams ##########:
                if size_fwhm > 40:
                    size_fwhm = 40 ### fixing fwhm to 20
                    print 'could not calculate fwhm. Assuming value 20'
            

            #if left_pixel != right_pixel:
                #print 'asymmetric: left site: %i right site: %i'%(left_pixel, right_pixel)

            return int(size_fwhm)

    def main(self):

        'this returns all needed parameters'

        return self.fwhm_x, self.fwhm_y, self.max_x, self.max_y


class Remove_Spikes(object):

    '''
    - given an array
    - Identify presence of spikes
    - Remove spikes
    - Deliver a cleaned array without spikes

    '''

    def __init__(self, array):

        self.surrounding_threshold = 0.65 # 65%
        self.average_max = self.average_surrounding_max(array)
        # typically spikes have less than 20% (0.2) surrounding. typical maximums about 80% (0.8). What about saturation ?
        if self.average_max < self.surrounding_threshold:
            
            self.array = self.remove_spikes(array)
        else:
            self.array = array

    def info_array(self, array):
        
        peak_intensity = array.max()
        coordinates = np.argwhere(array.max() == array)
        max_x = coordinates[0][0]
        max_y = coordinates[0][1]
        array_shape = array.shape

        return peak_intensity, coordinates, max_x, max_y, array_shape 

    def average_surrounding_max(self, array):

        peak_intensity, coordinates, max_x, max_y, array_shape = self.info_array(array)

        # discrimitate if max is located in end of image

        if array_shape[0]-1 != max_x:
            
            right_pixel = array[max_x+1][max_y]/float(array[max_x][max_y])

        if array_shape[0]-1 == max_x:
            # does this mean that max is at the edge?
            print 'CHECK if max is at edge'
            right_pixel = array[max_x][max_y]/float(array[max_x][max_y])

        left_pixel  = array[max_x-1][max_y]/float(array[max_x][max_y])

        if array_shape[1]-1 != max_y:
    
            upper_pixel =  array[max_x][max_y + 1]/float(array[max_x][max_y])
        
        if array_shape[1]-1 == max_y:
        
            upper_pixel =  array[max_x][max_y]/float(array[max_x][max_y])
            print 'Maximum upper pixel hit the border of array'
    
        lower_pixel =  array[max_x][max_y - 1]/float(array[max_x][max_y])
        average_surrounding = (right_pixel + left_pixel + upper_pixel + lower_pixel)/4

        return average_surrounding


    def remove_spikes(self, array):

        
        average_surrounding = self.average_surrounding_max(array)
        while average_surrounding < self.surrounding_threshold:

            average_surrounding = self.average_surrounding_max(array)
            peak_intensity, coordinates, max_x, max_y, array_shape = self.info_array(array)

            #print array[max_x][max_y]
            array[max_x][max_y] = 0

        return array

    def new_array(self):

        return self.array


class Fit_Beam(object):

    '''
    - given a cleaned array (without spikes) and the coordinates of the maximum:
    - it centers the position according to the center of masses

    '''

    def __init__(self, array, fwhm_x, fwhm_y, max_x, max_y):

        self.array = array
        self.max_x = max_x
        self.max_y = max_y

        self.size_x = fwhm_x
        self.size_y = fwhm_y
        
        self.centered_x, self.centered_y = self.center_mass_calculation()
        self.ellipse_cm, self.line_x_cm, self.line_y_cm = self.elipse_with_center_mass()
        self.plot_array_fit()

    def center_mass_calculation(self):

        '''
        - It calculates the center of mass in a region close to the main beam
        
        '''

        ROI_2 = self.array[self.max_x-1*self.size_y:self.max_x+1*self.size_y,self.max_y-1*self.size_x:self.max_y+1*self.size_x]
        CM_ROI = ndimage.measurements.center_of_mass(ROI_2)
    
        x_change = self.max_x - self.size_y
        y_change = self.max_y - self.size_x
    
        centered_x = CM_ROI[0] + x_change
        centered_y = CM_ROI[1] + y_change

        return centered_x, centered_y

    def elipse_with_center_mass(self):

        '''
        - Produces an Ellipse to represent the beam at the image
        '''

        ellipse_cm = Ellipse(xy=(self.centered_y,self.centered_x), width = self.size_x, height = self.size_y, edgecolor='r', fc='None', lw=2)
        line_x_cm = plt.Line2D((self.centered_y-self.size_x/2, self.centered_y+self.size_x/2),(self.centered_x,self.centered_x))
        line_y_cm = plt.Line2D((self.centered_y,self.centered_y),(self.centered_x-self.size_y/2, self.centered_x+self.size_y/2))

        return ellipse_cm, line_x_cm, line_y_cm


    def plot_array_fit(self):
        
        ax = plt.gca()
        ax.add_patch(self.ellipse_cm)
        plt.imshow(self.array)
        ax.add_line(self.line_x_cm)
        ax.add_line(self.line_y_cm)
        plt.show()

    def main(self):

        return self.centered_x, self.centered_y, self.ellipse_cm, self.line_x_cm, self.line_y_cm

class No_Beam(object):

    '''
    - given an array identifies the absence beam
    - returns beams if finds beam
    - returns no_beam if finds no beam

    '''

    def __init__(self,array):

        self.array = array
        self.threshold_std = 5
        self.size_box_x = 20
        self.size_box_y = 20
        

        

    def beam_or_not(self):

        '''
        - needs array, size of array and size of mask
        - 
        '''
        array = self.array
        
        x_size = array.shape[0]
        y_size = array.shape[1]
        
        x_box = self.size_box_x
        y_box = self.size_box_y
        
        number_box_x = int(math.modf(x_size/x_box)[1])
        number_box_y = int(math.modf(y_size/y_box)[1])

        lista = []

        for y in range(number_box_y):
    
            for x in range(number_box_x):
            
                lista.append(np.average(array[x*x_box:x_box + x*x_box, y*y_box :y_box + y*y_box])) 

        average = np.average(lista)
        std = np.std(lista)
        threshold = average + self.threshold_std*std
        max_lista = max(lista)

        #plt.plot(lista)
        #plt.show()

        if max_lista > threshold:

            return 'beam'

        if max_lista <= threshold:

            return 'no_beam'


class Find_and_Fit_Beam(object):

    '''
    - This executes the actual procedure of finding and fitting the beam
    - 

    '''

    def __init__(self, array):
        
        self.array = array

    def return_all_values(self):

        beam = No_Beam(self.array).beam_or_not()

        if beam == 'beam':
        
            original_array = self.array
            cleaned_array = Remove_Spikes(original_array).new_array()
            fwhm_x, fwhm_y, max_x, max_y = Find_Beam(cleaned_array).main()
            centered_x, centered_y, ellipse_cm, line_x_cm, line_y_cm = Fit_Beam(cleaned_array, fwhm_x, fwhm_y, max_x, max_y).main()

            return original_array, cleaned_array, fwhm_x, fwhm_y, max_x, max_y, centered_x, centered_y, ellipse_cm, line_x_cm, line_y_cm

        if beam == 'no_beam':

            return 'No beam found'
                


if __name__ == '__main__':

    if len(sys.argv) == 2:

        Find_and_Fit_Beam(sys.argv[1]).return_all_values()

        
