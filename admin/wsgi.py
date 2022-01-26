from pathlib import Path
from functools import partial
import pyape 
from pyape.config import GlobalConfig
from pyape.flask_extend import PyapeResponse


appdir = Path(__file__).parent.resolve()
gconfig = GlobalConfig(appdir)


class LotteryResponse(PyapeResponse):
    @property
    def cors_config(self):
        cors = PyapeResponse.CORS_DEFAULT.copy()
        cors['Access-Control-Allow-Headers'] = 'X-Requested-With, Content-Type'
        return cors


def setup_app(pyape_app, gdb):
    """ 初始化整个项目
    """
    # 创建所有数据库
    import pyape.app.models
    import app.models
    gdb.create_all()

    with pyape_app.app_context():
        # 初始化数据库内容
        app.models.init_from_xlsx()

    return pyape_app


def create_app(pyape_app, gdb):
    pyape_app.shell_context_processor(lambda: {
        'gdb': gdb,
        'setup': partial(setup_app, pyape_app, gdb),
    })
    pyape.app.logger.info(pyape_app.config)


lottery = pyape.init(gconfig, create_app, cls_config={'ResponseClass': LotteryResponse})
