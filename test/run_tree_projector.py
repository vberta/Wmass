import sys
sys.path.append('./')
sys.path.append('../python/')
from sys import argv

import os.path
from sys import argv
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
argv.remove( '-b-' )

from fit_utils import *
from plot_utils import *

if argv[1]=='pole':
    for var in ['lhe', 'Wdress', 'WpreFSR' ]:
        get_pole_mass(var=var, running=0, tag='qt')
        get_pole_mass(var=var, running=0, tag='y')

elif argv[1]=='plot_qt':
    plot_qt(var='Wdress')

elif argv[1]=='pt_bias':
    qt_max = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    #pt_bias_vs_qt( q='Wplus', var='Wdress', qt_max=qt_max, pt_max=65.0, pt_min=25.0, eta_max=2.5, verbose=False, debug=False )
    print_pt_bias_vs_qt(pt_min=25.0, pt_max=[55.0, 60.0, 65.0, 70.0], qt_max=qt_max, q='Wplus', var='Wdress')

elif argv[1]=='fit':
    for coeff in ['A0','A1','A2','A3','A4','A5', 'A6', 'A7']:
    #for coeff in ['A3']:
        draw_y_slice(fname='../root/tree_histos_CC.root', var='Wdress', coeff=coeff, weight_name=0, do_fit=True)
        #draw_qt_slice(fname='../root/tree_histos_NC.root', var='Wdress', coeff=coeff, weight_name=0, do_fit=False)

elif 'cov' in argv[1]:
    weights = {}
    weights['scale'] = ([0] + [1,2,3,4,6,8])
    weights['pdf'] = range(9,109)
    for q in [#'Wplus', 
              'Wminus'
              ]:
        if 'all' in argv[1]:
            get_covariance(fname='../root/tree_histos_CC.root', DY='CC', var='Wdress', q=q, weights=weights, 
                           coefficients=['A0','A1','A2','A3','A4','A5','A6','A7'], 
                           add_stat_uncert=True, postfix='all_A0-7',
                           save_corr=True, save_coeff=True, save_tree=True, save_pkl=True)
        else:
            for coeff in ['A7']:
                get_covariance(fname='../root/tree_histos_CC.root', DY='CC', var='Wdress', q=q, weights=weights, 
                               coefficients=[coeff], 
                               add_stat_uncert=True, postfix=coeff,
                               save_corr=True, save_coeff=True, save_tree=True, save_pkl=True)

elif argv[1]=='closure':
    for q in ['Wminus']:
        for ceval in ['val']:
            # MC
            plot_closure_test(charge=q,  var='Wdress', coeff_eval=ceval, coeff=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'], 
                              byInvPdf=False,
                              save_2D=True, save_pdf=True, save_summary=True, 
                              do_toy=False, extra_variance_toy=0.0)
            # toy
            plot_closure_test(charge=q,  var='Wdress', coeff_eval=ceval, coeff=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'], 
                              byInvPdf=False,
                              save_2D=False, save_pdf=False, save_summary=True, 
                              do_toy=True, extra_variance_toy=0.001)
            # MC byInvPdf
            plot_closure_test(charge=q,  var='Wdress', coeff_eval=ceval, coeff=['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'], 
                              byInvPdf=True,
                              save_2D=True, save_pdf=False, save_summary=True, 
                              do_toy=False, extra_variance_toy=0.0)            
