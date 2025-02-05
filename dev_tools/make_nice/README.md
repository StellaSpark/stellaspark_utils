Auto format python code in nexus directories that contain python code
=============================
Goal: run autoformat tools on python code without running a docker container that runs that python code (so no project deps required)
1. go to nexus project root
2. run make_nice harvester (or backend) <-- those 2 dirs have python code 
3. make_nice.bat calls make_nice.sh (also in nexus project root)
4. make_nice.sh build a docker image based dev_tools/make_nice/Dockerfile
   1. black, isort and flake8 make use of config files (so that all devs run these tools with same config)
   2. these config files are: dev_tools/make_nice/pyproject.toml and dev_tools/make_nice/setup.cfg
   3. black, isort and flake8 looks for these config files in root dir, so we COPY both in docker root dir
5. make_nice.sh runs isort, black and flake8 for 1 directory (e.g. nexus-harvester)
   1. isort applies it changes immediately
   2. black applies it changes immediately
   3. flake8 only gives feedback on what is wrong
