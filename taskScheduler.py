from datetime import date, time, datetime, timedelta
from typing import List, Optional
from models import (
    Owner, Pet, PetTask, DailySchedule, ScheduledItem, SchedulingRules,
    TimeWindow, ScheduleStatus
)

class TaskScheduler:
    def __init__(self, rules: SchedulingRules):
        self.rules = rules

    def generate(self, owner: Owner, pet: Pet, tasks: List[PetTask], day: date) -> DailySchedule:
        """Main method to generate a daily schedule."""
        available = self._build_available_slots(owner, pet, day)
        remaining = self._score_and_sort(tasks, owner, pet)
        schedule = DailySchedule(date=day, owner=owner, pet=pet)
        scheduled_items = []
        for task in remaining:
            assigned = self._find_slot(task, available, scheduled_items)
            if assigned:
                scheduled_items.append(assigned)
                schedule.items.append(assigned)
            else:
                schedule.notes.append(f"Could not place {task.title}")
        schedule.notes += self._explain(schedule)
        return schedule

    def _build_available_slots(self, owner: Owner, pet: Pet, day: date) -> List[TimeWindow]:
        """Extract available time slots from owner and pet constraints."""
        available = owner.availability.copy()
        # Remove pet rest blocks
        for rest in pet.rest_blocks:
            available = self._subtract_window(available, rest)
        # Remove owner quiet hours
        for quiet in owner.preferences.quiet_hrs:
            available = self._subtract_window(available, quiet)
        return available

    def _subtract_window(self, windows: List[TimeWindow], subtract: TimeWindow) -> List[TimeWindow]:
        """Subtract a time window from a list of windows."""
        result = []
        for window in windows:
            if not window.overlaps(subtract):
                result.append(window)
            else:
                # Split the window around the subtract window
                if window.start < subtract.start:
                    result.append(TimeWindow(window.start, min(window.end, subtract.start)))
                if window.end > subtract.end:
                    result.append(TimeWindow(max(window.start, subtract.end), window.end))
        return result

    def _score_and_sort(self, tasks: List[PetTask], owner: Owner, pet: Pet) -> List[PetTask]:
        """Rank tasks by priority, urgency, and preferences."""
        today = date.today()
        scored_tasks = []
        for task in tasks:
            days_overdue = (today - (task.last_done_date or today - timedelta(days=1))).days
            score = self.rules.calculate_score(task, owner, pet, days_overdue)
            scored_tasks.append((score, task))
        scored_tasks.sort(key=lambda x: x[0], reverse=True)
        return [task for _, task in scored_tasks]

    def _find_slot(self, task: PetTask, available_windows: List[TimeWindow], scheduled_items: List[ScheduledItem]) -> Optional[ScheduledItem]:
        """Locate a time window for a task and create ScheduledItem."""
        for window in available_windows:
            if not task.fits_in_window(window):
                continue
            # Candidate start times: window.start, plus end of any item that falls within this window
            candidate_starts = [window.start] + [
                item.end for item in scheduled_items
                if window.start <= item.end <= window.end
            ]
            candidate_starts.sort()
            for candidate_start in candidate_starts:
                if task.preferred_window and task.preferred_window.is_working(window.start):
                    candidate_start = max(candidate_start, task.preferred_window.start)
                candidate_end_dt = datetime.combine(date.today(), candidate_start) + timedelta(minutes=task.duration_min)
                candidate_end_time = candidate_end_dt.time()
                if candidate_end_time > window.end:
                    continue
                candidate_item = ScheduledItem(
                    task=task,
                    start=candidate_start,
                    end=candidate_end_time,
                    reason=self._generate_reason(task, window, task.preferred_window)
                )
                if not self._detect_conflicts(candidate_item, scheduled_items):
                    return candidate_item
        return None

    def _detect_conflicts(self, item: ScheduledItem, items: List[ScheduledItem]) -> bool:
        """Check if newly scheduled item conflicts with existing items."""
        return any(item.overlaps_with(existing) for existing in items)

    def _generate_reason(self, task: PetTask, window: TimeWindow, preferred: Optional[TimeWindow] = None) -> str:
        """Generate human-readable explanation for scheduling decision."""
        reasons = []
        if task.mandatory:
            reasons.append("mandatory task")
        if preferred and task.respects_preferred_window(window.start):
            reasons.append("fits preferred time window")
        reasons.append(f"high priority ({task.priority})")
        return ", ".join(reasons)

    def _explain(self, schedule: DailySchedule) -> List[str]:
        """Generate comprehensive explanation notes for the schedule."""
        notes = []
        total_time = schedule.total_minutes_scheduled()
        if total_time > schedule.owner.preferences.max_activity_minutes:
            notes.append(f"Warning: Scheduled time ({total_time} min) exceeds max activity limit.")
        mandatory_count = len(schedule.get_mandatory_tasks())
        notes.append(f"Successfully scheduled {len(schedule.items)} tasks, including {mandatory_count} mandatory.")
        return notes