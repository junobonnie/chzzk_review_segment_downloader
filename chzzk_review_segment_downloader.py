# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 21:31:20 2025

@author: replica
"""

# @title 필요 라이브러리 불러오기
import re
import json
import requests
import xml.etree.ElementTree as ET
import time
import subprocess
import os
import sys

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):  # 실행 파일로 빌드된 경우
        return os.path.join(sys._MEIPASS, "ffmpeg_bin", "ffmpeg.exe")
    return "ffmpeg"  # 개발 중에는 시스템 FFmpeg 사용

def progress_print(progress):
    print(f"\rDownloading... {progress:.2f}%")

def speed_print(speed):
    print(f"Speed: {speed} kB/s")

class ChzzkStreamExtractor:
    VOD_URL = "https://apis.naver.com/neonplayer/vodplay/v2/playback/{video_id}?key={in_key}"
    VOD_INFO = "https://api.chzzk.naver.com/service/v2/videos/{video_no}"
    
    def __init__(self, message = print, progress_update = progress_print, speed_update = speed_print):
        self.message = message
        self.progress_update = progress_update
        self.speed_update = speed_update
        self.NID_AUT = ""
        self.NID_SES = ""
        self.download_path = "./"

    def extract_streams(self, link, start_time, end_time, start_time_str, end_time_str, download_path):
        if not download_path == "":
            self.download_path = download_path
        match = re.match(r'https?://chzzk\.naver\.com/(?:video/(?P<video_no>\d+)|live/(?P<channel_id>[^/?]+))$', link)
        if not match:
            self.message("Invalid link\n")
            return

        video_no = match.group("video_no")
        return self._get_vod_streams(video_no, start_time, end_time, start_time_str, end_time_str)
    
    @staticmethod
    def _get_download_speed(log):
        """FFmpeg 로그에서 다운로드 속도를 추출 (speed=1.2x 같은 값 활용)"""
        match = re.findall(r"speed=([\d\.]+)x", log)
        if match:
            return float(match[-1]) * 1024  # KB/s로 변환
        return None

    def download_video(self, video_url, output_path, start_time, end_time):
        total_duration = end_time - start_time
        if total_duration <= 0:
            self.message("잘못된 구간입니다. (end_time이 start_time보다 커야 함)")
            return
    
        command = [
            get_ffmpeg_path(), "-y", "-ss", str(start_time), "-i", video_url,
            "-to", str(end_time - start_time), "-c", "copy", output_path,
            "-progress", "pipe:2", "-nostats"
        ]
    
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
            text=True,  # Python 3.7 이상에서는 universal_newlines=True 대신 사용
            bufsize=1,  # 줄 단위로 즉시 출력
            encoding="utf-8",
            creationflags=0x08000000
        )
    
        while True:
            if process.poll() is not None:
                break
    
            line = process.stderr.readline()
            if not line:
                time.sleep(0.1)
                continue
    
            decoded_line = line.strip()
    
            if 'out_time_ms=' in decoded_line:
                match = re.search(r'out_time_ms=(\d+)', decoded_line)
                if match:
                    current_time = int(match.group(1)) / 1_000_000
                    if current_time > total_duration:
                        current_time = total_duration
                    progress = (current_time / total_duration) * 100
                    self.progress_update(progress)
                    # sys.stdout.flush()  # 추가
                
            speed = self._get_download_speed(decoded_line)
            if speed:
                self.speed_update(speed)
    
        process.wait()
        self.message("\nDownload completed!\n")


    def _print_dash_manifest(self, video_url):
        try:
            response = requests.get(video_url, headers={"Accept": "application/dash+xml"})
            response.raise_for_status()
            root = ET.fromstring(response.text)
            ns = {"mpd": "urn:mpeg:dash:schema:mpd:2011", "nvod": "urn:naver:vod:2020"}
            base_url_element = root.find(".//mpd:BaseURL", namespaces=ns)
            if base_url_element is not None:
                return base_url_element.text
            else:
                self.message("BaseURL not found in DASH manifest\n")
        except requests.RequestException as e:
            self.message("Failed to fetch DASH manifest:" + str(e) + "\n")
        except ET.ParseError as e:
            self.message("Failed to parse DASH manifest XML:" + str(e) + "\n")

    def _get_vod_streams(self, video_no, start_time, end_time, start_time_str, end_time_str):
        api_url = self.VOD_INFO.format(video_no=video_no)
        UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        try:
            if self.NID_AUT == ""  or self.NID_SES =="":
                response = requests.get(api_url, headers={"User-Agent": UserAgent})
            else:
                response = requests.get(api_url, cookies={"NID_AUT":self.NID_AUT, "NID_SES":self.NID_SES}, headers={"User-Agent": UserAgent})
            response.raise_for_status()
        except requests.RequestException as e:
            self.message("Failed to fetch video information:" + str(e) + "\n")
            return

        if response.status_code == 404:
            self.message("Video not found\n")
            return

        try:
            content = response.json().get('content', {})
            video_id = content.get('videoId')
            in_key = content.get('inKey')
            if video_id is None or in_key is None:
                self.message("This is a need to login video." + "\n")
                cookies = self._load_cookies_from_file("cookies.json")
                if cookies is not None:
                    response = requests.get(api_url, cookies=cookies, headers={"User-Agent": UserAgent})
                    response.raise_for_status()
                    content = response.json().get('content', {})
                    video_id = content.get('videoId')
                    in_key = content.get('inKey')

            video_url = self.VOD_URL.format(video_id=video_id, in_key=in_key)
            author = content.get('channel', {}).get('channelName')
            category = content.get('videoCategory')
            title = content.get('videoTitle')
            self.message(f"Author: {author}, Title: {title}, Category: {category}")
            base_url = self._print_dash_manifest(video_url)
            if base_url:
                title = self.clean_filename(title)
                output_path = f"{self.download_path}/{title}_{start_time_str.replace(':', '-')}_{end_time_str.replace(':', '-')}.mp4"
                self.download_video(base_url, output_path, start_time, end_time)
                # self.move_to_drive(output_path)
        except json.JSONDecodeError as e:
            self.message("Failed to decode JSON response:" + str(e))

    def _load_cookies_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                cookies = json.load(file)
            return cookies
        except FileNotFoundError:
            self.message(f"Cookie file not found: {file_path}" + "\n")
            return None
        except json.JSONDecodeError:
            self.message(f"Error decoding JSON from file: {file_path}" + "\n")
            return None

    @staticmethod
    def clean_filename(filename):
        cleaned_filename = re.sub(r'[♥♡ღ⭐㉦✧》《♠♦❤️♣✿ꈍᴗ\/@!~*\[\]\#\$\%\^\&\(\)\-\_\=\+\<\>\?\;\:\'\"]', '', filename)
        return cleaned_filename

    # def move_to_drive(self, file_path):
    #     drive_path = './'
    #     if not os.path.exists(drive_path):
    #         os.makedirs(drive_path)
    #     file_name = os.path.basename(file_path)
    #     drive_file_path = os.path.join(drive_path, file_name)
    #     shutil.move(file_path, drive_file_path)
    #     self.message(f"File moved to: {drive_file_path}")

def convert_time_to_seconds(time_str, message = print):
    try:
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except ValueError:
        message("Invalid time format. Use hh:mm:ss")
        return None

# link_input = widgets.Text(
#     value='',
#     placeholder='Enter the link',
#     description='Link:',
#     disabled=False
# )

# start_time_input = widgets.Text(
#     value='00:00:00',
#     placeholder='Start time in hh:mm:ss',
#     description='Start Time:',
#     disabled=False
# )

# end_time_input = widgets.Text(
#     value='00:01:00',
#     placeholder='End time in hh:mm:ss',
#     description='End Time:',
#     disabled=False
# )

# download_button = widgets.Button(
#     description='Download',
#     disabled=False,
#     button_style='',
#     tooltip='Click to download video',
#     icon='download'
# )

# display(link_input, start_time_input, end_time_input, download_button)

# def on_download_button_clicked(b):
#     link = link_input.value
#     start_time_str = start_time_input.value
#     end_time_str = end_time_input.value
#     start_time = convert_time_to_seconds(start_time_str)
#     end_time = convert_time_to_seconds(end_time_str)
#     if link and start_time is not None and end_time is not None:
#         ChzzkStreamExtractor.extract_streams(link, start_time, end_time, start_time_str, end_time_str)
#     else:
#         print("Please provide valid inputs")

# download_button.on_click(on_download_button_clicked)

if __name__ == "__main__":
    CSE = ChzzkStreamExtractor()
    CSE.NID_AUT, CSE.NID_SES = "", ""
    link = "https://chzzk.naver.com/video/5845060"
    start_time_str = "01:00:05"
    end_time_str = "01:05:55"
    start_time = convert_time_to_seconds(start_time_str)
    end_time = convert_time_to_seconds(end_time_str)
    if link and start_time is not None and end_time is not None:
        CSE.extract_streams(link, start_time, end_time, start_time_str, end_time_str, "")
    else:
        print("Please provide valid inputs")
    
