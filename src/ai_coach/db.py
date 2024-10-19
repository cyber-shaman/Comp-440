from ai_coach.env import config
import dj_database_url


DABASE_URL = config("DATABASE_URL",default=None)
if DABASE_URL is not None:
  DATABASES = {
    'default': dj_database_url.config(
      default=DABASE_URL,
      conn_max_age=600,
      conn_health_checks=True
    )
}