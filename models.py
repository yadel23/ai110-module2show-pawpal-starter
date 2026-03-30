# models.py
from dataclasses import dataclass, field
from datetime import date, time, datetime
from enum import Enum
from typing import List, Optional

class TaskType(Enum):
    WALK = "walk"
    FEED = "feed"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"

class ScheduleStatus(Enum):
    PLANNED = "planned"
    SKIPPED = "skipped"
    CONFLICT = "conflict"
    COMPLETED = "completed"

@dataclass
class TimeWindow:
    start: time
    end: time

    def duration_minutes(self) -> int:
        """Calculate duration of this window in minutes."""
        start_dt = datetime.combine(date.today(), self.start)
        end_dt = datetime.combine(date.today(), self.end)
        return int((end_dt - start_dt).total_seconds() / 60)

    def contains(self, candidate: "TimeWindow") -> bool:
        """Check if this window fully contains another window."""
        return self.start <= candidate.start and candidate.end <= self.end

    def overlaps(self, candidate: "TimeWindow") -> bool:
        """Check if two windows share overlapping time."""
        return max(self.start, candidate.start) < min(self.end, candidate.end)

    def is_working(self, time_point: time) -> bool:
        """Check if a specific time point is within this window."""
        return self.start <= time_point <= self.end

@dataclass
class OwnerPreferences:
    preferred_times: List[TimeWindow]
    quiet_hrs: List[TimeWindow]
    max_activity_minutes: int = 180
    intensity_preference: str = "balanced"

    def is_quiet_hour(self, time_point: time) -> bool:
        """Check if time point falls in quiet hours."""
        return any(window.is_working(time_point) for window in self.quiet_hrs)

    def is_preferred_time(self, time_point: time) -> bool:
        """Check if time point falls in preferred time windows."""
        return any(window.is_working(time_point) for window in self.preferred_times)

@dataclass
class Owner:
    owner_id: str = ""
    name: str = ""
    email: str = ""
    timezone: str = "UTC"
    availability: List[TimeWindow] = field(default_factory=list)
    preferences: OwnerPreferences = field(default_factory=OwnerPreferences)

    def get_available_hours_today(self) -> int:
        """Calculate total available hours for the day."""
        return sum(window.duration_minutes() for window in self.availability) // 60

    def is_available_at(self, time_point: time) -> bool:
        """Check if owner is available at given time."""
        return any(window.is_working(time_point) for window in self.availability)

@dataclass
class Pet:
    pet_id: str = ""
    name: str = ""
    species: str = ""
    breed: str = ""
    age: int = 0
    required_daily_tasks: dict = field(default_factory=dict)
    rest_blocks: List[TimeWindow] = field(default_factory=list)
    preferred_activity_times: List[TimeWindow] = field(default_factory=list)

    def get_base_tasks(self) -> List["PetTask"]:
        """Generate default tasks based on species and age."""
        # This would be implemented based on species defaults
        return []

    def is_rest_time(self, time_point: time) -> bool:
        """Check if time point falls in pet rest blocks."""
        return any(window.is_working(time_point) for window in self.rest_blocks)

@dataclass
class PetTask:
    task_id: str = ""
    title: str = ""
    task_type: TaskType = TaskType.WALK
    duration_min: int = 0
    priority: int = 1
    mandatory: bool = False
    preferred_window: Optional[TimeWindow] = None
    frequency: str = "daily"
    last_done_date: Optional[date] = None
    completed_today: bool = False

    def is_overdue(self, today: date) -> bool:
        """Check if task is overdue based on frequency."""
        if not self.last_done_date:
            return True
        if self.frequency == "daily":
            return (today - self.last_done_date).days >= 1
        return False

    def fits_in_window(self, window: TimeWindow) -> bool:
        """Check if task duration fits in given time window."""
        return self.duration_min <= window.duration_minutes()

    def respects_preferred_window(self, time_point: time) -> bool:
        """Check if time point is in preferred window (if set)."""
        if not self.preferred_window:
            return True
        return self.preferred_window.is_working(time_point)

@dataclass
class ScheduledItem:
    scheduled_id: str = ""
    task: PetTask = field(default_factory=PetTask)
    start: time = time(0, 0)
    end: time = time(0, 0)
    reason: str = ""
    status: ScheduleStatus = ScheduleStatus.PLANNED

    def duration_minutes(self) -> int:
        """Calculate duration of this scheduled item."""
        start_dt = datetime.combine(date.today(), self.start)
        end_dt = datetime.combine(date.today(), self.end)
        return int((end_dt - start_dt).total_seconds() / 60)

    def overlaps_with(self, other_item: "ScheduledItem") -> bool:
        """Check if this item overlaps with another scheduled item."""
        this_window = TimeWindow(self.start, self.end)
        other_window = TimeWindow(other_item.start, other_item.end)
        return this_window.overlaps(other_window)

@dataclass
class DailySchedule:
    schedule_id: str = ""
    date: date = field(default_factory=date.today)
    owner: Owner = field(default_factory=Owner)
    pet: Pet = field(default_factory=Pet)
    items: List[ScheduledItem] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def total_minutes_scheduled(self) -> int:
        """Calculate total minutes of activity scheduled."""
        return sum(item.duration_minutes() for item in self.items)

    def get_mandatory_tasks(self) -> List[ScheduledItem]:
        """Return only mandatory scheduled items."""
        return [item for item in self.items if item.task.mandatory]

    def get_optional_tasks(self) -> List[ScheduledItem]:
        """Return only optional scheduled items."""
        return [item for item in self.items if not item.task.mandatory]

    def get_unscheduled_tasks(self, all_tasks: List[PetTask]) -> List[PetTask]:
        """Return tasks that couldn't be scheduled."""
        scheduled_task_ids = {item.task.task_id for item in self.items}
        return [task for task in all_tasks if task.task_id not in scheduled_task_ids]

@dataclass
class SchedulingRules:
    max_total_minutes: int = 180
    min_gap_between_tasks: int = 5
    must_insert_mandatory: bool = True
    priority_weight: float = 0.5
    urgency_weight: float = 0.3
    preference_weight: float = 0.2

    def calculate_score(self, task: PetTask, owner: Owner, pet: Pet, days_overdue: int) -> float:
        """Calculate priority score for a task based on rules."""
        base_score = task.priority * self.priority_weight
        urgency_score = days_overdue * self.urgency_weight
        preference_score = 0.0
        # Simple preference scoring - could be more complex
        if task.preferred_window and owner.preferences.is_preferred_time(task.preferred_window.start):
            preference_score = self.preference_weight
        return base_score + urgency_score + preference_score