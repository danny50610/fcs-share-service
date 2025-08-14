from time import sleep
from celery.app import Celery
from app.models import StatisticsJob
from app.settings import settings
from sqlmodel import Session, create_engine, select

engine = create_engine(settings.postgres_url)

def get_session():
    with Session(engine) as session:
        yield session

session = next(get_session())

redis_url = settings.redis_url

app = Celery(__name__, broker=redis_url, backend=redis_url)

@app.task(bind=True)
def statistics(self):
    job_id = self.request.id
    statistics_job = session.exec(select(StatisticsJob).where(StatisticsJob.job_id == job_id)).first()

    if not statistics_job:
        return

    statistics_job.status = 'running'
    session.add(statistics_job)
    session.commit()
    session.refresh(statistics_job)

    sleep(30)

    statistics_job.status = 'completed'
    statistics_job.result = {"message": "Statistics job completed successfully"}
    session.add(statistics_job)
    session.commit()
    session.refresh(statistics_job)

