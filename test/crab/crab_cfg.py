from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.requestName = 'TEST'
config.General.transferLogs=True

config.section_("JobType")
config.JobType.pluginName = 'PrivateMC'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
config.JobType.inputFiles = ['crab_script.py', 'FrameworkJobReport.xml', 'unfolder.py', 'template_parameters.py']
config.JobType.sendPythonFolder	 = True
config.JobType.outputFiles = ['result_TEST.pkl']

config.section_("Data")
config.Data.splitting = 'EventBased'
config.Data.unitsPerJob = 1
config.Data.totalUnits = 50
config.Data.publication = False
config.Data.outputDatasetTag = 'TEST'

config.section_("Site")
config.Site.storageSite = "T2_IT_Pisa"
#config.Site.whitelist = ["T2_IT_Pisa"]

create = False
submit = True
killall = False
getoutput = False

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand

    jobs = [ 
        #['1e5_pt_y', 100000,   ['mass', 'A0', 'A4'], 1, 1, 0.3, 0.3],
        ['1e6_pt_y', 1000000,  ['mass', 'A0', 'A4'], 1, 1, 0.3, 0.3],
        ['1e7_pt_y', 10000000, ['mass', 'A0', 'A4'], 1, 1, 0.3, 0.3],
        ['1e5_pt_y_A0_A4', 100000,   ['mass'], 1, 1, 0.3, 0.3],
        ['1e6_pt_y_A0_A4', 1000000,  ['mass'], 1, 1, 0.3, 0.3],
        ['1e7_pt_y_A0_A4', 10000000, ['mass'], 1, 1, 0.3, 0.3],
        ['1e5_pt_y_A0_A4_prior05', 100000,   ['mass'], 1, 1, 0.5, 0.5],
        ['1e6_pt_y_A0_A4_prior05', 1000000,  ['mass'], 1, 1, 0.5, 0.5],
        ['1e7_pt_y_A0_A4_prior05', 10000000, ['mass'], 1, 1, 0.5, 0.5],
        ['1e5_pt_y_A0_A4_mass', 100000,   [], 1, 1, 0.3, 0.3],
        ['1e6_pt_y_A0_A4_mass', 1000000,  [], 1, 1, 0.3, 0.3],
        ['1e7_pt_y_A0_A4_mass', 10000000, [], 1, 1, 0.3, 0.3],
        ['1e5_y_A0_A4', 100000,   ['mass'], 0, 1, 0.3, 0.3],
        ['1e6_y_A0_A4', 1000000,  ['mass'], 0, 1, 0.3, 0.3],
        ['1e7_y_A0_A4', 10000000, ['mass'], 0, 1, 0.3, 0.3],
        ]

    for job in jobs:
        if not create:
            continue
        fout = open('crab_script_'+job[0]+'.py', 'w') 
        fin = open('crab_script.py', 'r') 
        lines = fin.readlines()
        for line in lines:
            line = line.rstrip()
            if '#01' in line and (job[3]==0 and job[4]==1):
                line = line[1:]
            if '#10' in line and (job[3]==1 and job[4]==0):
                line = line[1:]                
            elif 'job_name =' in line:
                line += (' "'+job[0]+'"')
            elif 'num_events =' in line:
                line += (' '+str(job[1]))
            elif 'fix =' in line:
                line += '['
                for fixes in job[2]:
                    line += ('"'+fixes+'"')
                    line += ', '
                line += ']'
            elif 'prior_coeff =' in line:
                line += (' '+str(job[5]))
            elif 'prior_xsec =' in line:
                line += (' '+str(job[6]))
            #print line
            line += '\n'
            fout.write(line)
        fout.close()
        fin.close()

        fout = open('crab_script_'+job[0]+'.sh', 'w') 
        fin = open('crab_script.sh', 'r') 
        lines = fin.readlines()
        for line in lines:
            line = line.rstrip()
            if 'python crab_script_' in line:
                line += (job[0]+'.py $1')
            fout.write(line+'\n')
        fout.close()
        fin.close()

    if submit:
        for job in jobs:
            config.General.requestName = 'unfolder_'+job[0]
            config.JobType.scriptExe = 'crab_script_'+job[0]+'.sh'
            config.JobType.inputFiles = ['crab_script_'+job[0]+'.py', 'FrameworkJobReport.xml', 'unfolder.py', 'template_parameters.py']
            config.JobType.outputFiles = ['result_'+job[0]+'.pkl']
            crabCommand('submit', config = config)

    if killall:
        import os
        for job in jobs:
            os.system('crab kill -d '+'crab_'+'unfolder_'+job[0])
            os.system('rm -r '+'crab_'+'unfolder_'+job[0])
        os.system('rm crab_script_*.py crab_script_*.sh')

    if getoutput:
        import os
        for job in jobs:
            os.system('crab getoutput -d '+'crab_'+'unfolder_'+job[0])