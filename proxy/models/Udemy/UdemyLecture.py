class UdemyLecture:
    udemyCourse = None
    lecture_url = ""
    lecture_title = ""
    lecture_length = ""
    asset_id = ""  # asset_id different than lecture_id (using for requesting manifest)
    manifest_playlist = None
    manifests = []

    def __init__(self, lecture_id, udemyCourse):
        self.lecture_id = lecture_id
        self.udemyCourse = udemyCourse

    def updateLectureTitle(self):
        JSON = self.udemyCourse.get_course_lectures()
        lectures = JSON['results']
        for l in lectures:
            if (l['id'] == self.lecture_id):
                index = str(l['object_index'])
                title = l['title']
                asset_id = int(l['asset']['id'])
                time_estimation = int(l['asset']['time_estimation'])

                self.set_lecture_title(index + ". " + title)
                self.set_asset_id(asset_id)
                self.set_lecture_length(time_estimation)
                return

    def get_lecture_id(self):
        return self.lecture_id

    def get_udemy_course(self):
        return self.udemyCourse

    def get_lecture_url(self):
        return self.lecture_url

    def set_lecture_url(self, lecture_url):
        self.lecture_url = lecture_url

    def get_lecture_title(self):
        return self.lecture_title

    def set_lecture_title(self, lecture_title):
        self.lecture_title = lecture_title

    def get_lecture_length(self):
        return self.lecture_length

    def set_lecture_length(self, lecture_length):
        self.lecture_length = lecture_length

    def get_asset_id(self):
        return self.asset_id

    def set_asset_id(self, asset_id):
        self.asset_id = asset_id

    def get_manifest_playlist(self):
        return self.manifest_playlist

    def set_manifest_playlist(self, playlist_infos):
        self.manifest_playlist = playlist_infos

    def get_manifests(self):
        return self.manifests

    def set_manifests(self, playlists):
        self.manifests = playlists

