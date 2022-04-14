# EmotionFlower dockerインストール説明

## RaspberryPiにdockerをインストールする（3でも4でも可だが、32bitのみ）

おまじない（必要ない場合もある）
```bash
sudo apt-get update --allow-releaseinfo-change
```
[参考]<https://raspida.com/rpi-buster-error> 

下記コマンドでインストールする  
```bash
curl -sSL https://get.docker.com | sh  
```
[参考]<https://qiita.com/k_ken/items/0f2d6af2618618982723>  

ユーザ追加
```bash
sudo usermod -aG docker pi 
```
自動起動
```bash
sudo systemctl enable docker
```

ここまでで、一回Rebootしておく。  
下記の、いつものお試しhello-worldを動かして、dockerが正常に動作していることを確認。
```bash
docker run hello-world
```

## docker imageの作成
下記にある公式raspbianのImageをベースとする。  
<https://hub.docker.com/r/raspbian/stretch>
下記コマンドで、pullしておく。
```bash
docker pull raspbian/stretch:latest
```
Image作成（Dockerfileのある場所で、下記コマンド実行）
```bash
docker build -t emotionflower:ver7 .
```
Imageの確認（下記コマンドで、emotionflower:ver4がいること）
```bash
docker images
```

/home/pi/smartlife以下に下記をcloneしておく。（コンテナでマウントしているので、コンテナ内で見える様になる）  
https://github.com/y-kunii/face_classification

コンテナ作成
```bash
docker run -it -d -e DISPLAY=${DISPLAY} -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.Xauthority:/root/.Xauthority -v/home/pi/smartlife:/home/emotion --device=/dev/video0:/dev/video0 --device=/dev/mem:/dev/mem --net=host  emotionflower:ver7 bash
```
コンテナに入る（docker psコマンドでコンテナIDを確認しておく）
```bash
docker exec -it コンテナID bash
```
起動後やっておくといいこと  
sshのrestart
```bash
service ssh restart
```
videoのportの権限変更（これをしないとUSBカメラが使えない）
```bash
sudo chmod a+rw /dev/video0
```

## 困ったときは
* sshがうまくつながらない  
/etc/ssh/sshd_configのPort番号を確認し、ホスト側でlsof -iでPortが利用されていないことを確認する。  
使用されていたら、該当プロセスをkillするか、Port番号を変更してsshをrestartする。
* GUIがでない。その１。  
ホスト側で、sudo xhost +を実行し、xwindowの表示をできるようにする。  
* GUIがでない。その２。  
ホスト側でDISPLAY環境変数が正しく設定されていることを確認する。  
whoコマンドで確認できる。
dockerコンテナないで、xeyesを実行し、GUIが出る確認をする。
* pythonのScriptでASCIIで怒られたとき。  
下記を実行  
```bash
export PYTHONIOENCODING=utf-8
```
* emotionユーザのパスワードがわからなく、SSH接続できない。  
パスワードはユーザ名と同じです。

## 制限事項
* EmotionFlowerが動くRaspberryPiのImageをベースにフォルダのマウントをしています。  
  もし、新規の環境を作る場合には、コンテナ内でgit cloneするなど、Scriptを準備してください。
* LEDの制御までまだできていません。LED制御以外のvideo_emotion_color_demo.pyを実行し、  
カメラで認識した感情分類が動作するところまで、確認しています。  
* dockerのせいなのか、動作が重い可能性があります。  








