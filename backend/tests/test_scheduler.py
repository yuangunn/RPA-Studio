import pytest
from rpa_studio.scheduler.cron import ScheduleManager


class TestScheduler:
    def test_add_schedule(self):
        mgr = ScheduleManager()
        mgr.start()
        mgr.add_schedule("test_job", {"type": "daily", "time": "09:00"}, callback=lambda: None)
        assert "test_job" in mgr.list_schedules()
        mgr.shutdown()

    def test_remove_schedule(self):
        mgr = ScheduleManager()
        mgr.start()
        mgr.add_schedule("test_job", {"type": "daily", "time": "09:00"}, callback=lambda: None)
        mgr.remove_schedule("test_job")
        assert "test_job" not in mgr.list_schedules()
        mgr.shutdown()

    def test_monthly_schedule(self):
        mgr = ScheduleManager()
        mgr.start()
        mgr.add_schedule("monthly", {"type": "monthly", "day": 1, "time": "09:00"}, callback=lambda: None)
        assert "monthly" in mgr.list_schedules()
        mgr.shutdown()
