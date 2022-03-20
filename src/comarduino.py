import serial
#import struct

HEADER = 0xFF

# Arduino に送信するデータパケットを作成する
# 引数: leds		色 (probability, R, G, B) の値の配列を1行とした2次配列。出力したい数だけ行数を増やす。
# パケットのフォーマット：
#   HEADER  0xFF 固定
#   num     LED数
#   strength ┐
#   R        │ num の数だけ繰り返す
#   G        │
#   B        ┘
def make_packet(leds):
	packet = bytearray([HEADER])
	num = 0		
	packet.append(len(leds))	# 後続のデータの繰り返し数（＝LED数）

	#debug
#	print("len_leds = ", str(len(leds)))
#	print(leds)

	for i in range(len(leds)):
		# probability を強さ（0～3）に変換
		strength = int(leds[i][0] * 4)	# ！！とりあえず単純に probability を 4 等分する。よく取得される値の幅やLEDの光り方によって調整する。
		if strength > 3:					# 1.0 (100%) のときは 4 になってしまうので、3 にする。
			strength = 3
		packet.append(strength)

		# 色 R, G, B の追加：受け取ったデータをそのまま出力
		packet.extend(leds[i][1])

	return packet


# UART でデータを送信する
# 引数: packet	送信するデータのバイト配列
# ※1回送信する度に open/close することになるので、パフォーマンス次第では別途行うことも検討する。
def send_packet(packet):
	ser = serial.Serial('/dev/ttyS0', '9600', timeout=0.1)
	ser.reset_input_buffer()
	ser.reset_output_buffer()
	ser.write(packet)
	ser.close()
