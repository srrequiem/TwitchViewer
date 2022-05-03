class DaySchedule:
    def __init__(self, name, interval):
        self.name = name
        self.startAt = 0
        self.endAt = 0
        self._splitInterval(interval)

    def _splitInterval(self, interval):
        time = interval.split("-")
        startAt = time[0].split(":")
        startAtTime = int(startAt[0]) * 60 + int(startAt[1])
        endAt = time[1].split(":")
        endAtTime = int(endAt[0]) * 60 + int(endAt[1])
        if startAtTime > endAtTime:
            raise Exception(
                f"Start time greater than end time at {self.name}.")
        self.startAt = startAtTime
        self.endAt = endAtTime
