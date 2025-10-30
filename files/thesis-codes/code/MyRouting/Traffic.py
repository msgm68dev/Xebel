from utils import file_to_table
import os
import random

prop_A_default = 1
prop_B_default = 0
prop_C_default = 1
class Flow_property:
    def __init__(self, name, type, min, max) -> None:
        self.name = name
        self.type = type
        if type == "int":
            self.min = int(min)
            self.max = int(max)
        elif type == "float":
            self.min = float(min)
            self.max = float(max)
        else:
            raise Exception(f"Error in class Flow_property __init__ : Unknown type {type}")
    def generate_random(self):
        if self.type == "int":
            return random.randint(self.min, self.max)
        elif self.type == "float":
            return self.min + (random.random() * (self.max - self.min))
        else:
            raise Exception(f"Error in Flow_property generate_random: invalid type {self.type}")
    def cast(self, value):
        if self.type == "int":
            return int(value)
        elif self.type == "float":
            return float(value)
        else:
            raise Exception(f"Error in Flow_property cast: invalid type {self.type}")
    def to_str(self):
        return f"Flow_property {self.name}: {self.type} b.w. {self.min}, {self.max}"
class Flow:
    def __init__(self, src_id, dst_id, property_values_dict):
        self.src_id = src_id
        self.dst_id = dst_id
        self.property = property_values_dict
        self.OPTS = {}
    def show_oneline(self, prefix = ' '):
        print("{}f{}. {}>{} : {}".format(prefix, self.OPTS['id'], self.src_id, \
            self.dst_id, 
            ", ".join([f"{p}={self.property[p]}" for p in self.property])))
    def show(self, prefix = ' '):
        self.show_oneline(prefix=prefix)

class Traffic:
    def __init__(self, traffic_file, flow_properties_list, n_flows = -1):
        self.filename = traffic_file
        self.name = os.path.basename(traffic_file)
        self.flows = []
        self.flow_properties_list = flow_properties_list
        tbl = file_to_table(traffic_file, separator=',')
        if n_flows > 0:
            tbl = tbl[:n_flows]
        n_fields = 2 + len(self.flow_properties_list)
        for flow_record in tbl:
            if len(flow_record) < n_fields:
                raise Exception("flow record has not enough fields: {}".format(flow_record))
            src_id    = int(flow_record[0])
            dst_id    = int(flow_record[1])
            property_val_strs = flow_record[2:]
            property_values_dict = {}
            for i in range(len(property_val_strs)):
                name = flow_properties_list[i].name
                value = flow_properties_list[i].cast(property_val_strs[i])
                property_values_dict[name] = value
            flow = Flow(src_id, dst_id, property_values_dict)
            flow.OPTS['id'] = len(self.flows)
            self.flows.append(flow)
    def show(self):
        print('flowset: {}'.format(self.name))
        for flow in self.flows:
            flow.show_oneline('flow ')
