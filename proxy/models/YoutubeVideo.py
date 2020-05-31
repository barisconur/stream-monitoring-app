class YoutubeVideo:

    def __str__(self):
        return "Id :" + self.id + "\n" + \
               "Title: " + self.title + "\n" + \
               "isLive: " + str(self.isLive) + "\n" + \
               "f-link: " + self.google_video_link

    def __init__(self, id, title, length, keywords, isFamilySafe,
                 category, client_browser,google_video_link,
                 video_formats, audio_formats, isLive):
        self.id = id
        self.title = title
        self.isLive = isLive
        self.keywords = keywords
        self.isFamilySafe = isFamilySafe
        self.category = category
        self.client_browser = client_browser
        self.google_video_link = google_video_link
        self.video_formats = video_formats
        self.audio_formats = audio_formats
        if (isLive):
            self.length = -1 # no total length for live streaming
        else:
            self.length = length
    def get_id(self):
        return self.id

    def set_url(self, url):
        self.url = url

    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_length(self):
        return self.length

    def set_length(self, length):
        self.length = length

    def get_keywords(self):
        return self.keywords

    def set_keywords(self, keywords):
        self.keywords = keywords

    def get_category(self):
        return self.category

    def set_category(self, category):
        self.category = category

    def get_isFamilySafe(self):
        return self.isFamilySafe

    def set_isFamilySafe(self, isFamilySafe):
        self.isFamilySafe = isFamilySafe

    def get_client_browser(self):
        return self.client_browser

    def set_client_browser(self, client_browser):
        self.client_browser = client_browser

    def get_client_youtube_name(self):
        return self.client_youtube_name

    def set_client_youtube_name(self, client_youtube_name):
        self.client_youtube_name = client_youtube_name

    def get_google_video_link(self):
        return self.google_video_link

    def set_google_video_link(self,google_video_link):
        self.google_video_link = google_video_link

    def get_video_formats(self):
        return self.video_formats

    def set_video_formats(self, video_formats):
        self.video_formats = video_formats

    def get_audio_formats(self):
        return self.audio_formats

    def set_audio_formats(self, audio_formats):
        self.audio_formats = audio_formats

    def get_is_live(self):
        return self.isLive