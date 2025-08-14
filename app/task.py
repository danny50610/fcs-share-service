from celery.app import Celery
from app.models import ShortLink, StatisticsJob, User
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

    result = do_statistics_job()

    statistics_job.status = 'completed'
    statistics_job.result = result
    session.add(statistics_job)
    session.commit()
    session.refresh(statistics_job)


def do_statistics_job():
    result = {
        "file_details": [],
        "user_statistics": []
    }

    user_ids = []
    user_statistics_map = {}

    files = session.exec(select(ShortLink)).all()
    for file in files:
        file_detail = {
            "original_file": file.original_file,
            "filesize": file.filesize,
            "created_at": file.created_at.isoformat() if file.created_at else None,
            "fcs_version": file.fcs_version,
            "pnn": file.pnn,
            "event_count": file.event_count
        }
        result["file_details"].append(file_detail)

        user_id = file.user_id
        if user_id:
            user_ids.append(user_id)
        else:
            user_id = 'anonymous'
            
            
        if user_id not in user_statistics_map:
            user_statistics_map[user_id] = {}
            
        user_statistics_map[user_id]["file_count"] = user_statistics_map[user_id].get("file_count", 0) + 1
        user_statistics_map[user_id]["total_filesize"] = user_statistics_map[user_id].get("total_filesize", 0) + file.filesize

    user_ids = set(user_ids)
    usersInfo = session.exec(select(User).where(User.id.in_(user_ids))).all()
    for user in usersInfo:
        user_stat = {
            "email": user.email,
            "file_count": user_statistics_map.get(user.id, {}).get("file_count", 0),
            "total_filesize": user_statistics_map.get(user.id, {}).get("total_filesize", 0)
        }
        result["user_statistics"].append(user_stat)

    if 'anonymous' in user_statistics_map:
        anonymous_stat = {
            "email": "anonymous",
            "file_count": user_statistics_map['anonymous'].get("file_count", 0),
            "total_filesize": user_statistics_map['anonymous'].get("total_filesize", 0)
        }
        result["user_statistics"].append(anonymous_stat)

    return result
