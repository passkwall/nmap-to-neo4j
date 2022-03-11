def create_nodes(tx, i):
       h = i['host_info']
       ports = i['port_info']
       print("Adding {} data to to Neo4j".format(h['ip']))

       for p in ports:
              tx.run(
                     "MERGE(p:Port {port: $port, state: $state, protocol: $protocol, owner: $owner, service: $service, sunrpcinfo: $sunrpcinfo, versioninfo: $versioninfo})"
                     "MERGE(h:Host {ip: $ip, hostname: $hostname})"
                     "MERGE (p)-[:OPEN]->(h)",
                     port=p['no'],
                     state=p['state'],
                     protocol=p['protocol'],
                     owner=p['owner'],
                     service=p['service'],
                     sunrpcinfo=p['sunrpcinfo'],
                     versioninfo=p['versioninfo'],
                     hostname=h['hostname'],
                     ip=h['ip']
              )