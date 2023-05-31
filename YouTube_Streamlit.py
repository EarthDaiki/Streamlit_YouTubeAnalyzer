#https://youtubeexpert-earthstation.streamlit.app/

import streamlit as st
import subprocess
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
from yt_dlp import YoutubeDL
import os

Filename=None
TimeStampList = []
AuthorNameList = []
CommentList = []
TimeListConverted = []

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 500)
pd.set_option("display.max_colwidth", 200)

st.set_page_config(
    page_title='YouTubeAnalyzer🔥', 
    page_icon="./data/MetaHumanIcon.png", 
    layout="centered", 
    initial_sidebar_state="auto", 
    menu_items={
        "Get help": "https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md#supported-sites",
        "Report a Bug": "https://twitter.com/_EarthStation_",
        'About': "詳細はこちら:"
        }
    )

@st.cache_data
def DownloadLiveChat(url):
    #try:
    # Livechat = f"youtube-dl --skip-download --write-sub --sub-lang live_chat --get-filename --restrict-filenames {url}"
    # command = f"youtube-dl --skip-download --write-sub --sub-lang live_chat --restrict-filenames {url}"
    # Livechat = subprocess.run(Livechat, capture_output=True, text=True, encoding='utf-8', shell=True).stdout.strip()
    # FileName = subprocess.run(command, shell=True)
    ydl_options={
        'writesubtitles': True,
        'subtitleslangs': ['live_chat'],
        'skip_download': True
    }
    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        Livechat = ydl.prepare_filename(info)
        ydl.download([url])

    return Livechat

def FindAuthor(line):
    try:
        Author = line['replayChatItemAction']['actions'][0]['addChatItemAction']['item']['liveChatTextMessageRenderer']['authorName']['simpleText']
    except:
        Author = "YOUTUBE SYSTEM"
    return Author


def FindElements(Livechat):
    count = 0
    Livechat = Livechat.replace(".webm", ".live_chat.json")
    # LivechatFileName = f"{Livechat}.live_chat.json"
    # print(LivechatFileName)
    with open(Livechat, encoding="utf-8") as f:
        for line in f:
            line = json.loads(line)
            Author = FindAuthor(line)
            try: 
                TimeStamp = line["replayChatItemAction"]["actions"][0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["timestampText"]["simpleText"]
                Emojis = line['replayChatItemAction']['actions'][0]['addChatItemAction']['item']['liveChatTextMessageRenderer']['message']['runs']
                Text = ""
                EmojiComment = ""
                for Emoji in Emojis:
                    if 'emoji' in Emoji:
                        EmojiComment = EmojiComment + Emoji['emoji']['emojiId']
                    if 'text' in Emoji:
                        Text = Text + Emoji['text']
                    Comment = Text + EmojiComment
                if Text == "":
                    Text = "None"
                if EmojiComment == "":
                    EmojiComment = "None"
                # print(f"{TimeStamp} // {Author} // {Text} // {EmojiComment}")
                if (not TimeStamp.startswith("-")):
                    TimeStampList.append(TimeStamp)
                    AuthorNameList.append(Author)
                    CommentList.append(Comment)
            except:
                count += 1
                print(f'ERROR COUNT {count}')
    return Livechat

def ShowCommentCount(Livechat):
    for time in TimeStampList:
        if len(time) == 4:
            time = '00:0' + time
        elif len(time) == 5:
            time = '00:' + time
        TimeListConverted.append(time)

    df = pd.DataFrame({
            'Author': AuthorNameList,
            'Comment': CommentList,
            'TimeStamp': TimeListConverted,
        })
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format='%H:%M:%S')
    df['TimeStamp'] = df['TimeStamp'].dt.time
    df.to_csv(f"{Livechat}.csv", index=False)

    csv_df = pd.read_csv(f"{Livechat}.csv")
    csv_df['TimeStamp'] = pd.to_datetime(csv_df['TimeStamp'])
    csv_df.set_index('TimeStamp', inplace=True)

    # リサンプリングしてカウント
    counts = csv_df.resample(f"{Interval}{ScaleUnit}").count()
    counts.index = counts.index.strftime("%H:%M:%S")

    return csv_df, counts

def DuplicatedAuthorCount(csv_df):
    counts = csv_df['Author'].resample(f"{Interval}{ScaleUnit}").apply(list)
    author_duplicates = counts.apply(lambda x: len(x) - len(set(x)))
    AuthorDuplicates = pd.DataFrame({'AuthorDuplicates': author_duplicates})

    author_duplicates.plot()
    plt.minorticks_on()
    plt.grid()
    plt.show()
    # 結果を表示
    print(AuthorDuplicates.sort_values('AuthorDuplicates', ascending=False))

def DuplicatedCommentCount(csv_df):
    counts = csv_df['Comment'].resample(f"{Interval}{ScaleUnit}").apply(list)
    comment_duplicates = counts.apply(lambda x: len(x) - len(set(x)))
    CommentsDuplicates = pd.DataFrame({'CommentsDuplicates': comment_duplicates})

    comment_duplicates.plot()
    plt.minorticks_on()
    plt.grid()
    plt.show()
    # 結果を表示
    print(CommentsDuplicates.sort_values('CommentsDuplicates', ascending=False))

def ShowChart(counts):
    st.line_chart(counts)

def ShowTables(counts):
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(counts)
    with col2:
        st.dataframe(counts.sort_values('Comment', ascending=False))

def GetTimeStamp(Interval, counts):
    Seconds_StartTime = 0
    Seconds_EndTime = 0
    LivechatVideoDownload = False
    for i, HotTimeStamp in enumerate(counts.sort_values('Comment', ascending=False).head(Number).index, 1):
        if ScaleUnit == 'H':
            TimeDelta_Interval = datetime.timedelta(hours=Interval)
        elif ScaleUnit == 'T':
            TimeDelta_Interval = datetime.timedelta(minutes=Interval)
        elif ScaleUnit == 'S':
            TimeDelta_Interval = datetime.timedelta(seconds=Interval)
        Time = datetime.datetime.strptime(HotTimeStamp, "%H:%M:%S")
        DateTime_StartTime = Time - datetime.timedelta(seconds=VideoStartTime)
        if DateTime_StartTime < datetime.datetime.strptime("00:00:00", "%H:%M:%S"):
            DateTime_StartTime = datetime.datetime.strptime("00:00:00", "%H:%M:%S")
        DateTime_EndTime = Time + TimeDelta_Interval + datetime.timedelta(seconds=VideoEndTime)
        if DateTime_EndTime > datetime.datetime.strptime("23:59:59", "%H:%M:%S"):
            DateTime_EndTime = datetime.datetime.strptime("23:59:59", "%H:%M:%S")

        Str_StartTime = DateTime_StartTime.strftime("%H:%M:%S")
        Str_EndTime = DateTime_EndTime.strftime("%H:%M:%S")
        Seconds_StartTime = datetime.timedelta(hours=DateTime_StartTime.hour, minutes=DateTime_StartTime.minute, seconds=DateTime_StartTime.second).total_seconds()
        Seconds_EndTime = datetime.timedelta(hours=DateTime_EndTime.hour, minutes=DateTime_EndTime.minute, seconds=DateTime_EndTime.second).total_seconds()

        st.markdown(f"\n**{i}個目**")
        st.markdown(f"**StartTime:** {Str_StartTime}, **EndTime:** {Str_EndTime}")
        # st.text(f"StartTime: {int(Seconds_StartTime)}")
        # st.text(f"EndTime: {int(Seconds_EndTime)}")

        GetVideos(Seconds_StartTime, Seconds_EndTime)
        Format = st.radio('**形式を選んでください**', ('webm', 'mp4', 'mp4+m4a(スマートフォンの場合はこちらを選択してください)'), horizontal=True, key=f'livechat{i}', help='スマートフォンからアクセスの場合はmp4選択してください')
        LivechatVideoDownload = st.button(f'ダウンロード{i}',help='こちらでの部分的なダウンロードはまだ開発途中のため音声や映像がずれる場合があります。  \n結果を確認しながら、下の"動画ダウンロード"で全体をダウンロードして、ご自身でトリムすることをお勧めします。')
        if LivechatVideoDownload:
            return i, Seconds_StartTime, Seconds_EndTime, LivechatVideoDownload, Format
    return i, Seconds_StartTime, Seconds_EndTime, LivechatVideoDownload, Format

def GetVideos(Seconds_StartTime, Seconds_EndTime):
    VideoUrl = f"https://www.youtube.com/embed/{VideoId}?start={int(Seconds_StartTime)}&end={int(Seconds_EndTime)}"
    st.text(VideoUrl)
    # st.video(VideoUrl, format="video/mp4")
    video_embed = f'<iframe width="560" height="315" src="{VideoUrl}" frameborder="0" allowfullscreen></iframe>'
    st.markdown(video_embed, unsafe_allow_html=True)
    

def ErrorMessage(Error):
    if Error == "FilledIn":
        st.error('記入されていない項目があります')
    elif Error == "URL":
        st.error('URLの処理でエラーが起きました')
    elif Error == "Livechat":
        st.error('Livechatが存在しません')
    elif Error == "Replay":
        st.error("リプレイ情報が存在しません")
    elif Error == "Convert":
        st.error('mp4にコンバートする際にエラーが起きました')

@st.cache_data
def GetMostReplayedFromBrowser():
    url = f'https://yt.lemnoslife.com/videos?part=mostReplayed&id={VideoId}'
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')
    HTMLText = soup.text
    HTMLText = HTMLText.replace(" ", "").replace("\n", "")
    json_data = json.dumps(HTMLText)
    return json_data

def FormatMostReplayed(json_data):
    with open(f"{VideoId}_MostReplayed.json", "w") as f:
        f.write(json_data)
    with open(f"{VideoId}_MostReplayed.json") as f:
        t = f.read()
        t = t.replace("\\", "")
        t = t.lstrip('"')
        t = t.rstrip('"')
    with open(f"{VideoId}_MostReplayed.json", "w") as f:
        f.write(t)

def GetMostReplayedInformation():
    TimeList = []
    IntensityList = []
    TimeDeltaList = []
    with open(f"{VideoId}_MostReplayed.json") as f:
        data = f.read()
        json_dict = json.loads(data)
        Datas = json_dict['items'][0]['mostReplayed']['heatMarkers']
        for Data in Datas:
            Time = Data['heatMarkerRenderer']['timeRangeStartMillis']
            Intensity = Data['heatMarkerRenderer']['heatMarkerIntensityScoreNormalized']
            if len(str(Time)) >= 4:
                Time = str(Time)[:-3]
                #Time = int(Time) / 60
                TimeList.append(int(Time))
                IntensityList.append(Intensity)
            #print(f"{Time}s // {Intensity}")


    MostReplayedDatas = json_dict['items'][0]['mostReplayed']['heatMarkersDecorations']
    for Data in MostReplayedDatas:
        StartTime = Data['timedMarkerDecorationRenderer']['visibleTimeRangeStartMillis']
        EndTime = Data['timedMarkerDecorationRenderer']['visibleTimeRangeEndMillis']
        # youtube上にハイライトされている時間
        DecorationTimeMillis = Data['timedMarkerDecorationRenderer']['visibleTimeRangeEndMillis']
        if len(str(StartTime)) >= 4:
            StartTime = str(StartTime)[:-3]
        if len(str(EndTime)) >= 4:
            EndTime = str(EndTime)[:-3]
        if len(str(DecorationTimeMillis)) >= 4:
            DecorationTimeMillis = str(DecorationTimeMillis)[:-3]
        TimeDelta_StartTime = datetime.timedelta(seconds=int(StartTime))
        TimeDelta_EndTime = datetime.timedelta(seconds=int(EndTime))
        if len(str(TimeDelta_StartTime)) == 7:
            TimeDelta_StartTime = '0' + str(TimeDelta_StartTime)
        if len(str(TimeDelta_EndTime)) == 7:
            TimeDelta_EndTime = '0' + str(TimeDelta_EndTime)

        DateTime_StartTime = datetime.datetime.strptime(str(TimeDelta_StartTime), '%H:%M:%S')
        DateTime_EndTime = datetime.datetime.strptime(str(TimeDelta_EndTime), '%H:%M:%S')

        Str_StartTime = DateTime_StartTime.strftime("%H:%M:%S")
        Str_EndTime = DateTime_EndTime.strftime("%H:%M:%S")

        Seconds_StartTime = datetime.timedelta(hours=DateTime_StartTime.hour, minutes=DateTime_StartTime.minute, seconds=DateTime_StartTime.second).total_seconds()
        Seconds_EndTime = datetime.timedelta(hours=DateTime_EndTime.hour, minutes=DateTime_EndTime.minute, seconds=DateTime_EndTime.second).total_seconds()

        # print(f"{StartTime} to {EndTime}")
    for Time in TimeList:
        Minutes = datetime.timedelta(seconds=Time)
        #print(Minutes)
        TimeDeltaList.append(str(Minutes))
    df = pd.DataFrame({'Time':TimeDeltaList, 'Intensity':IntensityList})
    df.set_index('Time', inplace=True)
    df_sorted = df.sort_values('Intensity', ascending=False)

    return TimeDelta_StartTime, TimeDelta_EndTime, Seconds_StartTime, Seconds_EndTime, TimeDeltaList, IntensityList, df, df_sorted

def ShowReplayDataframe(IntensityList, TimeDeltaList, Seconds_StartTime, Seconds_EndTime, df, df_sorted):
    col1, col2 = st.columns(2)
    with col1:
        st.text('デフォルト順')
        st.dataframe(df)
    with col2:
        st.text('視聴されている順')
        st.dataframe(df_sorted)
    return Seconds_StartTime, Seconds_EndTime, TimeDeltaList, IntensityList

def ShowMostReplayRange(TimeDelta_StartTime, TimeDelta_EndTime):
    st.text(f'リプレイ回数が最も多い部分の範囲:\n{TimeDelta_StartTime} to {TimeDelta_EndTime}')

def ShowReplayChart(df):
    st.line_chart(df)

# @st.cache_data(max_entries=1)
def PartVideoDownloader(i, Seconds_StartTime, Seconds_EndTime, Format):
    # Video = f'{executable} -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --restrict-filenames {url}'
    # subprocess.run(Video)

    # # 入力ファイルと出力ファイルのパスを指定します
    # command = f'{executable} -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" --print filename --restrict-filenames {url}'
    # InputFileName = subprocess.run(command, capture_output=True, text=True, encoding='utf-8').stdout.strip()
    # OutputFileName= f'output-{i}-{InputFileName}'
    # # 範囲を切り取ります
    # ffmpeg_command = f'ffmpeg -i "{InputFileName}" -ss {Str_StartTime} -to {Str_EndTime} -c:v copy -c:a copy "{OutputFileName}"'
    # subprocess.run(ffmpeg_command, shell=True)

    def set_download_ranges(info_dict, self):
        duration_opt = [{
            'start_time': Seconds_StartTime,
            'end_time': Seconds_EndTime
        }]
        return duration_opt
    
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        VideoFormat = 'bestvideo+bestaudio[ext=m4a]/best'
    else:
        VideoFormat = 'bestvideo+bestaudio/best'

    ydl_options={
        "format" : VideoFormat,
        'download_ranges': set_download_ranges,
        'outtmpl': f'%(title)s[%(id)s]{i}.%(ext)s'
    }
    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url)
        Filename = ydl.prepare_filename(info)
        try:
            if Format == 'mp4' or Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
                Filename = ConvertToMP4(Filename)
        except:
            ErrorMessage('Convert')
            exit()
        st.video(Filename)
    return Filename

def PartVideoDownloadBtn(Filename):
    # Filename = Filename.replace('.webm', '.mp4')
    with open (Filename, 'rb') as data:
        st.download_button(label=':red[Download]🍿', data=data, file_name=Filename, mime='video/mp4')

@st.cache_data(max_entries=1)
def VideoDownloader():
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        VideoFormat = 'bestvideo+bestaudio[ext=m4a]/best'
    else:
        VideoFormat = 'bestvideo+bestaudio/best'

    ydl_options={
        "format" : VideoFormat,
        'outtmpl': '%(title)s[%(id)s].%(ext)s'
    }

    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(UrlForDownload)
        Filename = ydl.prepare_filename(info)
        try:                
            if Format == 'mp4' or Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
                Filename = ConvertToMP4(Filename, info)
        except:
            ErrorMessage('Convert')
            exit()
        st.video(Filename)
    return Filename

def VideoDownloadBtn(Filename):
    with open (Filename, 'rb') as data:
        btn = st.download_button(label=':red[Download]🍿', data=data, file_name=Filename, mime='video/mp4')

@st.cache_data(max_entries=1)
def AudioDownloader():
    ydl_options={
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0'
        }],
        # 'outtmpl': '%(title)s[%(id)s].mp3'
        # 'cookiesfrombrowser': ('chrome', )
    }
    with YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(UrlForDownload)
        Filename = ydl.prepare_filename(info)
        Filename = Filename.replace('.webm', '.mp3').replace('.mp4', '.mp3')
        st.audio(Filename, format="audio/mp3")
    return Filename

def AudioDownloadBtn(Filename):
    with open (Filename, 'rb') as data:
        st.download_button(label=':red[Download]🎵', data=data, file_name=Filename, mime='audio/mp3')

def PartVideoDownloadProcess(PartVideoDownloader, i, Str_StartTime, Str_EndTime, LivechatVideoDownload, MostReplayedVideoDownload, Format):
    Filename = None
    if MostReplayedVideoDownload or LivechatVideoDownload:
        if MostReplayedVideoDownload:
            i = 'MostReplayed'
        with st.spinner('ロード中・・・'):
            Filename = PartVideoDownloader(i, Str_StartTime, Str_EndTime, Format)
            # st.success('ダウンロード完了しました。')
    if Filename is None:
        st.error("error")
    return Filename

def ConvertToMP4(Filename, info):
    WebmFilename = Filename
    if Format == 'mp4':
        MP4Filename = Filename.replace('.webm', '.mp4')
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        MP4Filename = Filename.replace('.mkv', '.mp4')
    if os.path.exists(MP4Filename):
        if not info['ext'] == 'mp4':
            os.remove(MP4Filename)
    if Format == 'mp4':
        if not info['ext'] == 'mp4':
            command = f'ffmpeg -i "{WebmFilename}" -c:v copy -c:a copy "{MP4Filename}"'
            subprocess.run(command, shell=True)
    if Format == 'mp4+m4a(スマートフォンの場合はこちらを選択してください)':
        command = f'ffmpeg -i "{WebmFilename}" -c:v libx264 -profile:v high -level:v 4.0 -crf 18 -c:a copy "{MP4Filename}"'
        subprocess.run(command, shell=True)
    if not info['ext'] == 'mp4':
        os.remove(WebmFilename)
    return MP4Filename

def Callback():
    st.write(st.session_state.submit_state)

def OnChangeVideo(Filename):
    if not Filename == None:
        os.remove(Filename)
    VideoDownloader.clear()

def OnChangeAudio():
    AudioDownloader.clear()

def OnChangeLivechat():
    DownloadLiveChat.clear()
    GetMostReplayedFromBrowser.clear()
    # PartVideoDownloader.clear()

def OnChangePartVideo():
    # PartVideoDownloader.clear()
    print('')

def RefreshPage():
    print('')


###

if "Livechat" not in st.session_state:
    st.session_state.Livechat = False
if "MostReplayed" not in st.session_state:
    st.session_state.MostReplayed = False
if "Submit" not in st.session_state:
    st.session_state.Submit = False
if "Download_PartLivechatVideo" not in st.session_state:
    st.session_state.Download_PartLivechatVideo = False
if "Download_PartMostReplayedVideo" not in st.session_state:
    st.session_state.Download_PartMostReplayedVideo = False
if "download_video" not in st.session_state:
    st.session_state.download_video = False
if "download_audio" not in st.session_state:
    st.session_state.download_audio = False

# st.write(st.session_state)
st.title('YouTube分析🚀', help='Livechatまたはリプレイ情報が存在するにもかかわらず  \nエラーになった場合はページを再度読み込んでください')

# with st.form('LivechatAndMostReplayed'):
url = st.text_input('**Livechatが存在する動画のURLを入れてください**', placeholder='https://www.youtube.com/watch?v=', on_change=OnChangeLivechat)
Livechat_checkbox = st.checkbox('**Livechatの情報を表示する**')
if Livechat_checkbox:
    Scale = st.radio('**目盛りの単位を決めてください**', ('時', '分', '秒'), horizontal=True, index=2, on_change=OnChangePartVideo)
    Interval = st.number_input('**グラフの目盛りの値を決めてください：**', 1, 99, 30, on_change=OnChangePartVideo)
    col1, col2 = st.columns(2)
    with col1:
        VideoStartTime = st.number_input('**特定の時間の範囲の何秒前から？**', 0, 86400, 20, on_change=OnChangePartVideo)
    with col2:
        VideoEndTime = st.number_input('**特定の時間の範囲の何秒後まで？**', 0, 86400, 0, on_change=OnChangePartVideo)
    Number = st.number_input('**上位いくつを切り抜きますか？**', 1, 99, 3)
    if Scale == '時':
        ScaleUnit = 'H'
    elif Scale == '分':
        ScaleUnit = 'T'
    elif Scale == '秒':
        ScaleUnit = 'S'
MostReplayed_checkbox = st.checkbox('**リプレイ回数が最も多い部分の情報を表示する**')
submit_btn = st.button('Submit')
# cancel_btn = st.form_submit_button('Cancel')

if submit_btn or st.session_state.Submit:
    st.session_state.Submit = True
    if not (url.startswith("https://www.youtube.com/watch?v=") or url.startswith("https://youtu.be/")):
        ErrorMessage('URL')
        exit()
    if '&' in url:
        url = url.split("&")[0]
    try:
        VideoId = url.split("youtube.com/watch?v=")[1]
    except:
        try:
            VideoId = url.split("youtu.be/")[1]
        except:
            ErrorMessage('FilledIn')
            exit()
    if Livechat_checkbox:
        st.session_state.Livechat = True
        st.text(f'{Interval}{Scale}づつ目盛りを分けます')
        with st.spinner('Livechat情報をロード中・・・'):
            with st.expander('Livechatデータ'):
                try:
                    Livechat = DownloadLiveChat(url)
                    Livechat = FindElements(Livechat)
                except:
                    ErrorMessage('Livechat')
                    exit()
                csv_df, counts = ShowCommentCount(Livechat)

                # グラフ表示
                ShowChart(counts)

                ShowTables(counts)
                i, Seconds_StartTime, Seconds_EndTime, LivechatVideoDownload, Format = GetTimeStamp(Interval, counts)
                if LivechatVideoDownload:
                    Filename = PartVideoDownloadProcess(PartVideoDownloader, i, Seconds_StartTime, Seconds_EndTime, LivechatVideoDownload, None, Format)
                    PartVideoDownloadBtn(Filename)
                    os.remove(Filename)
            st.success('完了しました。')
    if MostReplayed_checkbox and submit_btn or st.session_state.MostReplayed:
        with st.spinner('リプレイ情報をロード中・・・'):
            with st.expander('リプレイ回数データ'):
                json_data = GetMostReplayedFromBrowser()
                FormatMostReplayed(json_data)
                try:
                    TimeDelta_StartTime, TimeDelta_EndTime, Seconds_StartTime, Seconds_EndTime, TimeDeltaList, IntensityList, df, df_sorted = GetMostReplayedInformation()
                except:
                    ErrorMessage('Replay')
                    exit()
                st.session_state.MostReplayed = True
                ShowReplayChart(df)
                ShowMostReplayRange(TimeDelta_StartTime, TimeDelta_EndTime)
                GetVideos(Seconds_StartTime, Seconds_EndTime)
                Format = st.radio('**形式を選んでください**', ('webm', 'mp4', 'mp4+m4a(スマートフォンの場合はこちらを選択してください)'), horizontal=True, key='MostReplayed_key', help='スマートフォンからアクセスの場合はmp4選択してください')
                MostReplayedVideoDownload = st.button('リプレイ回数が最も多い部分の動画をダウンロード')
                if MostReplayedVideoDownload:
                    Filename = PartVideoDownloadProcess(PartVideoDownloader, 'MostReplayed', Seconds_StartTime, Seconds_EndTime, None, MostReplayedVideoDownload, Format)
                    PartVideoDownloadBtn(Filename)
                    os.remove(Filename)
                ShowReplayDataframe(IntensityList, TimeDeltaList, Seconds_StartTime, Seconds_EndTime, df, df_sorted)
            st.success('完了しました。')

st.title('動画ダウンロード🚀', help='最高品質でダウンロードできます！(webm, mp4, mp3)  \n*YouTube以外にも対応しています(詳細は右上の三本線から"Get help"をクリック)  \n*ログインが必要なサイトの動画はダウンロードできません  \n*音声または映像が再生されない場合は動画再生アプリを変更してください(推奨: VLC Media Player)  \n*スマートフォンのための処理(mp4+m4a)は大変重いため再生されない場合があります。再生されなかった場合は別の動画をお試しください。')
with st.form(key='download'):
    UrlForDownload = st.text_input('**ダウンロードしたい動画のURLを入れてください**', placeholder='https://www.youtube.com/watch?v=, https://www.twitch.tv/videos/, etc...')
    col1, col2 = st.columns(2)
    with col1:
        Format = st.radio('**形式を選んでください**', ('webm', 'mp4', 'mp4+m4a(スマートフォンの場合はこちらを選択してください)'), horizontal=True, key='downloader', help='スマートフォンからアクセスの場合はmp4選択してください')
        VideoDownload = st.form_submit_button('動画全体をダウンロード', on_click=OnChangeVideo, args=(Filename,))
    with col2:
        st.markdown('**音声ファイルはmp3です**')
        AudioDownload = st.form_submit_button('音声のみをダウンロード', on_click=OnChangeAudio)

col1, col2, col3 = st.columns(3)
with col1:
    if VideoDownload or st.session_state.download_video:
        if not UrlForDownload:
            ErrorMessage('FilledIn')
            exit()
        with st.spinner('ロード中・・・'):
            try:
                Filename = VideoDownloader()
            except:
                ErrorMessage('URL')
                exit()
            st.session_state.download_video = True
            VideoDownloadBtn(Filename)
with col2:
    if AudioDownload or st.session_state.download_audio:
        if not UrlForDownload:
            ErrorMessage('FilledIn')
            exit()
        with st.spinner('ロード中・・・'):
            try:
                Filename = AudioDownloader()
            except:
                ErrorMessage('URL')
                exit()
            st.session_state.download_audio = True
            AudioDownloadBtn(Filename)

refresh = st.button("キャッシュを消す")
if refresh:
    st.cache_data.clear()
###