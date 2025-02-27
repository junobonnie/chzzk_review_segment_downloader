# 치지직 다시보기 구간 다운로더

https://github.com/user-attachments/assets/dbc24757-eabd-4a9a-a470-d74272f0ea36


## 다운로드 링크
# [Download for windows](https://github.com/junobonnie/chzzk_review_segment_downloader/releases/download/v1.1.0/v1.1.0.zip)

<br>

## 성인 영상 다운로드 방법

성인 영상 다운로드 시 사용자 계정의 NID 값이 필요합니다.

### NID_AUT, NID_SES 값 얻는 법
![스크린샷 2025-01-13 133549](https://github.com/user-attachments/assets/6e1c9e52-490a-4a00-9cba-ae741837fb0e)

엣지 기준: `로그인한 치지직 화면 > F12 > 응용프로그램 > 쿠키`

<br>

## 라이센스 및 출처 관련
 - 이 프로그램은 LGPL 라이센스를 갖는 ffmpeg의 바이너리를 포함하고 있습니다.
 - https://gall.dcinside.com/mgallery/board/view/?id=hejin0_0&no=28710
   
   해당 게시글의 코드를 참고 하였습니다.

## 빌드 방법
```
pyinstaller --noconfirm --onefile --windowed --icon "icon.ico" --upx-dir "D:\upx-4.0.2-win64" --add-data "ffmpeg.exe;ffmpeg_bin"  "gui.py"
```
