deploy_dir = '/srv/app/lottery'

env_prod = {
    'deploy_dir': deploy_dir,
    '_env': {
        'FLASK_ENV': 'production',
    },
    'gunicorn_conf_py': {
        'chdir': deploy_dir,
        'workers': 2,
        'threads': 2,
        'bind': f'unix:{deploy_dir}/gunicorn.sock',
        'pidfile': f'{deploy_dir}/gunicorn.pid',
        'accesslog': f'{deploy_dir}/logs/access.log',
        'errorlog': f'{deploy_dir}/logs/error.log',
    },
    'config_json': {
        'FLASK': {
            'SECRET_KEY': '{LOTTERY_PROD_SECRET_KEY}',
            'SQLALCHEMY_DATABASE_URI': '{LOTTERY_PROD_SQLALCHEMY_DATABASE_URI}',
        },
        'PATH': {
            'STATIC_FOLDER': 'dist',
            'STATIC_URL_PATH': '/lottery/static',
            'modules': {
                'cf': '/lottery/cf',
                'go': '/lottery/go',
            }
        },
    },
    'config_json_value_environ_replacer': {
        'FLASK': {
            'SECRET_KEY': 'LOTTERY_{}_SECRET_KEY',
            'SQLALCHEMY_DATABASE_URI': 'LOTTERY_{}_SQLALCHEMY_DATABASE_URI',
        }
    }
}
