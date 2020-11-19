#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Evgenii sopov <mrseakg@gmail.com>

import yaml
import sys
import os
import requests

def printHelp():
    print("""
  bop help   .....................   This help
  bop targets   ..................   List of targets
  bop install --dev <target>  ....   Install dev deps for <target>
  bop install --prod <target>  ...   Install prod deps for <target>
  bop install <target>  ..........   Install all deps for <target>
  bop install   ..................   Install all deps for all targets
""")

argc = len(sys.argv)

if argc <= 1:
    printHelp()
    sys.exit(0)

command = sys.argv[1]

if command == "help" or command == "h":
    printHelp()
    sys.exit(0)

parsed_bop_deps = {}

filename = "bop-deps.yml" 
with open(filename) as bop_deps:
    parsed_bop_deps = yaml.load(bop_deps, Loader=yaml.FullLoader)

if 'deps' not in parsed_bop_deps:
    sys.exit("\nERROR: Not found deps in '" + filename + "'\n")

if 'targets' not in parsed_bop_deps:
    sys.exit("\nERROR: Not found targets in '" + filename + "'\n")

if 'source-urls' not in parsed_bop_deps:
    sys.exit("\nERROR: Not found source-urls in '" + filename + "'\n")

list_deps = []
yaml_deps = parsed_bop_deps['deps']
for depid in yaml_deps:
    list_deps.append(depid)

list_source_urls = []
yaml_source_urls = parsed_bop_deps['source-urls']
for url in yaml_source_urls:
    list_source_urls.append(url)

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

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python ≥ 2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def try_download_file(src_filepath, dst_filepath):
    dst_dir = os.path.dirname(dst_filepath)
    if not os.path.exists(dst_dir):
        mkdir_p(dst_dir)

    downloaded_success = False
    for src_url in list_source_urls:
        src_url = src_url["url"] + src_filepath
        print("Try download file '" + src_url + "'")
        r = requests.get(src_url, allow_redirects=True)
        if r.status_code != 200:
            continue
        downloaded_success = True
        open(dst_filepath, 'wb').write(r.content)
        break

    if not downloaded_success:
        sys.exit("\nERROR: Could not download.\n")
    print("Saved to '" + dst_filepath + "'.")

def install_dep(depid, yaml_dep):
    selected_platform = ''
    if 'linux' in sys.platform:
        selected_platform = 'linux'
    yaml_files = {}
    if 'files' in yaml_dep:
        yaml_files = yaml_dep['files']
    if selected_platform not in yaml_files:
        sys.exit("\nERROR: Not found deps." + depid + ".files." + selected_platform + "'\n")

    yaml_files = yaml_files[selected_platform]
    for src_filepath in yaml_files:
        dst_filepath = yaml_files[src_filepath]
        try_download_file(src_filepath, dst_filepath)

if command == "install" or command == "i":
    current_path = os.path.abspath(".")
    type_deps = []
    target = ''
    if argc > 2:
        opt3 = sys.argv[2]
        if opt3 == '--prod':
            type_deps.append('deps-prod')
        elif opt3 == '--dev':
            type_deps.append('deps-dev')
        else:
            target = opt3
    if argc > 3 and type_deps != 'all':
        target = sys.argv[3]

    if target != '' and target not in list_targets:
        sys.exit("\nERROR: Not found '" + target + "' \n\n  Try " + sys.argv[0] + " targets\n")

    install_targets = []
    if target == '':
        install_targets.extend(list_targets)
    else:
        install_targets.append(target)

    if len(type_deps) == 0:
        type_deps.extend(['deps-prod', 'deps-dev'])

    print("install_targets = " + str(install_targets))
    print("type_deps = " + str(type_deps))

    for install_target in install_targets:
        yaml_target = yaml_targets[install_target]
        for install_type_deps in type_deps:
            if install_type_deps not in yaml_target:
                sys.exit("\nERROR: Not found type-deps '" + install_type_deps + "' in target '" + install_target + "'\n")
            names_deps = yaml_target[install_type_deps]
            for name_deps in names_deps:
                yaml_dep = yaml_deps[name_deps]
                install_dep(name_deps, yaml_dep)