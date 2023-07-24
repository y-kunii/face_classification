# coding: UTF-8
#######################################################
# 
# emotion.py
# 
#######################################################
from happymirror_const import *
import time

class Emotion:
    """
    感情データを蓄積し、最も強い感情や Happy の感情の割合などを計算します。
    """
    def __init__(self, accum_count = EMOTION_ACCUM_COUNT):
        self.__accum_count = accum_count
        self.__queue_emotions = [[0.0] * EMOTION_NUM]
        self.__reset_time_after_full = time.time() + EMOTION_RESET_TIME_AFTER_FULL

    def reset(self):
        """
        プロパティのリセット。
        """
        self.__queue_emotions = [[0.0] * EMOTION_NUM]

    def reset_after_full(self):
        """
        一度満点になった後、新しいアクションを起こすまでの間隔をリセットします。
        """
        self.reset()
        self.__reset_time_after_full = time.time()

    def accumurate(self, new_emotion):
        """
        新しい感情値を蓄積します。
        指定回数分取っておき、古いのから捨てていきます。
        """
        # 一度満点（レインボー表示）になった後は、少し間隔を空けるため、入力されたデータを読み捨てます。
        if (time.time() - self.__reset_time_after_full) < EMOTION_RESET_TIME_AFTER_FULL:
            return

        # 新しいデータを追加します。
        self.__queue_emotions.append(new_emotion)
        # データを最新からが指定個数より多い分は古いものを削除します。
        self.__queue_emotions = self.__queue_emotions[-self.__accum_count:]

    def no_faces(self):
        """
        顔を検出しなかった場合、全部 0 のデータを追加します。
        """
        new_emotion = [0.0] * EMOTION_NUM
        self.__queue_emotions.append(new_emotion)
        self.__queue_emotions = self.__queue_emotions[-self.__accum_count:]

    def __sum_emotions(self):
        """
        指定回数分取っておいた感情データで、
        感情ごとにデータを合計したリストを返します。
        """
        sum = [0.0] * EMOTION_NUM
#        print(f"__sum_emotions: {len(self.__queue_emotions)}")
#        print(self.__queue_emotions)
#        print("\n")
        for emotions in self.__queue_emotions:
            for index, value in enumerate(emotions):
                sum[index] += value
        return sum

    def get_largest_emotion_queue(self):
        """
        （指定回数分取っておくタイプ）
        蓄積された感情で最大のものを返します。
        戻り値は (int, double) 型のタプル。 (感情の番号, 感情の大きさ)
        感情の大きさは、全感情の合計からの割合としていますが、動作を見ながら調整した方が良いと思います。
        """
        emotions = self.__sum_emotions()
        largest_emotion = max(emotions)
        largest_index = emotions.index(largest_emotion)
        total = sum(emotions)
        if total == 0:
            largest_rate = 0
            largest_index = EMOTION_UNKNOWN
        else:
            largest_rate = largest_emotion / total
        return (largest_index, largest_rate)
