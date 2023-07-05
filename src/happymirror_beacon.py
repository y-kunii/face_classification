# coding: UTF-8
#######################################################
#
# happymirror_beacon.py
#
# HappyMirror 用 iBeacon 送信
#
# ifLink の if として使用します。
#
#######################################################
from bluetooth.ble import BeaconService
import time
from happymirror_const import *

def swap_endian(src):
    """
    16 ビット（2 バイト）整数の上位 1 バイトと下位 1 バイトを入れ替えます。

    Parameters
    ----------
    src : int
        変換元の数値
    
    Returns
    -------
    result : int
        返還後の値
    """
    result = src & 0xFFFF   # 16 ビットより上位の値は削除します。
    return ((result & 0xFF00) >> 8) + ((result & 0x00FF) << 8)


def send_iBeacon(emotion, level=0):
    """
    iBeacon プロトコルで表情を通知します。

    Parameters
    ----------
    emotion : int
        EMOTION_*** で定義した感情値（EMTION_ANGRY:angry, EMOTION_HAPPY:happy, 等）
    level : int
        感情の強さ、ON/OFF、続いた長さなど
    """
    service = BeaconService()

    # UUID は "JASA SmartLifeWG" を ASCII コードに変換したものにしています。
    # 固定にしていますが、変更可能です。（16 バイト）
    UUID = "4A415341-2053-6D61-7274-4C6966655747"
    # major, minor は 16 ビットの値で、エンディアンを逆にする必要があります。
    # 例えば 3 を送りたければ 0x0300 を送ります。
    major = swap_endian(emotion)
    minor = swap_endian(level)

    # アドバタイズパケット送信
    # おそらく 200ms 周期で送信しています。
    print(f"Sending iBeacon: {major}-{minor}...")    # debug
    service.start_advertising(UUID, major, minor, 1, 200)

    # しばらく待ってアドバタイズパケット停止
    # 1 発だけ送信するのは難しい？
    time.sleep(0.5)
    service.stop_advertising()


if __name__ == "__main__":
    # デバッグ用メインコード
    send_iBeacon(EMOTION_HAPPY, 1)          # 笑顔が続いたよ
    time.sleep(5)

    send_iBeacon(EMOTION_HAPPY, 0)          # level パラメータ違い
    time.sleep(5)

    send_iBeacon(EMOTION_ANGRY, 1)          # 怒ってるよ
    time.sleep(5)

    send_iBeacon(EMOTION_SAD, 1)            # 悲しんでるよ
    time.sleep(5)

    send_iBeacon(EMOTION_UNKNOWN, 1)        # 不明
