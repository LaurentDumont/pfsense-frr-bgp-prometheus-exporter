import subprocess
import os
import json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

variable = subprocess.Popen("vtysh -c \"show bgp neighbors json\"",stdout=subprocess.PIPE,shell=True)
potato = variable.stdout.read()
json_data = json.loads(potato)
bgp_state_established_epoch = 0

for key, value in json_data.items():
    neighbor_ip = key
    print(f'Parsing neighbor: {key}')
    registry = CollectorRegistry()
    for key, value in value.items():
        if key == 'remoteAs':
            remote_as = value
            metric = Gauge('bgp_exporter_remote_as', 'Remote AS of the BGP session', ['instance', 'neighbor_ip'], registry=registry)
            metric.labels(instance='pfsense-frr-2', neighbor_ip=neighbor_ip).set(remote_as)
        if key == 'localAs':
            local_as = value
            metric = Gauge('bgp_exporter_local_as', 'Local AS of the BGP session', ['instance', 'neighbor_ip'], registry=registry)
            metric.labels(instance='pfsense-frr-2', neighbor_ip=neighbor_ip).set(local_as)
        if key == 'nbrDesc':
            neighbor_description = value
            metric = Gauge('bgp_exporter_neighbor_description', 'Description of the BGP session', ['bgp_host', 'instance', 'neighbor_ip'], registry=registry)
            metric.labels(bgp_host=neighbor_description, instance='pfsense-frr-2', neighbor_ip=neighbor_ip).set(0)
        if key == 'bgpState':
            bgp_state = value
            if bgp_state == 'Established':
                bgp_state = 1
            else:
                bgp_state = 666
            metric = Gauge('bgp_exporter_neighbor_state', 'State of the BGP session', ['instance', 'neighbor_ip'], registry=registry)
            metric.labels(instance='pfsense-frr-2', neighbor_ip=neighbor_ip).set(bgp_state)
        if key == 'bgpTimerUpEstablishedEpoch':
            bgp_state_established_epoch = value
            metric = Gauge('bgp_exporter_neighbor_timestamp', 'Establised timestap of the BGP session', ['instance', 'neighbor_ip'], registry=registry)
            metric.labels(instance='pfsense-frr-2', neighbor_ip=neighbor_ip).set(bgp_state_established_epoch)
    print(remote_as, local_as, neighbor_description, bgp_state, bgp_state_established_epoch)
    push_to_gateway('10.10.89.10:9091', job=neighbor_ip, registry=registry)
