from __future__ import annotations
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class ScheduleManager:
    def __init__(self):
        self._scheduler = BackgroundScheduler()
        self._jobs: dict[str, dict] = {}

    def start(self):
        if not self._scheduler.running:
            self._scheduler.start()

    def shutdown(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def add_schedule(self, job_id: str, config: dict, callback: Callable) -> None:
        stype = config.get("type", "daily")
        time_str = config.get("time", "09:00")
        hour, minute = time_str.split(":")

        if stype == "daily":
            trigger = CronTrigger(hour=int(hour), minute=int(minute))
        elif stype == "weekly":
            day = config.get("day_of_week", "mon")
            trigger = CronTrigger(day_of_week=day, hour=int(hour), minute=int(minute))
        elif stype == "monthly":
            day = config.get("day", 1)
            trigger = CronTrigger(day=day, hour=int(hour), minute=int(minute))
        else:
            trigger = CronTrigger(hour=int(hour), minute=int(minute))

        self._scheduler.add_job(callback, trigger, id=job_id, replace_existing=True)
        self._jobs[job_id] = config

    def remove_schedule(self, job_id: str) -> None:
        try:
            self._scheduler.remove_job(job_id)
        except Exception:
            pass
        self._jobs.pop(job_id, None)

    def list_schedules(self) -> dict[str, dict]:
        return dict(self._jobs)

    def set_enabled(self, job_id: str, enabled: bool) -> None:
        if enabled:
            self._scheduler.resume_job(job_id)
        else:
            self._scheduler.pause_job(job_id)
