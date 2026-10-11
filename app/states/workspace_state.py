import logging
from datetime import date
from typing import TypedDict, Any

import reflex as rx
import reflex_enterprise as rxe
from sqlalchemy import select
from reflex_enterprise.auth import User

from app.models import Note, Task


class TaskItem(TypedDict):
    id: int
    title: str
    description: str
    completed: bool
    due_date: str
    priority: int


class NoteItem(TypedDict):
    id: int
    title: str
    body: str
    pinned: bool


class WorkspaceState(rx.State):
    tasks: list[TaskItem] = []
    notes: list[NoteItem] = []
    search_query: str = ""
    task_filter: str = "all"
    task_title: str = ""
    task_description: str = ""
    task_due_date: str = ""
    task_priority: str = "0"
    task_edit_id: int = 0
    task_form_revision: int = 0
    note_title: str = ""
    note_body: str = ""
    note_edit_id: int = 0
    note_form_revision: int = 0
    message: str = ""
    message_is_error: bool = False
    confirm_delete: bool = False
    delete_kind: str = ""
    delete_id: int = 0

    @rx.var
    def visible_tasks(self) -> list[TaskItem]:
        query = self.search_query.strip().lower()
        rows = [
            row
            for row in self.tasks
            if query in row["title"].lower()
            or query in row["description"].lower()
        ]
        if self.task_filter == "active":
            return [row for row in rows if not row["completed"]]
        if self.task_filter == "completed":
            return [row for row in rows if row["completed"]]
        return rows

    @rx.var
    def visible_notes(self) -> list[NoteItem]:
        query = self.search_query.strip().lower()
        return [
            row
            for row in self.notes
            if query in row["title"].lower() or query in row["body"].lower()
        ]

    @rx.var
    def task_count(self) -> int:
        return len(self.tasks)

    @rx.var
    def open_task_count(self) -> int:
        return sum(not row["completed"] for row in self.tasks)

    @rx.var
    def completed_task_count(self) -> int:
        return sum(row["completed"] for row in self.tasks)

    @rx.var
    def note_count(self) -> int:
        return len(self.notes)

    @rx.var
    def pinned_note_count(self) -> int:
        return sum(row["pinned"] for row in self.notes)

    def _read_rows(
        self, owner_sub: str
    ) -> tuple[list[TaskItem], list[NoteItem]]:
        with rx.session() as session:
            task_rows = session.scalars(
                select(Task)
                .where(Task.owner_sub == owner_sub)
                .order_by(Task.completed, Task.due_date, Task.id.desc())
            ).all()
            note_rows = session.scalars(
                select(Note)
                .where(Note.owner_sub == owner_sub)
                .order_by(
                    Note.pinned.desc(), Note.updated_at.desc(), Note.id.desc()
                )
            ).all()
            tasks = [
                {
                    "id": row.id,
                    "title": row.title,
                    "description": row.description or "",
                    "completed": row.completed,
                    "due_date": row.due_date.isoformat()
                    if row.due_date
                    else "",
                    "priority": row.priority,
                }
                for row in task_rows
            ]
            notes = [
                {
                    "id": row.id,
                    "title": row.title,
                    "body": row.body,
                    "pinned": row.pinned,
                }
                for row in note_rows
            ]
        return tasks, notes

    async def _load_for_current_user(self) -> bool:
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            self.tasks = []
            self.notes = []
            return False
        try:
            tasks, notes = self._read_rows(owner_sub)
            self.tasks = tasks
            self.notes = notes
            return True
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = (
                "بارگذاری اطلاعات با خطا روبه‌رو شد. دوباره تلاش کنید."
            )
            self.message_is_error = True
            return False

    @rxe.event
    async def load_data(self):
        await self._load_for_current_user()

    @rxe.event
    def set_search(self, value: str):
        self.search_query = value

    @rxe.event
    def set_task_filter(self, value: str):
        self.task_filter = value

    @rxe.event
    def clear_task_form(self):
        self.task_edit_id = 0
        self.task_title = ""
        self.task_description = ""
        self.task_due_date = ""
        self.task_priority = "0"
        self.task_form_revision += 1
        self.message = ""
        self.message_is_error = False

    @rxe.event
    def clear_note_form(self):
        self.note_edit_id = 0
        self.note_title = ""
        self.note_body = ""
        self.note_form_revision += 1
        self.message = ""
        self.message_is_error = False

    @rxe.event
    async def save_task(self, form_data: dict[str, Any]):
        title = str(form_data.get("title", "")).strip()
        description = str(form_data.get("description", "")).strip()
        due_value = str(form_data.get("due_date", "")).strip()
        priority_value = str(form_data.get("priority", "0")).strip()
        if not title:
            self.message = "برای کار، عنوان وارد کنید."
            self.message_is_error = True
            return
        try:
            priority = int(priority_value)
            if priority not in (0, 1, 2):
                raise ValueError("priority out of range")
            due_date = date.fromisoformat(due_value) if due_value else None
        except ValueError:
            self.message = "اولویت یا تاریخ واردشده معتبر نیست."
            self.message_is_error = True
            return
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            self.message = "نشست کاربری معتبر نیست. دوباره وارد شوید."
            self.message_is_error = True
            return
        try:
            with rx.session() as session:
                if self.task_edit_id:
                    row = session.scalar(
                        select(Task).where(
                            Task.id == self.task_edit_id,
                            Task.owner_sub == owner_sub,
                        )
                    )
                    if row is None:
                        self.message = "این کار پیدا نشد."
                        self.message_is_error = True
                        return
                    row.title = title
                    row.description = description
                    row.due_date = due_date
                    row.priority = priority
                else:
                    session.add(
                        Task(
                            owner_sub=owner_sub,
                            title=title,
                            description=description,
                            due_date=due_date,
                            priority=priority,
                        )
                    )
                session.commit()
            self.task_edit_id = 0
            self.task_title = ""
            self.task_description = ""
            self.task_due_date = ""
            self.task_priority = "0"
            self.task_form_revision += 1
            self.message = "کار با موفقیت ذخیره شد."
            self.message_is_error = False
            await self._load_for_current_user()
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "ذخیرهٔ کار انجام نشد. دوباره تلاش کنید."
            self.message_is_error = True

    @rxe.event
    async def edit_task(self, task_id: int):
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            return
        try:
            with rx.session() as session:
                row = session.scalar(
                    select(Task).where(
                        Task.id == task_id,
                        Task.owner_sub == owner_sub,
                    )
                )
                if row is None:
                    self.message = "این کار پیدا نشد."
                    self.message_is_error = True
                    return
                self.task_edit_id = row.id
                self.task_title = row.title
                self.task_description = row.description or ""
                self.task_due_date = (
                    row.due_date.isoformat() if row.due_date else ""
                )
                self.task_priority = str(row.priority)
                self.task_form_revision += 1
                self.message = ""
                self.message_is_error = False
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "بارگذاری کار برای ویرایش انجام نشد."
            self.message_is_error = True

    @rxe.event
    async def toggle_task(self, task_id: int):
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            return
        try:
            with rx.session() as session:
                row = session.scalar(
                    select(Task).where(
                        Task.id == task_id, Task.owner_sub == owner_sub
                    )
                )
                if row is None:
                    return
                row.completed = not row.completed
                session.commit()
            await self._load_for_current_user()
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "به‌روزرسانی وضعیت کار انجام نشد."
            self.message_is_error = True

    @rxe.event
    async def save_note(self, form_data: dict[str, Any]):
        title = str(form_data.get("title", "")).strip()
        body = str(form_data.get("body", "")).strip()
        if not title:
            self.message = "برای یادداشت، عنوان وارد کنید."
            self.message_is_error = True
            return
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            self.message = "نشست کاربری معتبر نیست. دوباره وارد شوید."
            self.message_is_error = True
            return
        try:
            with rx.session() as session:
                if self.note_edit_id:
                    row = session.scalar(
                        select(Note).where(
                            Note.id == self.note_edit_id,
                            Note.owner_sub == owner_sub,
                        )
                    )
                    if row is None:
                        self.message = "این یادداشت پیدا نشد."
                        self.message_is_error = True
                        return
                    row.title = title
                    row.body = body
                else:
                    session.add(
                        Note(owner_sub=owner_sub, title=title, body=body)
                    )
                session.commit()
            self.note_edit_id = 0
            self.note_title = ""
            self.note_body = ""
            self.note_form_revision += 1
            self.message = "یادداشت با موفقیت ذخیره شد."
            self.message_is_error = False
            await self._load_for_current_user()
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "ذخیرهٔ یادداشت انجام نشد. دوباره تلاش کنید."
            self.message_is_error = True

    @rxe.event
    async def edit_note(self, note_id: int):
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            return
        try:
            with rx.session() as session:
                row = session.scalar(
                    select(Note).where(
                        Note.id == note_id,
                        Note.owner_sub == owner_sub,
                    )
                )
                if row is None:
                    self.message = "این یادداشت پیدا نشد."
                    self.message_is_error = True
                    return
                self.note_edit_id = row.id
                self.note_title = row.title
                self.note_body = row.body
                self.note_form_revision += 1
                self.message = ""
                self.message_is_error = False
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "بارگذاری یادداشت برای ویرایش انجام نشد."
            self.message_is_error = True

    @rxe.event
    async def toggle_note_pin(self, note_id: int):
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            return
        try:
            with rx.session() as session:
                row = session.scalar(
                    select(Note).where(
                        Note.id == note_id, Note.owner_sub == owner_sub
                    )
                )
                if row is None:
                    return
                row.pinned = not row.pinned
                session.commit()
            await self._load_for_current_user()
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "تغییر وضعیت سنجاق یادداشت انجام نشد."
            self.message_is_error = True

    @rxe.event
    def ask_delete(self, kind: str, row_id: int):
        if kind not in ("task", "note"):
            return
        self.delete_kind = kind
        self.delete_id = row_id
        self.confirm_delete = True

    @rxe.event
    def cancel_delete(self):
        self.confirm_delete = False
        self.delete_kind = ""
        self.delete_id = 0

    @rxe.event
    async def confirm_delete_row(self):
        user = await User.current() or {}
        owner_sub = user.get("sub")
        if not isinstance(owner_sub, str) or not owner_sub:
            self.confirm_delete = False
            self.delete_kind = ""
            self.delete_id = 0
            return
        try:
            with rx.session() as session:
                if self.delete_kind == "task":
                    row = session.scalar(
                        select(Task).where(
                            Task.id == self.delete_id,
                            Task.owner_sub == owner_sub,
                        )
                    )
                elif self.delete_kind == "note":
                    row = session.scalar(
                        select(Note).where(
                            Note.id == self.delete_id,
                            Note.owner_sub == owner_sub,
                        )
                    )
                else:
                    row = None
                if row is not None:
                    session.delete(row)
                    session.commit()
            self.confirm_delete = False
            self.delete_kind = ""
            self.delete_id = 0
            self.message = "مورد انتخاب‌شده حذف شد."
            self.message_is_error = False
            await self._load_for_current_user()
        except Exception as e:
            logging.exception(f"Error: {e}")
            self.message = "حذف انجام نشد. دوباره تلاش کنید."
            self.message_is_error = True
            self.confirm_delete = False
