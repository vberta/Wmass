import ROOT
import math
import sys
import copy
import numpy as np
import numpy.random as ran

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from template_parameters import params_test, pdf_test , coefficients_test

class MixData:

    def __init__(self, input_dir='../data/', output_dir='../data/'):
        print "Initialize MixData"
        self.input_dir = input_dir
        self.output_dir = output_dir
        return

    def add_shapes(self, params, symmetrise=False, make_templates=False):

        # these are the available shapes (all generated for y=0.00)
        self.input_shapes_pt = params['params_W']['pt']

        # these are the shapes to be merged
        self.output_shapes_pt = params['params_template']['pt']
        self.output_shapes_y  = params['params_template']['y']

        # these are the parameters to be varied when making templates
        self.output_shapes_A0  = params['params_template']['A0']
        self.output_shapes_A1  = params['params_template']['A1']
        self.output_shapes_A2  = params['params_template']['A2']
        self.output_shapes_A3  = params['params_template']['A3']
        self.output_shapes_A4  = params['params_template']['A4']
        self.output_shapes_mass  = params['params_template']['mass']

        # this is the function that returns the coefficients
        self.make_templates = make_templates
        self.symmetrise = symmetrise


    def mix_bin(self, y_bin=[], pt_bin=[], pdf=(lambda x : 1.0), coefficients=coefficients_test):

        # the merged sample
        mix = np.array([])

        pt_edges = np.array([])
        y_edges = np.array([])        
        
        # load a test file to read the bon edges
        test_name = 'pt{:02.1f}'.format(0.0)+'_'+'y{:03.2f}'.format(0.00)+'_M{:05.3f}'.format(80.000)
        for c in range(5):
            p =  0.0
            test_name += ('_A'+str(c)+('{:03.2f}'.format(p)))
        grid_test = np.load(self.input_dir+'/grid_lab_'+test_name+'.npy')

        # y and pt bins of the input shape
        y_edges = grid_test[1]
        pt_edges = grid_test[2]

        # must be odd!
        middle_point = (len( y_edges ) - 1)/2
        y_bin_width = (y_edges[1]-y_edges[0])
        shift_pos = range( int((y_bin[0]-y_edges[0])/y_bin_width), 
                           int((y_bin[1]-y_edges[0])/y_bin_width) )        

        
        for ipt,pt in enumerate(self.input_shapes_pt):
            
            if pt<pt_bin[0] or pt>=pt_bin[1]:
                continue

            for iy in shift_pos:
                y = y_edges[0]+y_bin_width*iy
                print "(%s, %s) is in range" % (pt, y)

                in_name = 'pt{:02.1f}'.format(pt)+'_'+'y{:03.2f}'.format(0.00)
                if not self.make_templates:
                    in_name += '_M{:05.3f}'.format( self.output_shapes_mass[0] )
                in_name_symm = in_name
            
                for ic,c in enumerate( coefficients(pt_bin[0],y_bin[0]) ):
                    c = c if abs(c)>0. else 0.0
                    # this is the mass (if make_templates)
                    if self.make_templates and ic==0:                         
                        in_name      += ('_M'+('{:05.3f}'.format(c)))
                        in_name_symm += ('_M'+('{:05.3f}'.format(c)))
                    # these are the coefficients (if make_templates)
                    elif self.make_templates and ic>0:
                        in_name      += ('_A'+str(ic-1)+('{:03.2f}'.format(c)))
                        in_name_symm += ('_A'+str(ic-1)+('{:03.2f}'.format( -c if (ic-1) in [1,4] and abs(c)>0. else c )))
                    # these are the coefficients as a functon of (pt,y) (if NOT make_templates)
                    else:
                        in_name      += ('_A'+str(ic)+('{:03.2f}'.format(c)))
                        in_name_symm += ('_A'+str(ic)+('{:03.2f}'.format( -c if ic in [1,4] and abs(c)>0. else c )))

                # load the file
                grid = np.load(self.input_dir+'/grid_lab_'+in_name+'.npy')
                grid_symm = np.array([])
                if self.symmetrise:
                    if in_name_symm!=in_name: 
                        print "\tloading the symmetric file..."
                        grid_symm = np.load(self.input_dir+'/grid_lab_'+in_name_symm+'.npy')
                    else:
                        grid_symm = grid                    

                weight = pdf(pt=pt,y=y)
                #weight=1.0

                shifts = [ [iy-middle_point, grid] ]
                if self.symmetrise and shifts[0][0]!=0:                    
                    shifts.append( [-(iy-middle_point), grid_symm] )
                
                #print shifts[0][0], shifts[-1][0]
                for [shift,sample] in shifts:
                    sam = copy.deepcopy(sample[0]) 
                    if shift>0:
                        sam[-shift:, :] = 0.
                    elif shift<0:
                        sam[:-shift, :] = 0.
                    sam_shifted = np.roll(sam, shift, axis=0 ) 
                    if not mix.shape==sam.shape:
                        mix = sam_shifted*weight
                    else:
                        mix += sam_shifted*weight

        if self.symmetrise:
            for ipt in range(mix.shape[1]):
                for iy in range( mix.shape[0]/2 ):
                    #print iy, "+", mix.shape[0]-1-iy
                    left = mix[iy][ipt]
                    right = mix[mix.shape[0]-1-iy][ipt] 
                    mix[iy][ipt] += right
                    mix[mix.shape[0]-1-iy][ipt] += left
            mix *= 0.5

        out_name = 'pt{:02.1f}'.format(pt_bin[0])+'-'+'{:02.1f}'.format(pt_bin[1])+'_'+'y{:03.2f}'.format(y_bin[0])+'-'+'y{:03.2f}'.format(y_bin[1])
        if not self.make_templates:
            out_name += '_M{:05.3f}'.format( self.output_shapes_mass[0] )
        else:
            for ic,c in enumerate( coefficients(0.0, 0.0) ):
                c = c if abs(c)>0. else 0.0
                if ic==0:
                    out_name += ('_M'+('{:05.3f}'.format(c)))
                else:
                    out_name += ('_A'+str(ic-1)+('{:03.2f}'.format(c)))

        
        np.save(self.output_dir+'/mixed_dataset_'+out_name, mix)

        xx, yy = np.meshgrid(pt_edges, y_edges)        
        plt.pcolormesh(yy, xx, mix)
        plt.show()
        plt.savefig(self.output_dir+'/mixed_dataset_'+out_name+'.png')

    def mix_all_bins(self):
        for ipt in range(len(self.output_shapes_pt)-1):
            pt_bin=[ self.output_shapes_pt[ipt], self.output_shapes_pt[ipt+1] ]
            for iy in range(len(self.output_shapes_y)-1):
                y_bin=[ self.output_shapes_y[iy], self.output_shapes_y[iy+1] ]
                print "Call MixData for (%s,%s)" % (pt_bin, y_bin)
                if not self.make_templates:
                    self.mix_bin(pt_bin=pt_bin, y_bin=y_bin, pdf=pdf_test)
                else:
                    for im,m in enumerate(self.output_shapes_mass):
                        for iA0,A0 in enumerate(self.output_shapes_A0):
                            for iA1,A1 in enumerate(self.output_shapes_A1):
                                for iA2,A2 in enumerate(self.output_shapes_A2):
                                    for iA3,A3 in enumerate(self.output_shapes_A3):
                                        for iA4,A4 in enumerate(self.output_shapes_A4):
                                            coefficients = lambda x,y : [m,A0,A1,A2,A3,A4]
                                            self.mix_bin(pt_bin=pt_bin, y_bin=y_bin, pdf=pdf_test, coefficients=coefficients)

 


##################################