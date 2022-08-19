def Redis():
    import os,redis
    from dotenv import load_dotenv,find_dotenv
    load_dotenv(find_dotenv())

    stage = os.getenv('STAGE')

    return redis.Redis(
       host = os.getenv('REDIS_HOST') if stage!="TEST" else "localhost",
       port = os.getenv('REDIS_PORT') if stage!="TEST" else 6379
    )


def Queue(name:str):
    from rq import Queue
    return Queue(connection=Redis(),name=name)


def monitoring_queue():
    return Queue("monitoring")


def email_queue():
    return Queue("email")