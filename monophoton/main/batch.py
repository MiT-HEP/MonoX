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

        clusterId = submitter.submit(name = self.name)

        if not noWait:
            self._waitForCompletion(task, clusterId, argTemplate, autoResubmit)

    def _waitForCompletion(self, jobType, clusterId, argTemplate, autoResubmit):
        print 'Waiting for all jobs to complete.'

        # indices of arguments to pick up from condor_q output lines
        argsToExtract = []
        for ia, a in enumerate(argTemplate.split()):
            if a == '%s':
                argsToExtract.append(ia)

        while True:
            proc = subprocess.Popen(['condor_q', str(clusterId), '-af', 'ProcId', 'JobStatus', 'Arguments'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            out, err = proc.communicate()
            lines = out.split('\n')

            jobsInQueue = []
            heldJobs = []
            for line in lines:
                if line.strip() == '':
                    continue
    
                words = line.split()
    
                procId, jobStatus = words[:2]
                if jobStatus == '5':
                    args = tuple(words[3 + i] for i in argsToExtract)
                    if args in heldJobs:
                        continue

                    print 'Job %s is held' % str(args)

                    if autoResubmit:
                        print ' Resubmitting.'
                        proc = subprocess.Popen(['condor_release', '%s.%s' % (clusterId, procId)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                        out, err = proc.communicate()
                        print out.strip()
                        print err.strip()
                        jobsInQueue.append(procId)
                    else:
                        heldJobs.append(args)

                else:
                    jobsInQueue.append(procId)

            sys.stdout.write('\r %d jobs in queue.' % len(jobsInQueue))
            sys.stdout.flush()

            if len(jobsInQueue) == 0:
                break
    
            time.sleep(10)

sys.stdout.write('\n')
sys.stdout.flush()
