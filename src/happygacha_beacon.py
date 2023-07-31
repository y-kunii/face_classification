from bluetooth.ble import BeaconService
import RPi.GPIO as GPIO
import time

# 受信するビーコン
HAPPY_UUID          = "4a415341-2053-6d61-7274-4c6966655747"    # "JASA SmartLifeWG"
# 笑顔の時の Major ID
HAPPY_MAJOR         = 3             # ifLink ではエンディアンが違うので、笑顔の値（3）が 0x0300 となって届きます。
# 笑顔継続レベル
HAPPY_MINOR_FULL    = 100           # 100 → 0x64 → エンディアンをスワップして 0x6400
# 惜しいレベル（この値以上、HAPPY_MINOR_FULL 未満の場合惜しい反応をする。
HAPPY_MINOR_OSHII   = 51            #  51 → 0x33 → エンディアンをスワップして 0x3300

MOTOR_PORT          = 21            # ガチャモーターを回すための GPIO 番号
MOTOR_ON_SPAN       = 1.3           # ガチャモーターを回す時間（秒） ※動作を見ながら調整が必要


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


class Beacon(object):
    """
    取得したビーコンの情報を保持します。
    """
    def __init__(self, address, data):
        self._uuid = data[0]
        # Major, Minor（各 2 バイト）については、ifLink ではエンディアンが違うので、
        # Happy Mirror 側が送信時にそれぞれ値をスワップしています。
        # それに合わせるため、受信した値を再度スワップして元の値に戻します。
        self._major = swap_endian(data[1])
        self._minor = swap_endian(data[2])
        self._power = data[3]
        self._rssi = data[4]
        self._address = address


    def __str__(self):
#        ret = "Beacon: address:{ADDR} uuid:{UUID} major:{MAJOR}"\
#                " minor:{MINOR} txpower:{POWER} rssi:{RSSI}"\
#                .format(ADDR=self._address, UUID=self._uuid, MAJOR=self._major, 
#                        MINOR=self._minor, POWER=self._power, RSSI=self._rssi)
        ret = "Beacon: address:{ADDR} uuid:{UUID} major:{MAJOR} minor:{MINOR}"\
                .format(ADDR=self._address, UUID=self._uuid, MAJOR=self._major, MINOR=self._minor)
        return ret


    def get_property(self):
        """
        UUID, Major, Minor を返します。

        Returns
        -------
        uuid : string
            UUID
        major : int
            Major ID
        minor : int
            Minor ID
        """
        return (self._uuid, self._major, self._minor)


def init_gpio():
    """
    GPIO を初期化します。
    """
    # GPIO設定をリセット
    GPIO.cleanup()

    # GPIO 番号モードの設定
    GPIO.setmode(GPIO.BCM)                      # GPIO 番号指定。 GPIO.BOARD でピン番号指定になります。

    # 入出力設定
    GPIO.setup(MOTOR_PORT, GPIO.OUT)            # モーターを回すポートを出力ポートに設定します。


def reset_gpio():
    """
    GPIO をリセットします。
    """
    GPIO.cleanup()


def gacha(port, span):
    """
    ガチャを回します。

    Parameters
    ----------
    port : int
        制御する GPIO 番号
    span : float
        ガチャ（モーター）を回す時間（単位：秒）
    """
    print("Turn Gacha")
    print(f"GPIO{port} ON")
    GPIO.output(port, 1)
    print(f"Sleep {span} seconds...")
    time.sleep(span)
    print(f"GPIO{port} OFF")
    GPIO.output(port, 0)


###########################################################
# メイン処理
###########################################################

service = BeaconService()
init_gpio()

try:
    while True:
        print("scanning...")
        devices = service.scan(1)
        print(f"  {len(devices)} found.")
        if devices is None:
            continue

        # for address, data in list(devices.items()):
        for address, data in devices.items():
            beacon = Beacon(address, data)
            print(beacon)

            uuid, major, minor = beacon.get_property()
            if uuid != HAPPY_UUID:                  # Happy Mirror 以外のビーコンは無視します。
                continue

            if major == HAPPY_MAJOR:                # 笑顔の場合
                if minor >= HAPPY_MINOR_FULL:       # 「いい笑顔」のとき
                    gacha(MOTOR_PORT, MOTOR_ON_SPAN)
                    time.sleep(5.0)
                elif minor >= HAPPY_MINOR_OSHII:    # 「惜しい」とき
                    pass
                else:                               # 短時間で終わったとき
                    pass
            else:                                   # 笑顔以外の場合
                pass
except KeyboardInterrupt:           # Ctrl+C による例外をキャッチしたら終了処理します。
    GPIO.output(MOTOR_PORT, 0)
    reset_gpio()
    print("Done.")
