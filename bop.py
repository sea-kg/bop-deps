#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Evgenii sopov <mrseakg@gmail.com>

import yaml
import sys
import os
import requests
import base64
from getpass import getpass

def printHelp():
    print("""
  bop help   .......................   This help
  bop targets   ....................   List of targets
  bop install  .....................   Install prod && dev all targets for current platfrom<target>
  bop install [keys] [targets]  ....   Install dev deps for <target>
  <keys>:
    --dev ................... install dev dependencies
    --prod .................. install prod dependencies
    --lin ................... install only linux dependencies
    --win ................... install only windows dependencies
    --mac ................... install only macos dependencies
    --all-platfroms ......... install all platfrom dependencies dependencies
    --skip-installed ........ skip if target file already exists
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
    deps = yaml_targets[targetid]
    # check dep names
    for dep in deps:
        if dep not in list_deps:
            sys.exit("Not found '" + dep + "' in deps")

if command == "add-credentials" or command == "ac":
    print("Notice: In current time support only basic authorization via http header")
    src_urls_with_creds = []
    for src_url in list_source_urls:
        if 'with-credentials' in src_url and src_url['with-credentials'] == True:
            src_urls_with_creds.append(src_url['url'])
    if len(src_urls_with_creds) == 0:
        sys.exit("\nERROR: Not found source-urls with-credentials: yes\n")
    count = 0
    for src_url in src_urls_with_creds:
        print(str(count) + ": " + src_url)
        count = count + 1
    url_number = input("Select url for set credentials: ")
    url_number = int(url_number)
    if url_number >= len(src_urls_with_creds):
        sys.exit("\nERROR: please enter number less then " + str(count) + "\n")

    src_url = src_urls_with_creds[int(url_number)]
    
    username = input("Username: ")
    password = getpass()
    auth = username + ":" + password
    auth = base64.b64encode(auth.encode("UTF-8")).decode("UTF-8")
    auth = "Basic " + auth
    parsed_bop_creds = {}
    filename2 = "bop-credentials.yml"
    if os.path.isfile(filename2):
        with open(filename2, 'r') as bop_credentials:
            parsed_bop_creds = yaml.load(bop_credentials, Loader=yaml.FullLoader)
    parsed_bop_creds[src_url] = {
        "headers": {
            "Authorization": auth
        }
    }
    parsed_bop_creds = yaml.dump(parsed_bop_creds, sort_keys=True)
    bop_credentials_write = open(filename2, 'w')
    bop_credentials_write.write(parsed_bop_creds)
    bop_credentials_write.close()

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

installed_src_urls = []
installed_dst_files = []

def try_download_file(src_filepath, dst_filepath):
    dst_dir = os.path.dirname(dst_filepath)
    if not os.path.exists(dst_dir):
        mkdir_p(dst_dir)

    downloaded_success = False
    for src_url in list_source_urls:
        src_urlpath = src_url["url"]
        headers = {}
        if "with-credentials" in src_url and src_url["with-credentials"] == True:
            filename_creds = "bop-credentials.yml"
            if not os.path.isfile(filename_creds):
                sys.exit("\nERROR: expected creds (1) for '" + src_urlpath + "', but not found file " + filename_creds
                    + "\nPlease, try command: \n\n    bop add-credentials\n")
            parsed_bop_creds = {}
            with open(filename_creds, 'r') as bop_credentials:
                parsed_bop_creds = yaml.load(bop_credentials, Loader=yaml.FullLoader)
            if src_urlpath not in parsed_bop_creds:
                sys.exit("\nERROR: expected creds (2) for '" + src_urlpath + "', but not found "
                    + "\nPlease, try command: \n\n    bop add-credentials\n")
            headers = parsed_bop_creds[src_urlpath]['headers']

        src_fullurl = src_urlpath + src_filepath
        if src_fullurl in installed_src_urls:
            print("Skip. Already installed '" + src_fullurl + "'")
            downloaded_success = True
            return
        print("Try download file '" + src_fullurl + "'")
        r = requests.get(src_fullurl, headers=headers, allow_redirects=True)
        if r.status_code != 200:
            if r.status_code == 401:
                print("Not authorized")
            else:
                print("Status HTTP(s) Code: " + str(r.status_code))
            continue

        if dst_filepath in installed_dst_files:
            sys.exit("\nERROR: File " + dst_filepath + " - could not be rewrite!")
        installed_dst_files.append(dst_filepath)
        downloaded_success = True
        open(dst_filepath, 'wb').write(r.content)
        installed_src_urls.append(src_fullurl)
        break

    if not downloaded_success:
        sys.exit("\nERROR: Could not download.\n")
    print("Saved to '" + dst_filepath + "'.")

def install_dep(depid, type_deps, platforms, skip_exists, yaml_dep):
    for platform in platforms:
        files_tag = 'files-' + platform
        if files_tag not in yaml_dep:
            sys.exit("\nERROR: Not found deps." + depid + "." + files_tag + "'\n")
        yaml_types = yaml_dep[files_tag]
        for dep_type in type_deps:
            if dep_type not in yaml_types:
                sys.exit("\nERROR: Not found deps." + depid + "." + files_tag + "." + dep_type + "\n")
            yaml_files = yaml_types[dep_type]
            for src_filepath in yaml_files:
                dst_filepath = yaml_files[src_filepath]
                if skip_exists and os.path.isfile(dst_filepath):
                    print("Skip installed. Destination file exists: '" + dst_filepath + "'")
                    continue
                try_download_file(src_filepath, dst_filepath)

if command == "install" or command == "i":
    current_path = os.path.abspath(".")

    install_targets = []
    install_type_deps = ['all']
    install_platforms = ['any']
    install_skip_exists = False
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--prod':
            install_type_deps.append('prod')
        elif arg == '--dev':
            install_type_deps.append('dev')
        elif arg == '--lin':
            install_platforms.append('linux')
        elif arg == '--win':
            install_platforms.append('windows')
        elif arg == '--mac':
            install_platforms.append('macos')
        elif arg == '--skip-installed':
            install_skip_exists = True
        elif arg == '--all-platforms':
            install_platforms.extend(['linux', 'windows', 'macos'])
        else:
            install_targets.append(arg)
        i = i + 1

    if len(install_targets) == 0:
        install_targets.extend(list_targets)

    for target in install_targets:
        if target not in list_targets:
            sys.exit("\nERROR: Not found '" + target + "' \n\n  Try " + sys.argv[0] + " targets\n")

    # automaticly detect platfrom
    if len(install_platforms) == 1:
        platform = sys.platform
        if 'linux' in sys.platform:
            install_platforms.append('linux')
        if 'win' in platform:
            install_platforms.append('windows')
        if 'darwin' in platform:
            install_platforms.append('macos')

    # if not define prod or dev specific add all
    if len(install_type_deps) == 1:
        install_type_deps.extend(['prod', 'dev'])

    print("install_targets = " + str(install_targets))
    print("install_type_deps = " + str(install_type_deps))
    print("install_platforms = " + str(install_platforms))

    for install_target in install_targets:
        yaml_install_list_deps = yaml_targets[install_target]
        for install_depid in yaml_install_list_deps:
            yaml_dep = yaml_deps[install_depid]
            install_dep(install_depid, install_type_deps, install_platforms, install_skip_exists, yaml_dep)