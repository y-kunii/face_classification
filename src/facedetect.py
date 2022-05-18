#######################################################
# 
# FaceDetect.py
# Class FaceDetect
# 
#######################################################

import time

class FaceDetect:
    """
    顔を検出した情報（検出時刻）を保持する。
    """
    # 顔を検出したことを保持する時間（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
    # 顔検出がこの時間を超えて行われなかった場合は未検出（カメラの前から人がいなくなった等）と考える。
    hold_time_span = 2.0
    # 最後に検出した（detect()が実行された）時刻
    last_timestamp = 0.0

    def __init__(self):
        pass

    def init(self, span = 2.0):
        FaceDetect.hold_time_span = span
        FaceDetect.last_timestamp = time.time()  # 最後のハートビートを現在時刻に設定する。

    def __calc_time_span(self):
        """
        最後の顔検出からの経過時間を返す（整数部の単位：秒、浮動小数点数で1マイクロ秒単位で表現）
        起動直後など顔検出がまだ一度も届いていない場合は 0.0 を返す。
        """
        if FaceDetect.last_timestamp == 0.0:
            return FaceDetect.last_timestamp
        return time.time() - FaceDetect.last_timestamp

    def detect(self):
        """
        顔を検出した時に呼び出すこと。
        呼び出された時の時刻を保存する。
        """
        FaceDetect.last_timestamp = time.time()

    def get(self):
        """
        顔検出の状態を返す。
          0: 一定時間内に検出していない
          1: 一定時間内に検出した
        """
        diff = self.__calc_time_span()
        if diff > FaceDetect.hold_time_span:
            detect_status = 0
        else:
            detect_status = 1
        return detect_status

