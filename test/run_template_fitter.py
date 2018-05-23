import numpy as np
import os
import sys
sys.path.append('./')
sys.path.append('../python/')
from sys import argv
 
from template_fitter import TemplateFitter

#np.random.seed(0)

ntoys = 100

templateFitter = TemplateFitter(DY='CC_FxFx', charge='Wplus', var='WpreFSR', job_name='TEST', mc_mass=80.419, 
                                num_events=1.5e+06,
                                verbose=False, 
                                fixed_parameters=['pol', 'A'], 
                                use_prior=False, 
                                reduce_qt=-1, 
                                reduce_y=-8,
                                reduce_pt=0,
                                fit_mode='parametric',
                                use_prefit=False,
                                add_nonclosure=True,
                                save_plots=[],
                                print_evals=False
                                )

for i in range(ntoys):
    templateFitter.load_data( dataset='random', save_plots=[], postfix='_'+str(i) )
    status = templateFitter.run(n_points=100000, run_minos=False, run_post_hesse=False)
    if status>0:
        continue
    templateFitter.update_results(print_results=True, save_plots=[], run_postfit_toys=True)

templateFitter.close()
