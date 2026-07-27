from enum import StrEnum


class TaskStatus(StrEnum):
    AWAITING_NEXT_RUN = 'Awaiting next run'
    RUNNING = 'Running'
    FAILED = 'Failed'
    COMPLETED = 'Completed'


class LastRunStatus(StrEnum):
    RUNNING = 'running'
    SUCCESS = 'success'
    ERROR = 'error'
