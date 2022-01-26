# -*- coding: utf-8 -*-
"""
app.go.view
~~~~~~~~~~~~~~~~~~~

提供所有 /go 的视图方法
"""

from collections import OrderedDict, defaultdict
from tokenize import group
from flask import jsonify
from sqlalchemy import func, distinct


from pyape import gconfig
from pyape.app import vofun, checker, gdb, vofun
from pyape.app.re2fun import get_request_values, responseto
from pyape.util.func import parse_int

from app.models import Prize, User, Round, History

from . import go
from . import shuffle, write_xlsx, shift


wn = 'waiting_for_save'

def _get_lucky_users() -> list[list]:
    """ 获取已经获奖的用户列表"""
    # 查找已经获奖的用户
    lucky_users = User.query.\
        join(Round, User.user_id == Round.user_id).\
        filter(Round.user_id.isnot(None)).\
        with_entities(User.user_id, User.name, User.department, Round.level, Round.prize_id).\
        all()
    return lucky_users


def _get_left_users() -> list[list]:
    """ 获取没有获奖的用户列表"""
    # 查找已经获奖的用户
    lucky_users = _get_lucky_users()
    # 筛选出没有获奖的用户
    return [
        [ item.user_id, item.name, item.department ]
        for item in User.query.filter(~User.user_id.in_([user.user_id for user in lucky_users]))
    ]


def _get_prizes() -> tuple:
    """ 获取奖项"""
    # 获取每个奖项的奖品数量
    prize_records = Prize.query.\
        with_entities(Prize.level, Prize.level_name, Prize.prize_name, Prize.image_name, func.count(Prize.level).label('c')).\
        group_by(Prize.level).\
        order_by(Prize.level).\
        all()
    # 获取每个奖项的要进行几轮
    round_records = Round.query.\
        with_entities(Round.level, func.count(distinct(Round.round)).label('c')).\
        group_by(Round.level).\
        order_by(Round.level).\
        all()
        
    # 要加入一个特别奖前端代码才正常
    prizes = [
        {
            'type': 0,
            'count': 1000,
            'title': "",
            'text': "特别奖"
        }
    ]
    rounds = [1]
    for i in range(len(prize_records)):
        prize = prize_records[i]
        round = round_records[i]
        # 奖项轮数量和奖项中奖品数量相同，则每轮抽一个
        if round.c == prize.c:
            rounds.append(1)
        # 如果奖项轮数量是1，代表要一次把奖项所有奖品抽完
        elif round.c == 1:
            rounds.append(prize.c)
        # 否则就按照次数来抽
        else:
            rounds.append(round.c)
        prizes.append({
            'type': prize.level,
            'count': prize.c,
            'text': prize.level_name,
            'title': prize.prize_name,
            'img': f'../img/{prize.image_name}'
        })
    return rounds, prizes


def _update_round(round: int, prize_id:list[int], user_id: list[int]):
    """ 中奖人员名单更新"""
    rounds = Round.query.filter_by(round=round).all()
    for pid, uid in zip(prize_id, user_id):
        for round in rounds:
            if round.prize_id == pid:
                round.user_id = uid
                break
    gdb.session.add_all(rounds)
    gdb.session.commit()


def _update_round_by_saved():
    saved_vo = vofun.valueobject_get(0, None, wn, 1, 0, True)
    if saved_vo and not saved_vo.get('error'):
        waiting_for_save = saved_vo['vo']
        _update_round(waiting_for_save['round'], waiting_for_save['prize_id'], waiting_for_save['user_id'])
        # 更新后删除临时保存
        vofun.valueobject_del(vid=None, name=wn)
    

def _clear_saved_vo():
    saved_vo = vofun.valueobject_get(0, None, wn, 1, 0, True)
    if saved_vo and not saved_vo.get('error'):
        waiting_for_save = saved_vo['vo']
        hs = []
        for pid, uid in zip(waiting_for_save['prize_id'], waiting_for_save['user_id']):
            hs.append(History(user_id=uid, prize_id=pid, round=waiting_for_save['round']))
        gdb.session.add_all(hs)
        gdb.session.commit()
    vofun.valueobject_del(vid=None, name=wn)


@go.route('/lucky', methods=['POST'])
def lucky():
    """ 抽奖
    """
    round, clear = get_request_values('round', 'clear', request_key='json')
    round_rows = Round.query.\
        join(Prize, Prize.prize_id == Round.prize_id).\
        with_entities(Prize.prize_id, Prize.prize_name, Prize.level, Prize.level_name, Round.round).\
        filter(Round.round==round).\
        all()

    # 清除上次抽奖
    if clear:
        _clear_saved_vo()
    # 将缓存中的记录更新到 round 表中
    _update_round_by_saved()

    left_users = _get_left_users()
    lucky_indices = shift(len(round_rows), len(left_users))

    # 临时保存在 vo 对象中，下一次抽奖再保存
    waiting_for_save = {
        'round': round,
        'prize_id': [row.prize_id for row in round_rows],
        'user_id': [left_users[i][0] for i in lucky_indices],
    }
    
    lucky = []
    for i in range(len(round_rows)):
        user = left_users[lucky_indices[i]].copy()
        user.append(round_rows[i].prize_id)
        user.append(round_rows[i].prize_name)
        user.append(round_rows[i].level_name)
        lucky.append(user)

    vofun.valueobject_add(0, 0, wn, waiting_for_save , 0)
    return responseto(lucky=lucky)


@go.route('/update_saved', methods=['POST'])
def update_saved_vo():
    """ 从临时存储中向 round 表更新，一般在抽奖完毕后调用一次
    """
    _update_round_by_saved()
    return jsonify({'type': 'success'})

    
@go.route('/getTempData', methods=['POST'])
def gettempdata():
    rounds, prizes = _get_prizes()
    left_users = _get_left_users()
    shuffle(left_users)
    
    lucky_users = _get_lucky_users()
    lucky_data = defaultdict(list)
    for user in lucky_users:
        lucky_data[user.level].append([user.user_id, user.name, user.department])

    return responseto(cfgData={'prizes': prizes, 'EACH_COUNT': rounds, 'COMPANY': 'SAGI'}, 
        leftUsers=left_users,
        luckyData=lucky_data)


@go.route('/fodder', methods=['POST'])
def fodder():
    """ 初始化抽奖数据
    """
    # 将上一轮没有保存的临时抽奖数据更新到 round 表
    _update_round_by_saved()

    left_users = _get_left_users()
    shuffle(left_users)
    
    lucky_users = _get_lucky_users()
    lucky_data = defaultdict(list)
    for user in lucky_users:
        lucky_data[user.level].append([user.user_id, user.name, user.department])

    # 获取所有 Round
    round_prizes = Round.query.\
        join(Prize, Round.prize_id == Prize.prize_id).\
        with_entities(
            Prize.level,
            Prize.level_name,
            Prize.prize_id,
            Prize.prize_name,
            Prize.image_name, 
            Round.user_id,
            Round.round).\
        order_by(Round.round.asc()).\
        all()
    grouped = OrderedDict()
    for rp in round_prizes:
        round_value = grouped.get(rp.round)
        if round_value is None:
            grouped[rp.round] = {'round': rp.round, 'prize': []}
        grouped[rp.round]['prize'].append(gdb.to_response_data(rp))
    return responseto(round=list(grouped.values()), config={'COMPANY': 'SAGI'}, 
        left_users=left_users,
        lucky_users=lucky_data)
        

@go.route('/getUsers', methods=['POST'])
@go.route('/user', methods=['GET'])
def user():
    users = [
        [ item.user_id, item.name, item.department ]
        for item in User.query.all()
    ]
    shuffle(users)
    return jsonify(users)


@go.route('/saveData', methods=['POST'])
@go.route('/save', methods=['POST'])
def save():
    level, users = get_request_values('type', 'data', request_key='json')
    rounds = Round.query.filter_by(level=level).order_by(Round.prize_id).all()
    save_rounds = []
    for user in users:
        user_id = user[0]
        # print(f'user_id {user_id}')
        # save the user_id to round
        for round in rounds:
            if round.user_id is None:
                # print('None ', round.user_id, user_id)
                round.user_id = user_id
                save_rounds.append(round)
                break
    gdb.session.add_all(save_rounds)
    gdb.session.commit()
    return jsonify({'type': '设置成功'})


@go.route('/errorData', methods=['POST'])
@go.route('/history', methods=['POST'])
def history():
    users = get_request_values('data', request_key='json')
    save_users = [History(user_id=user[0]) for user in users]
    gdb.session.add_all(save_users)
    gdb.session.commit()
    return jsonify({'type': '设置成功'})


@go.route('/export', methods=['POST'])
@go.route('/export', methods=['GET'])
def export():
    """ 生成抽奖结果 Excel
    """
    results = Round.query.join(User, User.user_id == Round.user_id).\
        join(Prize, Prize.prize_id == Round.prize_id).\
        with_entities(Prize.prize_id, Prize.level_name, Prize.prize_name, User.user_id, User.name, User.department).\
        order_by(Prize.prize_id.asc()).\
        filter(Round.user_id.isnot(None)).\
        all()
    name = write_xlsx(['奖品ID', '奖项', '奖品名称', '编号', '名字', '部门'], results)
    url_path = gconfig.getcfg('PATH', 'STATIC_URL_PATH')
    return jsonify({
        'type': 'success',
        'url': f'{url_path}/{name}'
    })
    

@go.route('/reset', methods=['POST'])
@go.route('/reset', methods=['GET'])
def reset():
    """ 重置。需要清空 History 表，以及清空 Round 表中的 user_id
    """
    History.query.delete()
    Round.query.update({'user_id':None})
    vofun.valueobject_del(vid=None, name=wn)
    gdb.session.commit()
    return jsonify({'type': 'success'})