__author__ = 'savad'

import os, platform

from apps.jobs.generic.job_manager import ResultAction
from apps.jobs.generic.event_processor import ep_entry

def job_ping(**kwargs):
    ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
    if os.system("ping " + ping_str + " " + kwargs['url']) == 0:
        report = ResultAction(kwargs, status={"region": "", "status": "up"})
        ep_entry.delay(report)
    report = ResultAction(kwargs, status={"region": "", "status": "down"})
    ep_entry.delay(report)