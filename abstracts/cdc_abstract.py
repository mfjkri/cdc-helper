class CDCAbstract:
    def __init__(self, username, password, headless=False):
        self.username = username
        self.password = password
        self.headless = headless

        # Practical
        self.available_days_practical = []
        self.available_days_in_view_practical = []
        self.available_times_practical = []
        self.available_sessions_practical = {}
        self.booked_sessions_practical = {}
        self.lesson_name_practical = ''
        self.can_book_next_practical_lesson = True
        self.has_auto_reserved_practical = False

        # Road revision
        self.available_days_rr = []
        self.available_days_in_view_rr = []
        self.available_times_rr = []
        self.available_sessions_rr = {}
        self.booked_sessions_rr = {}

        # BTT
        self.available_days_btt = []
        self.available_days_in_view_btt = []
        self.available_times_btt = []
        self.available_sessions_btt = {}
        self.booked_sessions_btt = {}
        self.lesson_name_btt = ''

        # RTT
        self.available_days_rtt = []
        self.available_days_in_view_rtt = []
        self.available_times_rtt = []
        self.available_sessions_rtt = {}
        self.booked_sessions_rtt = {}
        self.lesson_name_rtt = ''

        # PT
        self.available_days_pt = []
        self.available_days_in_view_pt = []
        self.available_times_pt = []
        self.available_sessions_pt = {}
        self.booked_sessions_pt = {}
        self.lesson_name_pt = ''
        self.can_book_pt = True


class Types:
    PRACTICAL = "practical"
    ROAD_REVISION = "rr"
    BTT = "btt"
    RTT = "rtt"
    PT = "pt"
