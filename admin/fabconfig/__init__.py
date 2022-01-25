"""
Fabric 的配置文件
"""

# 要排除的文件/文件夹
rsync_exclude = ['.DS_Store', '.vscode', '*.pyc', 'fab*', '__pycache__', '*.swp', '*.iml', '*.code-workspace', '*.jinja2', '*.dot', '*.json',
    '.pyenv', 'venv', 'wiki', '.git', 'output', 'tests', 'logs', 'wechat_sdk', 'flask_sqlalchemy',
    '.gitignore', 'config.*', 'uwsgi.*', '*.service', 'gunicorn.*']

# .env 基本配置文件内容，保存 FLASK 运行需要的配置，以及 flask.config 中的配置
# 可在 envs 中进行覆盖
_env = {
    'FLASK_APP': 'wsgi:lottery',
    'FLASK_ENV': 'production',
    # 'FLASK_RUN_PORT': 5000,
    # 'FLASK_RUN_WITH_THREADS': True,
}

# gunicorn.conf.py 的基本配置文件内容，可在 env 中进行覆盖
gunicorn_conf_py = {
    'wsgi_app': 'wsgi:lottery',
    'proc_name': 'lottery',
    'bind': '127.0.0.1:5001',
    'umask': 0,
    'daemon': 'True',
    'capture_output': 'True',
}

# uwsgi.ini 基本配置文件内容
# 可以在 envs 中进行覆盖
uwsgi_ini = {
    'processes': 2,
    'threads': 1,
    'venv': '%dvenv',
    # 是否切换到后台，本地调试的时候可以设为 False，直接查看控制台输出
    'daemonize': True,
    # socket 和 http 参数二选一，如果同时选择，以 socket 参数为准
    # 端口转发可能引发 nginx 499 问题（推测是端口转发 limit 没有打开） 
    # 改为使用 sock 文件 （同样需要打开 limit 限制）
    'socket': '%d%n.sock',
    # 'http_socket': '127.0.0.1:5002',
    # 'http': '127.0.0.1:5002',
    # Stat Server
    'stats': '%d%nstats.sock',
}

# config.json 基本配置文件内容，pyape 服务器 运行需要的配置
# 可以在 envs 中进行覆盖
config_json = {
    'FLASK': {
        # 用于 FLASK 内部加密
        'SECRET_KEY': 'QHSg3iCkdYLc5rtvKXZ6lXjJwhWKt0HojK6Ecj2Zt9o=',
        # 数据库地址，多数据库配置参见 env_test
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///./db.sqlite',
        # REDIS 地址，多 REDIS 配置参见 env_test
        'REDIS_URI': None,
    },
    # 用于信任的 MJST TOKEN，处于这个列表中的 MJST 不会因为过期被拒绝。
    'TRUSTED_TOKENS': [],
    # logger 实例配置
    'LOGGER': {
        # pyzog 是远程 logger 接收器： https://github.com/zrong/pyzog
        'pyzog': None,
        # 格式
        # 'pyzog': {
        #     'type': 'redis/zmq',
        #     'target': 'redis://:123456@127.0.0.1:6379/0',
        # }
    },
}


from .env_local import env_local
from .env_prod import env_prod


# 环境定义，将覆盖 config_json/uwsgi_ini/_env
enviroments = {
    'local': env_local,
    'prod': env_prod,
}
