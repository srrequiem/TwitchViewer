from tinydb import TinyDB, Query
import ptypes


class DayRecord:
    def __init__(self, name, startAt=0, endAt=0):
        if name not in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
            raise Exception(f"Invalid weekday {name}")
        self.name = name
        self.startAt = startAt
        self.endAt = endAt


class DB:
    def __init__(self):
        self._db = TinyDB('./db.json')
        self._scheduleTable = self._db.table('schedule')
        if len(self._scheduleTable.all()) == 0:
            self._initializeScheduleTable()

    def _initializeScheduleTable(self):
        self._scheduleTable.insert_multiple([vars(DayRecord("Sunday")), vars(DayRecord("Monday")), vars(DayRecord("Tuesday")), vars(
            DayRecord("Wednesday")), vars(DayRecord("Thursday")), vars(DayRecord("Friday")), vars(DayRecord("Saturday"))])

    def getDaySchedule(self, day: str) -> dict:
        dayRecord = Query()
        return self._scheduleTable.search(dayRecord.name == day)[0]

    def getSchedule(self) -> list:
        return self._scheduleTable.all()

    def updateDaySchedule(self, daySchedule: ptypes.DaySchedule) -> bool:
        DayRecord = Query()
        self._scheduleTable.update(vars(daySchedule),
                                   DayRecord.name == daySchedule.name)
