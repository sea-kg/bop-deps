#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Evgenii sopov <mrseakg@gmail.com>

import yaml
import sys

def printHelp():
    print("""
  bop help   .....................   This help
  bop targets   ..................   List of targets
  bop install --dev <target>  ....   Install dev deps for <target>
  bop install --prod <target>  ...   Install prod deps for <target>
  bop install <target>  ..........   Install all deps for <target>
  bop install   ..................   Install all deps for all targets
""")

if len(sys.argv) <= 1:
    printHelp()
    sys.exit(0)

command = sys.argv[1]

if command == "help" or command == "h":
    printHelp()
    sys.exit(0)

parsed_bop_deps = {}

with open("bop-deps.yml") as bop_deps:
    parsed_bop_deps = yaml.load(bop_deps, Loader=yaml.FullLoader)

list_deps = []
for depid in parsed_bop_deps['deps']:
    list_deps.append(depid)

list_targets = []
yaml_targets = parsed_bop_deps['targets']
for targetid in yaml_targets:
    list_targets.append(targetid)
    target = yaml_targets[targetid]
    # check dep names
    if 'deps-prod' in target:
        for dep in target['deps-prod']:
            if dep not in list_deps:
                sys.exit("Not found '" + dep + "' in deps")
    # check dep names
    if 'deps-dev' in target:
        for dep in target['deps-dev']:
            if dep not in list_deps:
                sys.exit("Not found '" + dep + "' in deps")

if command == "targets" or command == "t":
    print("")
    print("Targets and commands for install:")
    for target in parsed_bop_deps["targets"]:
        print("  " + sys.argv[0] + " install " + target)
    print("")

if command == "install" or command == "i":
    
    pass