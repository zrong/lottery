# -*- coding: utf-8 -*-
"""
app.cf.vo
~~~~~~~~~~~~~~~~~~~

提供所有 /cf/vo 的视图方法
"""

from pyape.app import vofun, checker
from pyape.app.re2fun import get_request_values, responseto
from pyape.util.func import parse_int

from . import cf


@cf.route('/vo', methods=['GET'])
@checker.request_values('vid', 'name', 'merge', 'withcache', 
    defaultvalue={'merge': 0, 'withcache': 0}, request_key='args', 
    parse_int_params=['merge', 'withcache'])
def vo_get(vid, name, merge, withcache):
    return vofun.valueobject_get(0, vid, name, merge, withcache)


@cf.route('/vo', methods=['POST'])
def valueobject_add():
    data = get_request_values(request_key='json')
    if isinstance(data, dict):
        withcache = data.get('withcache')
        if withcache is not None:
            withcache = parse_int(withcache, 0)
            del data['withcache']
        else:
            withcache = 0

        name = data.get('name')
        value = data.get('value')
        votype = data.get('votype')
        if name is not None:
            del data['name']
        if value is not None:
            del data['value']
        if votype is not None:
            del data['votype']

        return vofun.valueobject_add(0, withcache, name, value, votype, **data)
    return responseto('参数不正确', code=401)


@cf.route('/vo', methods=['PUT'])
def valueobject_edit():
    data = get_request_values(request_key='json')
    if isinstance(data, dict):
        withcache = data.get('withcache')
        if withcache is not None:
            withcache = parse_int(withcache, 0)
            del data['withcache']
        else:
            withcache = 0
        return vofun.valueobject_edit(0, withcache, **data)
    return responseto('参数不正确', code=401)


@cf.route('/vo', methods=['DELETE'])
def vo_del():
    vid, name = get_request_values('vid', 'name', request_key='json')
    return vofun.valueobject_del(vid, name)
