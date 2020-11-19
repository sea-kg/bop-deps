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
bop help   .....................   This help
bop targets   ..................   List of targets
bop install --dev <target>  ....   Install dev deps for <target>
bop install --prod <target>  ...   Install prod deps for <target>
bop install <target>  ..........   Install all deps for <target>
bop install   ..................   Install all deps for all targets
```

Example of control file `bop-deps.yml`

```
source-urls:
  - url: https://sea-kg.com/music/
    with-credentials: no

targets:
  music:
    deps-prod:
      - 2020_mi_zoomka
    deps-dev:
      - 2020_mi_zoomka

deps:
  2020_mi_zoomka:
    files:
      linux:
        "2020_mi_zoomka/sea5kg%20-%20Mi%20Zoomka%20(30.08.2020).mp3": "bin/audio.mp3"
        "2020_mi_zoomka/cover.jpg": "bin/image.jpg"
```