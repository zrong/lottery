#====================================
# 使用 Gunicorn 部署 pyape 实例时候的配置文件
# 2020-05-17
# author: zrong
#====================================
import multiprocessing
import os          

wsgi_app = 'wsgi:pyape_app'
user = 'app'
group = 'app'
workers = multiprocessing.cpu_count() * 2 + 1
daemon = False