from kombu import Queue

# Accepted serializers and content types
accept_content = ['json']

# Celery task configs
task_track_started = True

# Queues
task_queues = (
    Queue('default_queue', routing_key='default_queue'),
    Queue('io_queue', routing_key='io_queue'),
    Queue('transcription_queue', routing_key='transcription_queue'),
)

task_routes = {
    'default_queue': {
        'queue': 'default_queue',
        'routing_key': 'default_queue',
    },
    'io_queue': {
        'queue': 'io_queue',
        'routing_key': 'io_queue',
    },
    'transcription_queue': {
        'queue': 'transcription_queue',
        'routing_key': 'transcription_queue',
    },
}

# Worker configs
worker_max_tasks_per_child = 1

# Timeout configurations
task_soft_time_limit = 3600  # 1 hour soft limit
task_time_limit = 7200  # 2 hour hard limit
worker_disable_rate_limits = True

# Task execution settings
task_acks_late = True
task_reject_on_worker_lost = True



