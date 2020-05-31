#!/usr/bin/env python3

import json
import re
import sys
import warnings

from bs4 import BeautifulSoup
from mitmproxy import ctx
from datetime import datetime

from models.YoutubeVideo import YoutubeVideo
from service.MongoService import MongoService


class YoutubeGrabber:
    youtubeVideos = []
    platform = "YouTube"
    isMongoInstanceInitialized = False

    def __init__(self):
        ctx.log.warn("Youtube script has been initialised")

    #testing purposes
    def printAllYoutubeVideos(self):
        for video in YoutubeGrabber.youtubeVideos:
            print("-----------")
            print("Video Title")
            print(video.get_title())
            print("Video Id")
            print(video.get_id())
            print("-----------")

    def parseVideoIdFromUrl(self, url):
        id = url.split('?')[1]
        if ('&' in id): id = id.split('&')[0]
        return id

    def extractJsonFileFromHtml(self, htmlFile):
        soup = BeautifulSoup(htmlFile, "html.parser")
        element = soup.find("div", {"id": "player-wrap"})
        string = str(element)
        jsonFile = re.search('ytplayer.config = (.+?);ytplayer.web_player_context_config', string).group(1)

        return json.loads(jsonFile)

    def isVideoRequestedBefore(self, video_id):
        for video in YoutubeGrabber.youtubeVideos:
            if (video.get_id() == video_id):
                return True
        return False

    def addYoutubeVideo(self, id, JSON):
        video_formats = []
        audio_formats = []

        player_response = JSON['args']['player_response']
        decoded_player_response = json.loads(player_response)

        #testing purposes
        with open ('youtube-player.json', 'w') as out:
            json.dump(decoded_player_response, out)

        video_details = decoded_player_response['videoDetails']
        video_renderer = decoded_player_response['microformat']['playerMicroformatRenderer']
        streaming_data = decoded_player_response.get('streamingData')
        adaptiveFormats = streaming_data['adaptiveFormats']
        formats = streaming_data['formats']
        url = adaptiveFormats[0].get('url')
        if url:
            googleLink = adaptiveFormats[0].get('url')
            link = re.search('https://(.*)/', googleLink).group(1)
        else:
            cipher = adaptiveFormats[0].get('cipher')
            if cipher:
                link = self.setLink(cipher, adaptiveFormats)
            else:
                cipher = formats[0].get('signatureCipher')
                link = self.setLinkV2(cipher)


        keywords = video_details.get('keywords')
        if not keywords:
            keywords = None

        for item in adaptiveFormats:
            mime_type = item['mimeType']
            if ('video' in mime_type):
                video_formats.append(item)
            elif ('audio' in mime_type):
                audio_formats.append(item)

        isLive = video_details.get('isLive')
        if isLive:
            islive = video_details['isLive']
        else:
            isLive = False

        youtube_obj = YoutubeVideo(id, video_details['title'], video_details['lengthSeconds'],
                                   keywords, video_renderer['isFamilySafe'], video_renderer['category'],
                                   JSON['args']['cbr'], link,
                                    video_formats, audio_formats, isLive)
        YoutubeGrabber.youtubeVideos.append(youtube_obj)

    def setLinkV2(self, cipher):
        link = re.search('&url(.*)', cipher).group(1)
        return link
    def setLink(self, cipher, formats):
        if cipher:
            link = re.search('%2F%2F(.*)%2Fvideoplayback', cipher).group(1)
        else:
            url = formats[0]['url']
            link = re.search('https://(.*)/videoplayback', url).group(1)
        return link

    def findYoutubeVideoByLink(self, link):
        for video in YoutubeGrabber.youtubeVideos:
            if (link == video.get_google_video_link()):
                return video
        return None

    def createVideoChunk(self, url, video, content_length):
        parsedUrl = re.search('&itag=(.*)&', url).group(1)
        itag = int(parsedUrl[:3])
        video_formats = video.get_video_formats()
        video_chunk_format = self.findFormatWithItag(itag, video_formats)

        if (video_chunk_format == None):
            warnings.warn("Video chunk could not be found in adaptive video formats")
            return

        bitrateMbps = float(video_chunk_format['bitrate']) / 1000000
        fileSizeMb = float(content_length) / (1024 * 1024)
        type = re.search('(.*);', video_chunk_format['mimeType']).group(1)
        codecs = re.search('; codecs=(.*)', video_chunk_format['mimeType']).group(1)
        r_buf = re.search('&rbuf=(.*)', url).group(1)
        if not video.get_is_live():
            parsedRange = re.search('&range=(.*)&', url).group(1)
            av_bitrateMbps = float(video_chunk_format['averageBitrate']) / 1000000
            range = parsedRange.split("&", 1)[0]
            video_chunk = {"platform": YoutubeGrabber.platform,
                           "title": video.get_title(),
                           "id": video.get_id(),
                           "forward_link": video.get_google_video_link(),
                           "type": type,
                           "resolution": video_chunk_format['qualityLabel'],
                           "codecs": codecs,
                           "bitrate": bitrateMbps,
                           "average_bitrate": av_bitrateMbps,
                           "buffer": r_buf,
                           "range": range,
                           "content_length": fileSizeMb,
                           "totalVideoLength": video.get_length(),
                           "isLive": False,
                           "request_time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                           }
        else:
            video_chunk = {"platform": YoutubeGrabber.platform,
                           "title": video.get_title(),
                           "id": video.get_id(),
                           "forward_link": video.get_google_video_link(),
                           "type": type,
                           "resolution": video_chunk_format['qualityLabel'],
                           "codecs": codecs,
                           "bitrate": bitrateMbps,
                           "buffer": r_buf,
                           "fps": video_chunk_format['fps'],
                           "targetDurationSec": video_chunk_format['targetDurationSec'],
                           "maxDvrDurationSec": video_chunk_format['maxDvrDurationSec'],
                           "content_length": fileSizeMb,
                           "totalVideoLength": video.get_length(),
                           "isLive": True,
                           "request_time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                           }
        return video_chunk

    def createAudioChunk(self, url, video, content_length):
        parsedUrl = re.search('&itag=(.*)&', url).group(1)
        itag = int(parsedUrl[:3])
        video_formats = video.get_audio_formats()
        audio_chunk_format = self.findFormatWithItag(itag, video_formats)

        if (audio_chunk_format == None):
            warnings.warn("Video chunk could not be found in adaptive video formats")
            return

        r_buf = re.search('&rbuf=(.*)', url).group(1)
        bitrateMbps = float(audio_chunk_format['bitrate']) / 1000000
        fileSizeMb = float(content_length) / (1024 * 1024)
        type = re.search('(.*);', audio_chunk_format['mimeType']).group(1)
        codecs = re.search('; codecs=(.*)', audio_chunk_format['mimeType']).group(1)
        range = "None"

        if not video.get_is_live():
            parsedRange = re.search('&range=(.*)&', url).group(1)
            range = parsedRange.split("&", 1)[0]

        audio_chunk = {"platform": YoutubeGrabber.platform,
                       "title": video.get_title(),
                       "id": video.get_id(),
                       "forward_link": video.get_google_video_link(),
                       "type": type,
                       "resolution": re.search('QUALITY_(.*)',audio_chunk_format['audioQuality']).group(1),
                       "codecs": codecs,
                       "bitrate": bitrateMbps,
                       "buffer": r_buf,
                       "range": range,
                       "content_length": fileSizeMb,
                       "totalVideoLength": video.get_length(),
                       "isLive": video.get_is_live(),
                       "request_time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                       }

        return audio_chunk

    def createyoutubeDbObj(self, youtubeObj):
        obj = {"platform": YoutubeGrabber.platform,
               "id": youtubeObj.get_id(),
               "video_url": "www.youtube.com/watch?" + youtubeObj.get_id(),
               "forward_link": youtubeObj.get_google_video_link(),
               "video_title": youtubeObj.get_title(),
               "video_length": youtubeObj.get_length(),
               "average_video_bitrate": float(0),
               "video_chunk_count": 0,
               "audio_chunk_count": 0,
               "video_resolutions": [],
               "audio_resolutions": [],
               "download_size": float(0),
               "is_live": youtubeObj.get_is_live(),
               "first_request_time": None,
               "last_request_time": None
               }
        return obj

    def findFormatWithItag(self, itag, formats):
        for format in formats:
            if (format['itag'] == itag):
                return format
        return None

    def response(self, flow):
        if not YoutubeGrabber.isMongoInstanceInitialized:
            MongoService.initDbAndCollections()
            YoutubeGrabber.isMongoInstanceInitialized = True

        url = flow.request.path
        host = flow.request.host
        header = flow.response.headers
        content_type = header.get('Content-Type')
        packet_type = None
        content_length = header.get('Content-Length')

        if content_type:
            packet_type = content_type.translate({ord('/'): '-'})

        if ((flow.response.status_code) == 204 or (content_length == "0")):
            return

        if (("youtube.com" in host) and ("watch?" in url)):
            video_id = self.parseVideoIdFromUrl(url)
            if (self.isVideoRequestedBefore(video_id)):
                warnings.warn = "The video is requested before"
                return

            videoJson = None
            if ('text-html' in packet_type): # video request from YouTube homepage
                videoJson = self.extractJsonFileFromHtml(flow.response.content)
            elif ('application-json' in packet_type): # video request from YouTube Up next
                videoJson = (json.loads(flow.response.content))[2]['player']

            self.addYoutubeVideo(video_id, videoJson)

        elif ("googlevideo.com" in host):
            if (content_length == None):
                content_length = sys.getsizeof(flow.response.content)

            youtubeObj = self.findYoutubeVideoByLink(host)
            if (youtubeObj == None):
                warnings.warn = "The video could not be found with googlevideo link"
                return
            youtubeDbObj = self.createyoutubeDbObj(youtubeObj)
            MongoService.addVideoToStreamsCollection(youtubeDbObj)

            if ('video' in packet_type): # video chunk request
                video_chunk = self.createVideoChunk(url, youtubeObj, content_length)
                with open('chunks.txt', 'a+') as file:
                    file.write(json.dumps(video_chunk) + "\n")
                with open('bufferValues.txt', 'a+') as file:
                    file.write("v:" + video_chunk['buffer'] + "\n")
                MongoService.addChunk(video_chunk)
                print(video_chunk)
                MongoService.modifyYoutubeVideo(video_chunk)

            elif ('audio' in packet_type): # audio chunk request
                audio_chunk = self.createAudioChunk(url, youtubeObj, content_length)

                with open('chunks.txt', 'a+') as file:
                    file.write(json.dumps(audio_chunk) + "\n")
                with open('bufferValues.txt', 'a+') as file:
                    file.write("a:" + audio_chunk['buffer'] + "\n")
                MongoService.addChunk(audio_chunk)
                MongoService.modifyYoutubeVideo(audio_chunk)



    # thread = threading.Thread(target=self.downloadVideoFromYoutube, args=())
    # thread.daemon = True
    # thread.start()

    def downloadVideoFromYoutube(self):
        a = 1
        # video = YouTube(YoutubeGrabber.video_URL)
        # video.streams.filter(progressive=True, file_extension='mp4'). \
        #    order_by('resolution').desc().first().download(YoutubeGrabber.path)

addons = [
    YoutubeGrabber()
]
