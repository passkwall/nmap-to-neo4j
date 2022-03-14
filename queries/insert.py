def create_nodes(tx, i, a):
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

              if a.attacking_ip:

                     if a.attacking_ip and a.attacking_hostname is None:
                            a.attacking_hostname = "None"

                     tx.run(
                            "MATCH(h:Host {ip: $ip})"
                            "MERGE(a:Attacker {ip: $attacking_ip, hostname: $attacking_hostname})"
                            "MERGE(a)-[:CONNECTS_TO]->(h)",
                            attacking_hostname=a.attacking_hostname,
                            attacking_ip=a.attacking_ip,
                            ip=h['ip']
                     )