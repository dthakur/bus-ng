import datetime

class EST(datetime.tzinfo):
  def utcoffset(self, dt):
      return datetime.timedelta(hours=-4)

  def dst(self, dt):
      return datetime.timedelta(0)

  def tzname(self, dt):
      return 'EST+04EDT'

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)
