class UdemyCourse:
    course_lectures = None

    def __init__(self, course_id, course_title, course_url):
        self.course_id = course_id
        self.course_title = course_title
        self.course_url = course_url

    def get_course_id(self):
        return self.course_id

    def get_course_title(self):
        return self.course_title

    def get_course_lectures(self):
        return self.course_lectures

    def set_course_lectures(self, course_lectures):
        self.course_lectures = course_lectures

    def get_course_url(self):
        return self.course_url