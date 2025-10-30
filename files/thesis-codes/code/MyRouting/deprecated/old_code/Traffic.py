from utils import file_to_table
import os
# from evaluation.evaltools import read_flowset

Rate_default = 1
ArriveAt_default = 0
Duration_default = 1
class Flow:
    def __init__(self, src_id, dst_id, rate = Rate_default, arrive_at = ArriveAt_default, duration = Duration_default):
        self.src_id = src_id
        self.dst_id = dst_id
        self.rate = rate
        self.arrive_at = arrive_at
        self.duration = duration
        self.OPTS = {}
    def show_oneline(self, prefix = ' '):
        print("{}f{}. {} > {} R={} D={} Aat={}".format(prefix, self.OPTS['id'], self.src_id, \
            self.dst_id, self.rate, self.duration, self.arrive_at))
    def show(self):
        self.show_oneline()

class Traffic:
    def __init__(self, traffic_file):
        self.filename = traffic_file
        self.name = os.path.basename(traffic_file)
        self.flows = []
        tbl = file_to_table(traffic_file, separator=',')
        for flow_record in tbl:
            if len(flow_record) < 5:
                raise Exception("flow record has not enough fields: {}".format(flow_record))
            src_id    = int(flow_record[0])
            dst_id    = int(flow_record[1])
            rate      = int(flow_record[2] or Rate_default) 
            arrive_at = int(flow_record[3] or ArriveAt_default)
            duration  = int(flow_record[4] or Duration_default)
            flow = Flow(src_id, dst_id, rate=rate, arrive_at=arrive_at, duration=duration)
            flow.OPTS['id'] = len(self.flows)
            self.flows.append(flow)
    def show(self):
        print('flowset: {}'.format(self.name))
        for flow in self.flows:
            flow.show_oneline('  ')