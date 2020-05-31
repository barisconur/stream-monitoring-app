#!/usr/bin/env python3
import re

import urllib.request, json
import warnings

from mitmproxy import ctx
from datetime import datetime

from models.Udemy.UdemyCourse import UdemyCourse
from models.Udemy.UdemyLecture import UdemyLecture
from service.MongoService import MongoService


class UdemyGrabber:
    udemyCourses = []
    udemyLectures = []
    #cachedChunks = [] --> buna bakıcaz bi ara
    platform = "Udemy"
    isMongoInstanceInitialized = False

    def __init__(self):
        ctx.log.warn("Udemy script has been initialised")

    # testing purposes
    def print_udemy_courses(self):
        for uc in UdemyGrabber.udemyCourses:
            print("----------COURSE_ID-------------")
            print(uc.get_course_id())
            print("-----------URL--------------")
            print(uc.get_course_url())
            print("-------------TITLE-----------")
            print(uc.get_course_title())
            print("-----------JSON-----------------")
            if (uc.get_course_lectures() == None):
                print("NONE")
            else:
                print("NOT NONE, JSON IS EXTRACTED")
    # testing purposes
    def print_udemy_lectures(self):
        for ul in UdemyGrabber.udemyLectures:
            uc = ul.get_udemy_course()
            self.print_lecture(ul)
            print("-----------JSON-----------------")
            if (uc.get_course_lectures() == None):
                print("NONE")
            else:
                print("NOT NONE, JSON IS EXTRACTED")
    # testing purposes
    def print_lecture(self, lec):
        print("-----Lecture Title----------")
        print(lec.get_lecture_title())
        print("-----Asset ID----------")
        print(lec.get_asset_id())
        print("-----Playlist----------")
        for pl in lec.get_manifests():
            print(pl['resolution']+"\n")
    # testing purposes
    def print_manifest_of_lecture(self, lec):
        manifest = lec.get_manifest_playlist()
        print(manifest)

    def requestUdemyApiWithCourseId(self, course_id): # Capturing course Title, course_url data
        with urllib.request.urlopen('https://www.udemy.com/api-2.0/courses/' + str(course_id)) as url:
            course_json = json.loads(url.read().decode())
        return course_json
    #course methods
    def handleWhichCourseIsRequested(self, flow, url):
        course_id = int(re.search('course_id=(.*)', url).group(1))
        if (self.isUdemyCourseAlreadyRequested(course_id)):
            return

        course_json = self.requestUdemyApiWithCourseId(course_id)
        course_title = course_json['title']
        course_url = re.search('course/(.*)/', course_json['url']).group(1)
        self.addUdemyCourse(course_id, course_title, course_url)
    def isUdemyCourseAlreadyRequested(self, course_id):
        for uc in UdemyGrabber.udemyCourses:
            if (uc.get_course_id == course_id):
                return True
        return False
    def addUdemyCourse(self, course_id, course_title, course_url):
        udemyCourse = UdemyCourse(course_id, course_title, course_url)
        UdemyGrabber.udemyCourses.append(udemyCourse)
    #lecture methods
    def isUdemyLectureNotRequestedBefore(self, lecture_id, course_id):
        for ul in UdemyGrabber.udemyLectures:
            if (ul.get_lecture_id() == lecture_id):
                uc = ul.get_udemy_course()
                if (uc.get_course_id() == course_id):
                    return False
        return True
    def whichUdemyLecture(self, asset_id, course_id):
        for ul in UdemyGrabber.udemyLectures:
            uc = ul.get_udemy_course()
            if (ul.get_asset_id() == asset_id):
                if (uc.get_course_id() == course_id):
                    return ul
        return None
    def addUdemyLecture(self, lecture_id, uc):
        for ul in UdemyGrabber.udemyLectures:
            if (ul.get_lecture_id() == lecture_id):  # if any client request same lecture ignore it
                course = ul.get_udemy_course()
                if (course.get_course_id() == uc.get_course_id()):
                    warnings.warn("The lecture is already created before")
                    return

        udemyLecture = UdemyLecture(lecture_id, uc)
        UdemyGrabber.udemyLectures.append(udemyLecture)
    def addUdemyLectureWithLectureId(self, lecture_id, course_id):
        for ul in UdemyGrabber.udemyLectures:
            uc = ul.get_udemy_course()
            if (ul.get_lecture_id() == lecture_id):
                if (uc.get_course_id() == course_id):
                    warnings.warn("This lecture is already created")
                    return

        for uc in UdemyGrabber.udemyCourses:
            if (uc.get_course_id() == course_id):
                json = uc.get_course_lectures()
                lectures = json['results']
                for l in lectures:
                    l_id = int(l['id'])
                    if (l_id == lecture_id):
                        index = str(l['object_index'])
                        title = l['title']
                        asset_id = int(l['asset']['id'])
                        udemyLecture = UdemyLecture(lecture_id, uc)
                        udemyLecture.set_lecture_title(index + ". " + title)
                        udemyLecture.set_asset_id(asset_id)
                        UdemyGrabber.udemyLectures.append(udemyLecture)
                        return
    def addUdemyLectureWithAssetId(self, asset_id, course_id, manifest_playlist):
        for ul in UdemyGrabber.udemyLectures:
            uc = ul.get_udemy_course()
            if (ul.get_asset_id() == asset_id):
                if (uc.get_course_id() == course_id):
                    warnings.warn("This lecture is already created")
                    return

        for uc in UdemyGrabber.udemyCourses:
            if (uc.get_course_id() == course_id):
                json = uc.get_course_lectures()
                lectures = json['results']
                for l in lectures:
                    asset = l.get('asset')
                    if (asset):
                        a_id = int(l['asset']['id'])
                        if (a_id == asset_id):
                            index = str(l['object_index'])
                            title = l['title']
                            lecture_id = int(l['id'])
                            udemyLecture = UdemyLecture(lecture_id, uc)
                            udemyLecture.set_lecture_title(index + ". " + title)
                            udemyLecture.set_asset_id(asset_id)
                            udemyLecture.set_manifest_playlist(manifest_playlist)
                            UdemyGrabber.udemyLectures.append(udemyLecture)
                            return
    def whichLectureRequestedBefore(self, asset_id, course_id):
        for ul in UdemyGrabber.udemyLectures:
            if (ul.get_asset_id() == asset_id):
                uc = ul.get_udemy_course()
                if (uc.get_course_id() == course_id):
                    return ul
        return None
    def addLecturesJson(self, flow, url):
        course_id = int(re.search('courses/(.*)/sub', url).group(1))
        for uc in UdemyGrabber.udemyCourses:
            if (uc.get_course_id() == course_id):
                if (uc.get_course_lectures() == None):
                    jsonFile = flow.response.content
                    lecturesJSON = json.loads(jsonFile)
                    uc.set_course_lectures(lecturesJSON)
                    self.modifyLectures(uc)
                    return
                return
    def modifyLectures(self, uc):
        for ul in UdemyGrabber.udemyLectures:
            course = ul.get_udemy_course()
            if (course.get_course_id() == uc.get_course_id()):
                ul.updateLectureTitle()
    def findAvailableManifests(self, content_decoded):
        available_playlists = []
        playlist_regex = "#EXT-X-STREAM-INF:(.*)"
        url_regex = "https://(.*)?"
        playlists = re.findall(playlist_regex, content_decoded)
        urls = re.findall(url_regex, content_decoded)

        for i in range(playlists.__len__()):
            bandwidth, average_bandwidth, resolution, frame_rate, codecs = ["None"] * 5
            pl = playlists[i]
            codec_str = re.search('CODECS=(.*)"', pl).group(1)
            commaCount = pl.count(",")
            codec_count = codec_str.count(",")
            pl = pl.split(",", commaCount - codec_count)
            for element in pl:
                element = element.split("=", 2)
                key = element[0]
                value = element[1]
                if ('AVERAGE-BANDWIDTH' in key):
                    average_bandwidth = value
                else:
                    if ('BANDWIDTH' in key):
                        bandwidth = value
                    elif ('RESOLUTION' in key):
                        resolution = value
                        resolution = resolution.split("x", 2)[1] + "p"
                    elif ('FRAME-RATE' in key):
                        frame_rate = value
                    elif ('CODECS' in key):
                        codecs = value

            url = urls[i]
            res_signiture = re.search('hls/(.*)/', url).group(1)
            pl_obj = {
                "res_signiture": res_signiture,
                "bandwidth": bandwidth,
                "average_bandwidth": average_bandwidth,
                "resolution": resolution,
                "frame_rate": frame_rate,
                "codecs": codecs,
                "url": url,
            }
            available_playlists.append(pl_obj)
        return available_playlists
    def findAllChunks(self, content_decoded):
        chunks = []
        duration_regex = "#EXTINF:(.*),"
        url_regex = "https://(.*)?"
        urls = re.findall(url_regex, content_decoded)
        chunk_durations = re.findall(duration_regex, content_decoded)

        for i in range(urls.__len__()):
            res_signiture = re.search('hls/(.*)/', urls[i]).group(1)
            iThPacket = i
            chunk_duration = chunk_durations[i]
            chunk_url = re.search('udemycdn.com(.*)?', urls[i]).group(1)

            chunk_obj = {
                "res_signiture": res_signiture,
                "iThPacket": iThPacket,
                "chunk_duration": chunk_duration,
                "chunk_url": chunk_url
            }
            chunks.append(chunk_obj)
        return chunks
    def findManifestWithRes(self, manifest_playlist, res):
        for manifest in manifest_playlist:
            if (manifest['res_signiture'] == res):
                return manifest
        return None
    def handleLectureRequest(self, url):
        course_url = re.search('course/(.*)/learn', url).group(1)
        lecture_id = int((re.search('lecture/(.*)?start', url).group(1))[:-1])

        for uc in UdemyGrabber.udemyCourses:
            if ((uc.get_course_url() == course_url)):
                if (self.isUdemyLectureNotRequestedBefore(lecture_id, uc.get_course_id())):
                    self.addUdemyLecture(lecture_id, uc)
                    return
    def handlePostRequestsToAnotherLecture(self, flow):
        post_req_bytes = flow.request.content
        post_req = post_req_bytes.decode()
        post_reqJSON = json.loads(post_req)
        try:
            lecture_id = post_reqJSON['objectId']
            course_id = post_reqJSON.get('courseId')

            for uc in UdemyGrabber.udemyCourses:
                if (uc.get_course_id() == course_id):
                    self.addUdemyLecture(lecture_id, uc)
        except:
            pass
    def handleManifest(self, flow, url):
        asset_id = int(re.search('assets/(.*)/files', url).group(1))
        course_id = int(re.search('files/(.*)/' + str(asset_id), url).group(1))
        resolution = re.search('hls/(.*)/', url).group(1)

        content_bytes = flow.response.content
        content_decoded = content_bytes.decode()

        chunks = self.findAllChunks(content_decoded)
        lecture = self.whichLectureRequestedBefore(asset_id, course_id)

        manifest_obj = {
            "resolution": resolution,
            "chunks": chunks
        }
        if (lecture == None):
            warnings.warn("Lecture is cached!!!")
        else:
            manifests = lecture.get_manifests()
            manifests.append(manifest_obj)
            lecture.set_manifests(manifests)
    def handleManifestPlaylist(self, flow, url):
        if ('files' in url):  # req to manifest playlist containing all manifest urls
            asset_id = int(re.search('assets/(.*)/files', url).group(1))
            course_id = int(re.search('files/(.*)/' + str(asset_id), url).group(1))

            content_bytes = flow.response.content
            content_decoded = content_bytes.decode()
            manifest_playlist = self.findAvailableManifests(content_decoded)
            reqLecture = self.whichLectureRequestedBefore(asset_id, course_id)

            if (reqLecture == None):
                self.addUdemyLectureWithAssetId(asset_id, course_id, manifest_playlist)
            else:
                reqLecture.set_manifest_playlist(manifest_playlist)

    def whichChunkRequested(self, url, host, content_length):
        ids = re.search('/(.*)/hls', url).group(1)
        ids = ids.split("/", 2)
        course_id = int(ids[0])
        asset_id = int(ids[1])
        unique_id = ids[2][:-4]

        res_signiture = re.search('hls/(.*)/', url).group(1)
        lecture = self.whichUdemyLecture(asset_id, course_id)

        # debugging for caching issues
        if (lecture == "None"):
            warnings.warn("Lecture has been cached")
            return

        for pl in lecture.get_manifests():
            if (pl['resolution'] == res_signiture):
                for chunk in pl['chunks']:
                    if (url == chunk['chunk_url']):
                        iThChunk = chunk['iThPacket']
                        if (content_length == None):  # 0 Byte Dummy Response (must be in cache)
                            print("TODO")
                            return

                        manifest = self.findManifestWithRes(lecture.get_manifest_playlist(), res_signiture)
                        uc = lecture.get_udemy_course()
                        uc_title = uc.get_course_title()
                        uc_url = uc.get_course_url()

                        bandwidthMbps = float(manifest['bandwidth']) / 1000000
                        average_bandwidth = float(manifest['average_bandwidth']) / 1000000
                        frame_rate =  manifest['frame_rate']
                        codecs = manifest['codecs']
                        duration = float(chunk['chunk_duration'])
                        fileSizeInMB = float(content_length) / float(1024 * 1024)

                        chunk_data_obj = {
                            "platform": UdemyGrabber.platform,
                            "titles": {"course_title": uc_title, "lecture_title": lecture.get_lecture_title()},
                            "id": str(asset_id),
                            "ids": {"course_id": course_id, "lecture_id": lecture.get_lecture_id()},
                            "course_url": "www.udemy.com/course/ "+ uc_url,
                            "forward_link": host + "/" + str(course_id) + "/" + str(asset_id) + "/" + unique_id,
                            "type": "MPEG-2 Muxed",
                            "duration": duration,
                            "video_length": lecture.get_lecture_length(),
                            "res_signiture": res_signiture,
                            "codecs": codecs,
                            "bandwidth": float(bandwidthMbps),
                            "average_bandwidth": float(average_bandwidth),
                            "frame_rate": frame_rate,
                            "iThChunk": iThChunk,
                            "content_length": fileSizeInMB,
                            "request_time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                        }
                        return chunk_data_obj
        return None

    def createUdemyDbObj(self, chunk):
        obj = {"platform": UdemyGrabber.platform,
               "id": str(chunk['id']),
               "course_url": chunk['course_url'],
               "forward_link": chunk['forward_link'],
               "course_title": chunk['titles']['course_title'],
               "lecture_title": chunk['titles']['lecture_title'],
               "video_length": None,
               "average_bandwidth": float(0),
               "video_chunk_count": 0,
               "video_resolutions": [],
               "download_size": float(0),
               "is_live": False,
               "first_request_time": None,
               "last_request_time": None
               }
        return obj

    def response(self, flow):
        if not UdemyGrabber.isMongoInstanceInitialized:
            MongoService.initDbAndCollections()
            UdemyGrabber.isMongoInstanceInitialized = True

        url = flow.request.path
        host = flow.request.host
        header = flow.response.headers
        content_type = header.get('Content-Type')
        packet_type = None
        content_length = header.get('Content-Length')
        if content_type:
            packet_type = content_type.translate({ord('/'): '-'})

        if 'udemy.com' in host:
            if ('course-dashboard-redirect' in url):  # course request
               self.handleWhichCourseIsRequested(flow, url)
            elif ('/api-2.0' in url and ('subscriber-curriculum-items' in url)) :  # api-2.0 reqs
                self.addLecturesJson(flow, url)
            elif ('course' in url) and ('learn/lecture') in url:  # lecture request
                self.handleLectureRequest(url)
            elif ('coursetaking' in url): # post request to watch another lecture
                self.handlePostRequestsToAnotherLecture(flow)
            elif ('assets' in url):
                if ('hls' in url): # request for a manifest file
                    self.handleManifest(flow, url)
                else: # request for manifest playlist
                    self.handleManifestPlaylist(flow, url)

        if 'hls-a.udemycdn.com' in host: #request for a video chunk
            chunk_obj = self.whichChunkRequested(url, host, content_length)
            udemyDbObj = self.createUdemyDbObj(chunk_obj)
            MongoService.addVideoToStreamsCollection(udemyDbObj)
            MongoService.addChunk(chunk_obj)
            MongoService.modifyUdemyVideo(chunk_obj)
addons = [
    UdemyGrabber()
]