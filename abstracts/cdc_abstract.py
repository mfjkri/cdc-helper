import re

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

    def __str__(self):
        #members = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        return re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', 
            f"""
            # ------------------------------------- - ------------------------------------ #
            CDC_ABSTRACT:
            
            user = {str(self.username)},
            password = {str(self.password)},
            headless = {str(self.headless)},

            # Practical
            available_days_practical = {str(self.available_days_practical)}
            available_days_in_view_practical = {str(self.available_days_in_view_practical)}
            available_times_practical = {str(self.available_times_practical)}
            available_sessions_practical = {str(self.available_sessions_practical)}
            booked_sessions_practical = {str(self.booked_sessions_practical)}
            lesson_name_practical = {str(self.lesson_name_practical)}
            can_book_next_practical_lesson = {str(self.can_book_next_practical_lesson)}
            has_auto_reserved_practical = {str(self.has_auto_reserved_practical)}

            # Road revision
            available_days_rr = {str(self.available_days_rr)}
            available_days_in_view_rr = {str(self.available_days_in_view_rr)}
            available_times_rr = {str(self.available_times_rr)}
            available_sessions_rr = {str(self.available_sessions_rr)}
            booked_sessions_rr = {str(self.booked_sessions_rr)}

            # BTT
            available_days_btt = {str(self.available_days_btt)}
            available_days_in_view_btt = {str(self.available_days_in_view_btt)}
            available_times_btt = {str(self.available_times_btt)}
            available_sessions_btt = {self.available_sessions_btt}
            booked_sessions_btt = {str(self.booked_sessions_btt)}
            lesson_name_btt = {str(self.lesson_name_btt)}

            # RTT
            available_days_rtt = {str(self.available_days_rtt)}
            available_days_in_view_rtt = {str(self.available_days_in_view_rtt)}
            available_times_rtt = {str(self.available_times_rtt)}
            available_sessions_rtt = {str(self.available_sessions_rtt)}
            booked_sessions_rtt = {str(self.booked_sessions_rtt)}
            lesson_name_rtt = {str(self.lesson_name_rtt)}

            # PT
            available_days_pt = {str(self.available_days_pt)}
            available_days_in_view_pt = {str(self.available_days_in_view_pt)}
            available_times_pt = {str(self.available_times_pt)}
            available_sessions_pt = {str(self.available_sessions_pt)}
            booked_sessions_pt = {str(self.booked_sessions_pt)}
            lesson_name_pt = {str(self.lesson_name_pt)}
            can_book_pt = {str(self.can_book_pt)}
            # ------------------------------------- - ------------------------------------ #
            """, flags=re.M
        )

class Types:
    PRACTICAL = "practical"
    ROAD_REVISION = "rr"
    BTT = "btt"
    RTT = "rtt"
    PT = "pt"
