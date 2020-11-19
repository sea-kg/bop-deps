# bop
Binary dependency

## Requirements

```
$ python3 -m pip install requests pyyaml
```

## How to install 

Linux (install from github):
```
sudo curl -L https://raw.githubusercontent.com/sea-kg/bop/main/bop.py -o /usr/local/bin/bop && chmod +x /usr/local/bin/bop
```
*Don't forget install requirements*

## How to use

Help:
```
  bop help   .......................   This help
  bop targets   ....................   List of targets
  bop install  .....................   Install prod && dev all targets for current platfrom<target>
  bop install [keys] [targets]  ....   Install dev deps for <target>
  <keys>:
    --dev .................. install dev dependencies
    --prod ................. install prod dependencies
    --lin .................. install only linux dependencies
    --win .................. install only windows dependencies
    --mac .................. install only macos dependencies
    --all-platfroms ........ install all platfrom dependencies dependencies
    --skip-installed ........ skip if target file already exists
```

Example of control file `bop-deps.yml`

```
source-urls:
  - url: https://sea-kg.com/music/
    with-credentials: no
  - url: https://sea-kg.com/secret/
    with-credentials: yes

targets:
  music:
    - 2020_mi_zoomka

deps:
  2020_mi_zoomka:
    files-any:
      all:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
      prod: {}
      dev: {}
    files-linux:
      all:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
      prod:
        "2020_mi_zoomka/sea5kg%20-%20Mi%20Zoomka%20(30.08.2020).mp3": "bin/audio.mp3"
      dev:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
    files-windows:
      all:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
      prod:
        "2020_mi_zoomka/sea5kg%20-%20Mi%20Zoomka%20(30.08.2020).mp3": "bin/audio.mp3"
      dev:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
    files-macos:
      all:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
      prod:
        "2020_mi_zoomka/sea5kg%20-%20Mi%20Zoomka%20(30.08.2020).mp3": "bin/audio.mp3"
      dev:
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
```

create the bop-credentials:

```
$ bop add-credentials
Notice: In current time support only basic authorization via http header
0: https://sea-kg.com/secret/
Select url for set credentials: 0
Username: user
Password: 
```