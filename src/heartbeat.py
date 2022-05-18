#######################################################
# 
# HeartBeat.py
# Class HeartBeat
# 
#######################################################

import time

class HeartBeat:
    """
    ハートビート状態の保持
    """
    # ハートビートを維持する時間（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
    # ハートビートがこの時間を超えて届かなかった場合は動作に問題発生と考える。
    hold_time_span = 1.0
    # 最後にハートビート検出した（beat()が実行された）時刻
    last_timestamp = 0.0

    def __init__(self):
        pass

    def init(self, span = 1.0):
        HeartBeat.hold_time_span = span
        HeartBeat.last_timestamp = time.time()  # 最後のハートビートを現在時刻に設定する。

    def __calc_time_span(self):
        """
        最後のハートビートからの経過時間を返す（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
        起動直後などハートビートがまだ一度も届いていない場合は 0.0 を返す。
        """
        if HeartBeat.last_timestamp == 0.0:
            return HeartBeat.last_timestamp
        return time.time() - HeartBeat.last_timestamp

    def beat(self):
        """
        ハートビート通知するときに呼び出すこと。
        呼び出された時の時刻を保存する。
        """
        HeartBeat.last_timestamp = time.time()

    def get(self):
        """
        ハートビート検出の状態を返す。
          0: 一定時間内に検出していない
          1: 一定時間内に検出した
        """
        diff = self.__calc_time_span()
        if diff > HeartBeat.hold_time_span:
            hb_status = 0
        else:
            hb_status = 1
        return hb_status

