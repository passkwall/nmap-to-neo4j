#!/usr/bin/python3

import argparse
import re
from neo4j import GraphDatabase
from queries import insert

def check_attacking_args(a):
     if a.attacking_hostname and not a.attacking_ip:
          print("[!] - Attacking-host needs to be supplied with an attacking-ip (-ai / --attacking-ip).")
          exit()

def create_arg_parser():
     parser = argparse.ArgumentParser(description="Masscan-to-Neo4j Graph Database Utility")
     parser.add_argument(
          "-b",
          "--bolt",
          action="store",
          dest="bolt",
          help="Address of your bolt connector. Default, '127.0.0.1'",
          required=False,
          default="127.0.0.1",
     )
     parser.add_argument(
          "-u",
          "--username",
          action="store",
          dest="neo_user",
          help="Username of the Neo4j user.  Default, 'neo4j'.",
          required=False,
          default="neo4j",
     )
     parser.add_argument(
          "-p",
          "--password",
          dest="neo_pass",
          help="Password of the Neo4j user.",
          required=True,
     )
     parser.add_argument(
          "-P",
          "--port",
          dest="neo_port",
          help="Port of the bolt instance if not 7687.",
          required=False,
          default="7687",
     )
     parser.add_argument(
          "-f",
          "--file",
          dest="nmap_file",
          help="Scan of the grepable nmap file (-oG flag).",
          required=True,
     )
     parser.add_argument(
          "-ah",
          "--attacking-host",
          dest="attacking_hostname",
          help="Hostname of the attacking machine.",
     )

     parser.add_argument(
          "-ai",
          "--attacking-ip",
          dest="attacking_ip",
          help="IP address of the attacking machine.",
     )
     return parser

def create_neo4j_driver(bolt, neo_port, neo_user, neo_pass):
     uri = "neo4j://{}:{}".format(bolt, neo_port)
     print("Connecting to {}".format(uri))
     driver = GraphDatabase.driver(uri, auth=(neo_user, neo_pass))
     return driver

def extract_nmap_host_information(data):
     split_data = data.split("\t")
     host_line = split_data[0]
     portinfo_line = split_data[1]

     has_open_port_pattern = "[0-9]{1,5}/open/"

     has_open_ports = re.search(has_open_port_pattern, portinfo_line)

     if has_open_ports is None:
          return None

     ipv4_pattern = "([0-9]{1,3}\.){3}[0-9]{1,3}"

     extracted_ipv4_addr = re.search(ipv4_pattern, host_line).group()
     extracted_hostname = host_line.split("(")[1].split(")")[0]

     port_line = portinfo_line.split("Ports: ")[1]
     port_data = parse_port_protocol_info(port_line)

     host = {
          'host_info': {
               'hostname': extracted_hostname,
               'ip': extracted_ipv4_addr
          },
          'port_info': port_data
     }

     return host

def open_nmap_file(file):
     print("Opening nmap file.")
     return open(file, 'r')

def parse_nmap_file(file):
     up_host_regex_pattern = "Host:\s([0-9]{1,3}\.?){4}\s\(([a-zA-Z0-9\.\-\_]+)?\)\sPorts:" # Find up hosts that have port info. 
     entries = []
     nmap_file = open_nmap_file(file)
     for line in nmap_file:
          match = re.search(up_host_regex_pattern, line)
          if match:
               data = extract_nmap_host_information(line)
               if data is not None:
                    entries.append(data)

     print ("{} host to add.".format(len(entries)))
     return entries

def parse_port_protocol_info(info):
     details = []
     port_lines = info.split(" ")

     for p in port_lines:
          if "open" in p:
               d = p.split("/")

               port_info = {
                    'no': d[0],
                    'state': d[1],
                    'protocol': d[2],
                    'owner': d[3],
                    'service': d[4],
                    'sunrpcinfo': d[5],
                    'versioninfo': d[6]
               }
               details.append(port_info)
     return details

def populate_neo4j_database(data, driver, a):
     for entry in data:
          with driver.session() as session:
               session.write_transaction(insert.create_nodes, entry,  a)

if __name__ == "__main__":
     arg_paser = create_arg_parser()
     args = arg_paser.parse_args()

     check_attacking_args(args)

     driver = create_neo4j_driver(args.bolt, args.neo_port, args.neo_user, args.neo_pass)
     parsed_nmap_data = parse_nmap_file(args.nmap_file)

     populate_neo4j_database(parsed_nmap_data, driver, args)

     print("Done Syncing!")