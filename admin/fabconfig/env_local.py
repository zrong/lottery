env_local = {
    'deploy_dir': 'N/A',
    '_env': {
        'FLASK_ENV': 'development',
        'FLASK_RUN_PORT': 5001,
        'FLASK_RUN_WITH_THREADS': 1,
    },
    'uwsgi_ini': {
        'socket': '127.0.0.1:5000',
        'daemonize': False,
    },
    'config_json': {
        'FLASK': {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///Users/zrong/storage/zrong/lottery/admin/db.sqlite',
        },
        'PATH': {
            'STATIC_FOLDER': 'dist',
            'STATIC_URL_PATH': '/static',
            'modules': {
                'cf': '/cf',
            }
        },
    },
}
