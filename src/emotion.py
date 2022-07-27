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
        self.__emotions = [0.0] * EMOTION_NUM
        self.__accum_count = accum_count
        self.__queue_emotions = [[0.0] * EMOTION_NUM]
        self.__reset_time_after_full = time.time() + EMOTION_RESET_TIME_AFTER_FULL

    def reset(self):
        """
        プロパティのリセット。
        """
        self.__emotions = [0.0] * EMOTION_NUM
        self.__queue_emotions = [[0.0] * EMOTION_NUM]

    def reset_after_full(self):
        """
        一度満点になった後、新しいアクションを起こすまでの間隔をリセットします。
        """
        self.reset()
        self.__reset_time_after_full = time.time()

    def reset_sum(self):
        """
        感情値の合計のみリセットします。
        """
        self.__emotions = [0.0] * EMOTION_NUM

    def accumurate(self, new_emotion):
        """
        新しい感情値を蓄積します。
        データを加算していくタイプ（前半のコード）がいいか、
        指定回数分取っておき、古いのから捨てていくタイプ（後半のコード）のがいいか。
        """
        # 一度満点（レインボー表示）になった後は、少し間隔を空けるため、入力されたデータを読み捨てます。
        if (time.time() - self.__reset_time_after_full) < EMOTION_RESET_TIME_AFTER_FULL:
            return

#        self.__emotions = [x + y for x, y in zip(self.__emotions, new_emotion)]
        for index, value in enumerate(new_emotion):
            self.__emotions[index] += value

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
        # if len(self.__queue_emotions) > self.__accum_count:
        #     del self.__queue_emotions[0]

    def __sum_emotions(self):
        """
        指定回数分の感情データを取っておくタイプの場合で、
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

    def get_largest_emotion(self):
        """
        蓄積された感情で最大のものを返します。
        戻り値は (int, double) 型のタプル。 (感情の番号, 感情の大きさ)
        感情の大きさは、全感情の合計からの割合としていますが、動作を見ながら調整した方が良いと思います。
        """
        largest_emotion = max(self.__emotions)
        largest_index = self.__emotions.index(largest_emotion)
        total = sum(self.__emotions)
        if total == 0:
            largest_rate = 0
        else:
            largest_rate = largest_emotion / sum(self.__emotions)
        return (largest_index, largest_rate)

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
            largest_rate = largest_emotion / sum(emotions)
        return (largest_index, largest_rate)

    def get_emotion_ratio(self, index = EMOTION_HAPPY):
        """
        蓄積された感情の中で index で指定された感情の割合を返します。
        戻り値は double 型。
        感情の大きさは、全感情の合計からの割合としています。
        index = EMOTION_HAPPY として Happy の割合を返すことを目的にしています。
        """
        total = sum(self.__emotions)
        if total == 0:
            ratio = 0
        else:
            ratio = self.__emotions[index] / sum(self.__emotions)
        return ratio

    def get_emotion_ratio_queue(self, index = EMOTION_HAPPY):
        """
        （指定回数分取っておくタイプ）
        蓄積された感情の中で index で指定された感情の割合を返します。
        戻り値は double 型。
        感情の大きさは、全感情の合計からの割合としています。
        index = EMOTION_HAPPY として Happy の割合を返すことを目的にしています。
        """
        emotions = self.__sum_emotions()
        total = sum(emotions)
        if total == 0:
            ratio = 0
        else:
            ratio = emotions[index] / sum(emotions)
        return ratio

