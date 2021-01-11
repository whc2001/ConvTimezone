from datetime import date, time, datetime, timedelta
from pytz import timezone
import re
import json

WEEKDAY_SHORTS = [ "M", "T", "W", "R", "F" ]

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
]

class WeekdayAndTime():
    _firstDayOfThisWeek = None

    WeekDay = 0
    Time = time()

    def _GetWeekdayDate(weekday):
        return WeekdayAndTime._firstDayOfThisWeek + timedelta(days=weekday)
    
    def __init__(self, weekday, time):
        self.WeekDay = weekday
        self.Time = time
        if not WeekdayAndTime._firstDayOfThisWeek:
            firstDayOfThisWeek = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            firstDayOfThisWeek = firstDayOfThisWeek - timedelta(days=firstDayOfThisWeek.weekday())
            WeekdayAndTime._firstDayOfThisWeek = firstDayOfThisWeek

    def __str__(self):
        return f"{WEEKDAYS[self.WeekDay]} {self.Time} @ {self.Time.tzinfo}"
    
    def ShiftTimezone(self, newTimezone):
        fromDateTime = datetime.combine(WeekdayAndTime._GetWeekdayDate(self.WeekDay), self.Time.replace(tzinfo=None))
        fromDateTime = self.Time.tzinfo.localize(fromDateTime)
        toDateTime = fromDateTime.astimezone(newTimezone)
        return WeekdayAndTime(toDateTime.weekday(), toDateTime.time().replace(tzinfo=newTimezone))

class CourseSchedule():
    Name = ""
    Sessions = []

    def __init__(self, name, sessions):
        self.Name = name
        self.Sessions = sessions

    def __str__(self):
        ret = ""
        ret += f"[{self.Name}]\r\n"
        for i in self.Sessions:
            ret += f"    {i[0]} ~ {i[1]}\r\n"
        return ret

    def ShiftTimezone(self, newTimezone):
        return CourseSchedule(self.Name, [(i[0].ShiftTimezone(newTimezone), i[1].ShiftTimezone(newTimezone)) for i in self.Sessions])

jsonData = None
with open("courses.json", "r") as fs:
    jsonData = json.load(fs)
    
tzSrc = timezone(jsonData["from_timezone"])
tzDst = timezone(jsonData["to_timezone"])

courses = []

for courseData in jsonData["timetable"]:
    sessions = []
    for session in courseData["sessions"]:
        for weekdayShort in session["weekday"]:
            weekday = WEEKDAY_SHORTS.index(weekdayShort)
            meetingTimeBegin = WeekdayAndTime(weekday, datetime.strptime(session["begin"], "%H:%M").time().replace(tzinfo=tzSrc))
            meetingTimeEnd = WeekdayAndTime(weekday, datetime.strptime(session["end"], "%H:%M").time().replace(tzinfo=tzSrc))
            sessions.append((meetingTimeBegin, meetingTimeEnd))
    course = CourseSchedule(courseData["name"], sessions)
    courses.append(course)
    print(course)

print(f"=================Converting to {tzDst}=================")
timezoneConvertedCourses = [i.ShiftTimezone(tzDst) for i in courses]
for course in timezoneConvertedCourses:
    print(course)
