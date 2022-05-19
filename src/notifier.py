#######################################################
# 
# notifier.py
# 
#######################################################

import time

class Notifier:
    """
    通知を一定時間保持する（最後の通知からの経過時間を調べ、一定時間経過したら通知なしとみなす）
    ハートビートの検出、顔検出に使用する。
    """
    # 検出通知を維持する時間（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
    # この時間を超えて通知が届かなかった場合は、通知なしと判定する。
#    __hold_time_span = 1.0
    # 最後に検出した（notice()が実行された）時刻
#    __last_timestamp = 0.0

    def __init__(self, span = 1.0):
        """
        コンストラクタ
        """
        # 検出通知を維持する時間（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
        # この時間を超えて通知が届かなかった場合は、通知なしと判定する。
        self.__hold_time_span = span
        # 最後に検出した（notice()が実行された）時刻
        self.__last_timestamp = 0.0

    def init(self, span = 1.0):
        """
        初期化
        現在時刻を最後に通知があった時刻として設定する。
        """
        self.__last_timestamp = time.time()     # 最後の通知を現在時刻に設定する。

    def __calc_time_span(self):
        """
        最後の通知からの経過時間を返す（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
        """
        return time.time() - self.__last_timestamp

    def notice(self):
        """
        通知するときに呼び出すこと。
        呼び出された時の時刻を保存する。
        """
        self.__last_timestamp = time.time()

    def get(self):
        """
        通知検出の状態を返す。
          0: 一定時間内に検出していない
          1: 一定時間内に検出した
        """
        diff = self.__calc_time_span()
        if diff > self.__hold_time_span:
            notice_status = 0
        else:
            notice_status = 1
        return notice_status

