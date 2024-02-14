#!/usr/bin/python3
'''Fabric file to deploy web static

do_pack: Creates an archive of the web_static directory
do_deploy: Moves an archive to the web servers
'''
from fabric.api import *
from datetime import datetime
import os


env.hosts = [
    '52.87.185.174',
    '34.228.162.170'
]
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'


def do_pack():
    ''' Creates an archive of the web_static directory
    Using format:
        versions/web_static_<year><month><day><hour><minute><second>.tgz
    '''
    local("mkdir -p versions")
    archive_path = "versions/web_static_{}.tgz".format(
        datetime.now().strftime('%Y%m%d%H%M%S'))
    result = local("tar -cvzf {} web_static".format(archive_path))

    if result.succeeded:
        return archive_path
    return None


def do_deploy(archive_path):
    '''Tranfers archives to the web servers
    '''
    if not os.path.exists(archive_path):
        return False
    arch_name = archive_path.split('/')[-1]
    dir_name = arch_name.replace(".tgz", "")
    try:
        put(local_path=archive_path, remote_path="/tmp/")
        run("mkdir -p /data/web_static/releases/{}".format(dir_name))
        run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".format(
            arch_name, dir_name))
        run("rm /tmp/{}".format(arch_name))
        run("mv /data/web_static/releases/{}/web_static/*\
        /data/web_static/releases/{}/".format(dir_name, dir_name))
        run("rm -rf /data/web_static/releases/{}/web_static".format(
            dir_name))
        run("rm -rf /data/web_static/current")
        run("ln -s /data/web_static/releases/{}\
        /data/web_static/current".format(dir_name))
    except Exception:
        return False
    return True
