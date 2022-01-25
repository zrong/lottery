"""
部署 pyape app
~~~~~~~~~~~~~~~~~~~

默认使用 GunicornDeploy 部署。

另外支持 UwsgiDeploy/SupervisorGunicornDeploy，详见 pyape.cli.fabric 。

查看所有可用的环境(env)，请调用：

fab envs

对于一个全新的未部署的环境，请调用：

fab init -env [env] 

然后需要登录服务器进入 flask shell 初始化数据库

fab start --env [env] 

日常更新功能：

fab deploy --env [env] 
fab reload --env [env] 

更新配置文件 config.json + gunicorn.conf.py + .env：

fab putjson --env [env] 
fab putpy --env [env] 
fab putenv --env [env] 
"""

from pathlib import Path

from invoke import task
from invoke.exceptions import Exit

from pyape.cli.fabric import logger, GunicornDeploy as Deploy

from fabconfig import rsync_exclude, config_json, _env, gunicorn_conf_py, enviroments


basedir = Path(__file__).parent


@task
def envs(c):
    """ 查看支持哪些环境
    """
    logger.info('可用的环境(env): \n\n%s\n', '\n'.join(enviroments.keys()))


@task
def putjson(c, env, local=False):
    """ 生成 config.json 并上传
    """
    d = Deploy(env, enviroments, c, basedir)
    d.put_tpl('config_json', config_json, dstname='config.json', force=True, local=local)


@task
def putenv(c, env, local=False):
    """ 生成 .env 或上传
    """
    d = Deploy(env, enviroments, c, basedir)
    d.put_tpl('_env', _env, dstname='.env', wrapkey='options', force=True, local=local)

@task
def putpy(c, env, local=False):
    """ 生成 gunicorn.conf.py 并上传
    """
    d = Deploy(env, enviroments, c, basedir)
    d.put_tpl('gunicorn_conf_py', gunicorn_conf_py, dstname='gunicorn.conf.py', force=True, local=local)


@task
def putcfiles(c, env, local=False):
    """ 根据tpl文件生成配置文件并上传
    """
    d = Deploy(env, enviroments, c, basedir)
    d.put_tpl('config_json', config_json, dstname='config.json', force=True, local=local)
    d.put_tpl('_env', _env, dstname='.env', wrapkey='options', force=True, local=local)
    d.put_tpl('gunicorn_conf_py', _env, dstname='gunicorn.conf.py', force=True, local=local)


@task
def venv(c, env, init=False, upgrade=None):
    """ 创建虚拟环境
    """
    d = Deploy(env, enviroments, c, basedir)
    if init:
        d.init_remote_venv()
    if upgrade == 'all':
        d.pipupgrade(all=True)
    elif isinstance(upgrade, str):
        d.pipupgrade(names=upgrade.split(','))


@task
def deploy(c, env):
    """ 部署最新程序到远程服务器
    """
    d = Deploy(env, enviroments, c, basedir)
    d.rsync(exclude=rsync_exclude)
    putcfiles(c, env, False)


@task
def dar(c, env):
    """ 部署并重载
    """
    deploy(c, env)
    reload(c, env)


@task
def init(c, env):
    """ 在服务器上创建一个全新的 API 环境
    """
    deploy(c, env)
    venv(c, env, init=True)


@task
def start(c, env, wsgi_app='wsgi:pyape_app'):
    """ 在服务器上启动一个 API
    """
    d = Deploy(env, enviroments, c, basedir)
    d.start(wsgi_app)


@task
def stop(c, env):
    """ 在服务器上停止一个 API
    """
    d = Deploy(env, enviroments, c, basedir)
    d.stop()


@task
def reload(c, env):
    """ 在服务器上重载一个 API
    """
    d = Deploy(env, enviroments, c, basedir)
    d.reload()


@task
def pipoutdated(c, env):
    """ 打印所有的过期的 package
    """
    d = Deploy(env, enviroments, c, basedir)
    d.pipoutdated()
