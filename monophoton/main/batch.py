import os
import sys
import time
import subprocess

class BatchManager(object):
    def __init__(self, name):
        self.name = name

    def _submit(self, submitter, task, argTemplate, noWait = False, autoResubmit = False):
        submitter.logdir = '/local/' + os.environ['USER']
        submitter.hold_on_fail = True
#        submitter.group = 'group_t3mit.urgent'
        submitter.min_memory = 1

        submitter.submit(name = self.name)

        if not noWait:
            self._waitForCompletion(task, dict(submitter.last_submit), argTemplate, autoResubmit)

    def _waitForCompletion(self, jobType, clusterToJob, argTemplate, autoResubmit):
        print 'Waiting for all jobs to complete.'

        # indices of arguments to pick up from condor_q output lines
        argsToExtract = []
        for ia, a in enumerate(argTemplate.split()):
            if a == '%s':
                argsToExtract.append(ia)

        clusters = clusterToJob.keys()
    
        while True:
            proc = subprocess.Popen(['condor_q'] + clusters + ['-af', 'ClusterId', 'JobStatus', 'Arguments'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = proc.communicate()
            lines = out.split('\n')

            jobsInQueue = []
            for line in lines:
                if line.strip() == '':
                    continue
    
                words = line.split()
    
                clusterId, jobStatus = words[:2]
                if jobStatus == '5':
                    args = tuple(words[3 + i] for i in argsToExtract)
                    print 'Job %s is held' % str(args)

                    if autoResubmit:
                        print ' Resubmitting.'
                        proc = subprocess.Popen(['condor_release', clusterId], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                        out, err = proc.communicate()
                        print out.strip()
                        print err.strip()
                        jobsInQueue.append(clusterId)

                    else:
                        clusters.remove(clusterId)

                else:
                    jobsInQueue.append(clusterId)

            for clusterId in (set(clusters) - set(jobsInQueue)):
                clusters.remove(clusterId)

            if len(clusters) == 0:
                break
    
            time.sleep(10)

