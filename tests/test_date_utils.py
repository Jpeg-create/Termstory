import os
from datetime import datetime
from termstory.date_utils import get_current_time, get_today_range, get_week_range, get_month_range, format_date_range

def test_get_current_time(monkeypatch):
    # Without override
    monkeypatch.delenv("TERMSTORY_DATE_OVERRIDE", raising=False)
    now = datetime.now()
    ct = get_current_time()
    assert abs((ct - now).total_seconds()) < 2
    
    # With override
    monkeypatch.setenv("TERMSTORY_DATE_OVERRIDE", "2026-06-02")
    ct = get_current_time()
    assert ct.year == 2026
    assert ct.month == 6
    assert ct.day == 2

def test_get_today_range(monkeypatch):
    monkeypatch.setenv("TERMSTORY_DATE_OVERRIDE", "2026-06-02 12:34:56")
    start, end = get_today_range()
    
    start_dt = datetime.fromtimestamp(start)
    end_dt = datetime.fromtimestamp(end)
    
    assert start_dt.year == 2026 and start_dt.month == 6 and start_dt.day == 2
    assert start_dt.hour == 0 and start_dt.minute == 0 and start_dt.second == 0
    assert end_dt.hour == 23 and end_dt.minute == 59 and end_dt.second == 59

def test_get_week_range(monkeypatch):
    # June 2, 2026 is a Tuesday
    monkeypatch.setenv("TERMSTORY_DATE_OVERRIDE", "2026-06-02 12:00:00")
    start, end = get_week_range()
    
    start_dt = datetime.fromtimestamp(start)
    end_dt = datetime.fromtimestamp(end)
    
    # Monday of that week should be June 1st
    assert start_dt.year == 2026 and start_dt.month == 6 and start_dt.day == 1
    # Sunday should be June 7th
    assert end_dt.year == 2026 and end_dt.month == 6 and end_dt.day == 7
    
    # Last week range: Monday should be May 25, Sunday should be May 31
    l_start, l_end = get_week_range(last=True)
    l_start_dt = datetime.fromtimestamp(l_start)
    l_end_dt = datetime.fromtimestamp(l_end)
    assert l_start_dt.month == 5 and l_start_dt.day == 25
    assert l_end_dt.month == 5 and l_end_dt.day == 31

def test_get_month_range():
    start, end = get_month_range(2026, 6)
    start_dt = datetime.fromtimestamp(start)
    end_dt = datetime.fromtimestamp(end)
    
    assert start_dt.year == 2026 and start_dt.month == 6 and start_dt.day == 1
    assert end_dt.year == 2026 and end_dt.month == 6 and end_dt.day == 30

def test_format_date_range():
    # Same month
    s = datetime(2026, 6, 1, 0, 0).timestamp()
    e = datetime(2026, 6, 7, 23, 59).timestamp()
    assert format_date_range(int(s), int(e)) == "June 01 - 07, 2026"
    
    # Different months, same year
    s2 = datetime(2026, 5, 25, 0, 0).timestamp()
    e2 = datetime(2026, 6, 1, 23, 59).timestamp()
    assert format_date_range(int(s2), int(e2)) == "May 25 - June 01, 2026"
    
    # Different years
    s3 = datetime(2025, 12, 29, 0, 0).timestamp()
    e3 = datetime(2026, 1, 4, 23, 59).timestamp()
    assert format_date_range(int(s3), int(e3)) == "December 29, 2025 - January 04, 2026"
