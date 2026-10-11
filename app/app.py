import reflex as rx
import reflex_enterprise as rxe
from reflex_enterprise.auth import User

from app.states.workspace_state import NoteItem, TaskItem, WorkspaceState


def task_card(item: TaskItem) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.el.button(
                rx.cond(
                    item["completed"],
                    rx.icon("rotate-ccw", class_name="h-4 w-4"),
                    rx.icon("check", class_name="h-4 w-4"),
                ),
                title=rx.cond(item["completed"], "بازگرداندن کار", "انجام شد"),
                on_click=WorkspaceState.toggle_task(item["id"]),
                class_name=rx.cond(
                    item["completed"],
                    "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#C6D9D4] bg-[#E8F1EE] text-[#137C73] hover:bg-[#DCEBE6]",
                    "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-[#D9DED9] bg-white text-[#53666A] hover:border-[#137C73] hover:text-[#137C73]",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        item["title"],
                        class_name=rx.cond(
                            item["completed"],
                            "text-base font-semibold text-[#758386] line-through",
                            "text-base font-semibold text-[#182D32]",
                        ),
                    ),
                    rx.match(
                        item["priority"],
                        (
                            2,
                            rx.el.span(
                                "اولویت بالا",
                                class_name="rounded-full bg-[#FBF0D9] px-2.5 py-1 text-xs font-semibold text-[#9A6815]",
                            ),
                        ),
                        (
                            1,
                            rx.el.span(
                                "اولویت متوسط",
                                class_name="rounded-full bg-[#F7F1E5] px-2.5 py-1 text-xs font-semibold text-[#8A744C]",
                            ),
                        ),
                        rx.el.span(
                            "عادی",
                            class_name="rounded-full bg-[#F0F1EC] px-2.5 py-1 text-xs font-semibold text-[#687477]",
                        ),
                    ),
                    class_name="flex flex-wrap items-center gap-2",
                ),
                rx.cond(
                    item["description"],
                    rx.el.p(
                        item["description"],
                        class_name="mt-2 whitespace-pre-wrap text-sm leading-7 text-[#58696C]",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    item["due_date"],
                    rx.el.div(
                        rx.icon("calendar-days", class_name="h-3.5 w-3.5"),
                        rx.el.span(item["due_date"], dir="ltr"),
                        class_name="mt-3 flex w-fit items-center gap-1.5 text-xs font-medium text-[#758386]",
                    ),
                    rx.fragment(),
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="h-4 w-4"),
                    title="ویرایش",
                    on_click=WorkspaceState.edit_task(item["id"]),
                    class_name="rounded-lg p-2 text-[#53666A] hover:bg-[#F0F1EC] hover:text-[#137C73]",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4"),
                    title="حذف",
                    on_click=WorkspaceState.ask_delete("task", item["id"]),
                    class_name="rounded-lg p-2 text-[#879294] hover:bg-[#F9EAE5] hover:text-[#A34F3B]",
                ),
                class_name="flex shrink-0 items-start gap-1",
            ),
            class_name="flex items-start gap-3",
        ),
        class_name="rounded-xl border border-[#E7E7E0] bg-white p-4 sm:p-5",
    )


def note_card(item: NoteItem) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        item["title"],
                        class_name="text-base font-semibold text-[#182D32]",
                    ),
                    rx.cond(
                        item["pinned"],
                        rx.el.span(
                            rx.icon("pin", class_name="h-3.5 w-3.5"),
                            "سنجاق‌شده",
                            class_name="flex w-fit items-center gap-1 rounded-full bg-[#FBF0D9] px-2.5 py-1 text-xs font-semibold text-[#9A6815]",
                        ),
                        rx.fragment(),
                    ),
                    class_name="flex flex-wrap items-center gap-2",
                ),
                rx.cond(
                    item["body"],
                    rx.el.p(
                        item["body"],
                        class_name="mt-3 whitespace-pre-wrap break-words text-sm leading-7 text-[#58696C]",
                    ),
                    rx.el.p(
                        "این یادداشت هنوز متنی ندارد.",
                        class_name="mt-3 text-sm text-[#98A2A1]",
                    ),
                ),
                class_name="min-w-0 flex-1",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("pin", class_name="h-4 w-4"),
                    title=rx.cond(
                        item["pinned"], "برداشتن سنجاق", "سنجاق کردن"
                    ),
                    on_click=WorkspaceState.toggle_note_pin(item["id"]),
                    class_name=rx.cond(
                        item["pinned"],
                        "rounded-lg bg-[#FBF0D9] p-2 text-[#9A6815] hover:bg-[#F6E7C4]",
                        "rounded-lg p-2 text-[#758386] hover:bg-[#F0F1EC] hover:text-[#9A6815]",
                    ),
                ),
                rx.el.button(
                    rx.icon("pencil", class_name="h-4 w-4"),
                    title="ویرایش",
                    on_click=WorkspaceState.edit_note(item["id"]),
                    class_name="rounded-lg p-2 text-[#53666A] hover:bg-[#F0F1EC] hover:text-[#137C73]",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="h-4 w-4"),
                    title="حذف",
                    on_click=WorkspaceState.ask_delete("note", item["id"]),
                    class_name="rounded-lg p-2 text-[#879294] hover:bg-[#F9EAE5] hover:text-[#A34F3B]",
                ),
                class_name="flex shrink-0 items-start gap-1",
            ),
            class_name="flex items-start gap-3",
        ),
        class_name="rounded-xl border border-[#E7E7E0] bg-white p-4 sm:p-5",
    )


def task_form() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    rx.cond(
                        WorkspaceState.task_edit_id > 0,
                        "ویرایش کار",
                        "کار تازه",
                    ),
                    class_name="text-base font-semibold text-[#182D32]",
                ),
                rx.el.button(
                    rx.icon("rotate-ccw", class_name="h-4 w-4"),
                    "پاک‌کردن فرم",
                    on_click=WorkspaceState.clear_task_form,
                    class_name="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-medium text-[#758386] hover:bg-[#F0F1EC]",
                ),
                class_name="flex items-center justify-between gap-3",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "عنوان",
                        html_for="task-title",
                        class_name="mb-1.5 block text-sm font-medium text-[#405458]",
                    ),
                    rx.el.input(
                        id="task-title",
                        name="title",
                        placeholder="مثلاً: تماس با همکار",
                        default_value=WorkspaceState.task_title,
                        key=WorkspaceState.task_title,
                        required=True,
                        max_length=255,
                        class_name="w-full rounded-lg border border-[#DDE1DA] bg-white px-3.5 py-2.5 text-sm text-[#182D32] placeholder:text-[#A0AAA7] focus:border-[#137C73] focus:outline-hidden",
                    ),
                    class_name="sm:col-span-2",
                ),
                rx.el.div(
                    rx.el.label(
                        "توضیحات",
                        html_for="task-description",
                        class_name="mb-1.5 block text-sm font-medium text-[#405458]",
                    ),
                    rx.el.textarea(
                        id="task-description",
                        name="description",
                        placeholder="جزئیات یا یادآوری کوتاه…",
                        default_value=WorkspaceState.task_description,
                        key=WorkspaceState.task_description,
                        rows=3,
                        class_name="w-full resize-y rounded-lg border border-[#DDE1DA] bg-white px-3.5 py-2.5 text-sm leading-6 text-[#182D32] placeholder:text-[#A0AAA7] focus:border-[#137C73] focus:outline-hidden",
                    ),
                    class_name="sm:col-span-2",
                ),
                rx.el.div(
                    rx.el.label(
                        "تاریخ سررسید",
                        html_for="task-date",
                        class_name="mb-1.5 block text-sm font-medium text-[#405458]",
                    ),
                    rx.el.input(
                        id="task-date",
                        name="due_date",
                        type="date",
                        default_value=WorkspaceState.task_due_date,
                        key=WorkspaceState.task_due_date,
                        dir="ltr",
                        class_name="w-full rounded-lg border border-[#DDE1DA] bg-white px-3 py-2.5 text-sm text-[#182D32] focus:border-[#137C73] focus:outline-hidden",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "اولویت",
                        html_for="task-priority",
                        class_name="mb-1.5 block text-sm font-medium text-[#405458]",
                    ),
                    rx.el.div(
                        rx.el.select(
                            rx.el.option("عادی", value="0"),
                            rx.el.option("متوسط", value="1"),
                            rx.el.option("بالا", value="2"),
                            id="task-priority",
                            name="priority",
                            default_value=WorkspaceState.task_priority,
                            key=WorkspaceState.task_priority,
                            class_name="w-full appearance-none rounded-lg border border-[#DDE1DA] bg-white px-3.5 py-2.5 pl-9 text-sm text-[#182D32] focus:border-[#137C73] focus:outline-hidden",
                        ),
                        rx.icon(
                            "chevron-down",
                            class_name="pointer-events-none absolute left-3 top-3 h-4 w-4 text-[#758386]",
                        ),
                        class_name="relative",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        rx.cond(
                            WorkspaceState.task_edit_id > 0,
                            "ذخیرهٔ تغییرات",
                            "افزودن کار",
                        ),
                        rx.icon("plus", class_name="h-4 w-4"),
                        type="submit",
                        class_name="flex w-full items-center justify-center gap-2 rounded-lg bg-[#137C73] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F665F] focus:outline-hidden focus:ring-2 focus:ring-[#137C73] focus:ring-offset-2",
                    ),
                    class_name="self-end",
                ),
                class_name="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2",
                on_submit=WorkspaceState.save_task,
            ),
            class_name="rounded-xl border border-[#E4E5DE] bg-[#FCFCF9] p-4 sm:p-5",
        ),
    )


def note_form() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    rx.cond(
                        WorkspaceState.note_edit_id > 0,
                        "ویرایش یادداشت",
                        "یادداشت تازه",
                    ),
                    class_name="text-base font-semibold text-[#182D32]",
                ),
                rx.el.button(
                    rx.icon("rotate-ccw", class_name="h-4 w-4"),
                    "پاک‌کردن فرم",
                    on_click=WorkspaceState.clear_note_form,
                    class_name="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-medium text-[#758386] hover:bg-[#F0F1EC]",
                ),
                class_name="flex items-center justify-between gap-3",
            ),
            rx.el.form(
                rx.el.div(
                    rx.el.label(
                        "عنوان",
                        html_for="note-title",
                        class_name="mb-1.5 block text-sm font-medium text-[#405458]",
                    ),
                    rx.el.input(
                        id="note-title",
                        name="title",
                        placeholder="عنوان یادداشت",
                        default_value=WorkspaceState.note_title,
                        key=WorkspaceState.note_title,
                        required=True,
                        max_length=255,
                        class_name="w-full rounded-lg border border-[#DDE1DA] bg-white px-3.5 py-2.5 text-sm text-[#182D32] placeholder:text-[#A0AAA7] focus:border-[#137C73] focus:outline-hidden",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        "متن یادداشت",
                        html_for="note-body",
                        class_name="mb-1.5 block text-sm font-medium text-[#405458]",
                    ),
                    rx.el.textarea(
                        id="note-body",
                        name="body",
                        placeholder="هر فکری که می‌خواهید نگه دارید…",
                        default_value=WorkspaceState.note_body,
                        key=WorkspaceState.note_body,
                        rows=5,
                        class_name="w-full resize-y rounded-lg border border-[#DDE1DA] bg-white px-3.5 py-2.5 text-sm leading-7 text-[#182D32] placeholder:text-[#A0AAA7] focus:border-[#137C73] focus:outline-hidden",
                    ),
                ),
                rx.el.button(
                    rx.cond(
                        WorkspaceState.note_edit_id > 0,
                        "ذخیرهٔ تغییرات",
                        "ذخیرهٔ یادداشت",
                    ),
                    rx.icon("plus", class_name="h-4 w-4"),
                    type="submit",
                    class_name="mt-1 flex w-full items-center justify-center gap-2 rounded-lg bg-[#137C73] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0F665F] focus:outline-hidden focus:ring-2 focus:ring-[#137C73] focus:ring-offset-2",
                ),
                class_name="mt-4 flex flex-col gap-3",
                on_submit=WorkspaceState.save_note,
            ),
            class_name="rounded-xl border border-[#E4E5DE] bg-[#FCFCF9] p-4 sm:p-5",
        ),
    )


def delete_dialog() -> rx.Component:
    return rx.cond(
        WorkspaceState.confirm_delete,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "triangle-alert",
                            class_name="h-5 w-5 text-[#A34F3B]",
                        ),
                        class_name="flex h-10 w-10 items-center justify-center rounded-full bg-[#F9EAE5]",
                    ),
                    rx.el.h2(
                        "حذف این مورد؟",
                        class_name="mt-4 text-lg font-semibold text-[#182D32]",
                    ),
                    rx.el.p(
                        "این کار قابل بازگشت نیست.",
                        class_name="mt-2 text-sm leading-6 text-[#667679]",
                    ),
                    class_name="text-center",
                ),
                rx.el.div(
                    rx.el.button(
                        "انصراف",
                        on_click=WorkspaceState.cancel_delete,
                        class_name="flex-1 rounded-lg border border-[#DDE1DA] bg-white px-4 py-2.5 text-sm font-semibold text-[#405458] hover:bg-[#F5F5F0]",
                    ),
                    rx.el.button(
                        "حذف نهایی",
                        on_click=WorkspaceState.confirm_delete_row,
                        class_name="flex-1 rounded-lg bg-[#A34F3B] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#8D4232]",
                    ),
                    class_name="mt-6 flex gap-3",
                ),
                class_name="w-full max-w-sm rounded-2xl border border-[#E4E5DE] bg-white p-6",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-[#182D32]/35 px-4",
        ),
        rx.fragment(),
    )


def index() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "square-check", class_name="h-5 w-5 text-[#137C73]"
                        ),
                        class_name="flex h-10 w-10 items-center justify-center rounded-xl bg-[#E4F0EC]",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "دفتر روزانه",
                            class_name="text-[11px] font-semibold tracking-[0.15em] text-[#758386]",
                        ),
                        rx.el.h1(
                            "کارها و یادداشت‌ها",
                            class_name="text-lg font-bold text-[#182D32] sm:text-xl",
                        ),
                        class_name="leading-tight",
                    ),
                    class_name="flex items-center gap-3",
                ),
                rx.el.div(
                    rx.el.span(
                        User.name,
                        class_name="max-w-36 truncate text-sm font-medium text-[#53666A]",
                    ),
                    rx.el.button(
                        rx.icon("log-out", class_name="h-4 w-4"),
                        "خروج",
                        on_click=User.logout,
                        class_name="flex items-center gap-2 rounded-lg border border-[#E1E3DC] bg-white px-3 py-2 text-sm font-semibold text-[#53666A] transition-colors hover:bg-[#F0F1EC]",
                    ),
                    class_name="flex items-center gap-3",
                ),
                class_name="mx-auto flex w-full max-w-[1440px] items-center justify-between gap-4 px-4 py-3 sm:px-8",
            ),
            class_name="border-b border-[#E6E7E0] bg-[#F8F7F3]",
        ),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "فضای شخصی شما",
                                class_name="text-sm font-medium text-[#758386]",
                            ),
                            rx.el.h2(
                                "یک روز روشن‌تر، با ذهنی مرتب‌تر.",
                                class_name="mt-1 text-2xl font-bold leading-relaxed text-[#182D32] sm:text-3xl",
                            ),
                            rx.el.p(
                                "کارهای مهم را پیش ببرید و فکرهای خوب را نگه دارید.",
                                class_name="mt-1 text-sm leading-7 text-[#647477]",
                            ),
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    "کارهای باز",
                                    class_name="text-xs font-medium text-[#758386]",
                                ),
                                rx.el.strong(
                                    WorkspaceState.open_task_count,
                                    class_name="mt-1 block text-2xl font-bold text-[#182D32]",
                                ),
                                class_name="min-w-28 rounded-xl border border-[#E4E5DE] bg-white px-4 py-3",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "انجام‌شده",
                                    class_name="text-xs font-medium text-[#758386]",
                                ),
                                rx.el.strong(
                                    WorkspaceState.completed_task_count,
                                    class_name="mt-1 block text-2xl font-bold text-[#137C73]",
                                ),
                                class_name="min-w-28 rounded-xl border border-[#E4E5DE] bg-white px-4 py-3",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "یادداشت‌ها",
                                    class_name="text-xs font-medium text-[#758386]",
                                ),
                                rx.el.strong(
                                    WorkspaceState.note_count,
                                    class_name="mt-1 block text-2xl font-bold text-[#182D32]",
                                ),
                                class_name="min-w-28 rounded-xl border border-[#E4E5DE] bg-white px-4 py-3",
                            ),
                            class_name="flex flex-wrap gap-2",
                        ),
                        class_name="flex flex-col justify-between gap-6 lg:flex-row lg:items-end",
                    ),
                    rx.el.div(
                        rx.icon("search", class_name="h-4 w-4 text-[#758386]"),
                        rx.el.input(
                            placeholder="جست‌وجو در کارها و یادداشت‌ها…",
                            aria_label="جست‌وجو در کارها و یادداشت‌ها",
                            default_value="",
                            key="workspace-search",
                            on_change=WorkspaceState.set_search.debounce(350),
                            class_name="w-full border-0 bg-transparent text-sm text-[#182D32] outline-hidden placeholder:text-[#98A2A1]",
                        ),
                        class_name="mt-6 flex w-full items-center gap-3 rounded-xl border border-[#E1E3DC] bg-white px-4 py-3 sm:max-w-md",
                    ),
                    rx.cond(
                        WorkspaceState.message,
                        rx.el.div(
                            rx.icon(
                                rx.cond(
                                    WorkspaceState.message_is_error,
                                    "circle-alert",
                                    "circle-check",
                                ),
                                class_name="h-4 w-4 shrink-0",
                            ),
                            rx.el.p(
                                WorkspaceState.message,
                                class_name="text-sm font-medium",
                            ),
                            class_name=rx.cond(
                                WorkspaceState.message_is_error,
                                "mt-4 flex items-center gap-2 rounded-lg border border-[#F0D4CC] bg-[#F9EAE5] px-4 py-3 text-[#A34F3B]",
                                "mt-4 flex items-center gap-2 rounded-lg border border-[#CFE2D9] bg-[#EAF3EE] px-4 py-3 text-[#286A54]",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    class_name="mb-7",
                ),
                rx.el.div(
                    rx.el.section(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "list-checks",
                                        class_name="h-5 w-5 text-[#137C73]",
                                    ),
                                    class_name="flex h-10 w-10 items-center justify-center rounded-xl bg-[#E4F0EC]",
                                ),
                                rx.el.div(
                                    rx.el.h2(
                                        "فهرست کارها",
                                        class_name="text-lg font-bold text-[#182D32]",
                                    ),
                                    rx.el.p(
                                        f"{WorkspaceState.task_count} کار در مجموع",
                                        class_name="mt-0.5 text-xs text-[#758386]",
                                    ),
                                ),
                                class_name="flex items-center gap-3",
                            ),
                            class_name="flex items-center justify-between gap-3",
                        ),
                        rx.el.div(
                            rx.foreach(
                                [
                                    {"value": "all", "label": "همه"},
                                    {"value": "active", "label": "باز"},
                                    {"value": "completed", "label": "انجام‌شده"},
                                ],
                                lambda option: rx.el.button(
                                    option["label"],
                                    on_click=WorkspaceState.set_task_filter(
                                        option["value"]
                                    ),
                                    class_name=rx.cond(
                                        WorkspaceState.task_filter
                                        == option["value"],
                                        "rounded-full bg-[#182D32] px-3.5 py-1.5 text-xs font-semibold text-white",
                                        "rounded-full bg-[#F0F1EC] px-3.5 py-1.5 text-xs font-semibold text-[#647477] hover:bg-[#E6E8E1]",
                                    ),
                                ),
                            ),
                            class_name="mt-5 flex flex-wrap gap-2",
                        ),
                        rx.el.div(class_name="my-5 h-px bg-[#E9EAE4]"),
                        task_form(),
                        rx.el.div(
                            rx.cond(
                                WorkspaceState.visible_tasks.length() > 0,
                                rx.el.div(
                                    rx.foreach(
                                        WorkspaceState.visible_tasks, task_card
                                    ),
                                    class_name="mt-5 flex flex-col gap-3",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "list-todo",
                                        class_name="h-8 w-8 text-[#A3AEAA]",
                                    ),
                                    rx.el.p(
                                        "هنوز کاری در این فهرست نیست.",
                                        class_name="mt-3 text-sm font-semibold text-[#53666A]",
                                    ),
                                    rx.el.p(
                                        "یک کار تازه اضافه کنید یا فیلتر دیگری را ببینید.",
                                        class_name="mt-1 text-xs leading-6 text-[#8A9797]",
                                    ),
                                    class_name="mt-5 flex flex-col items-center justify-center rounded-xl border border-dashed border-[#DDE1DA] bg-[#FCFCF9] px-5 py-10 text-center",
                                ),
                            ),
                        ),
                        class_name="min-w-0 rounded-2xl border border-[#E4E5DE] bg-white p-4 sm:p-6",
                    ),
                    rx.el.section(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.icon(
                                        "notebook-pen",
                                        class_name="h-5 w-5 text-[#137C73]",
                                    ),
                                    class_name="flex h-10 w-10 items-center justify-center rounded-xl bg-[#E4F0EC]",
                                ),
                                rx.el.div(
                                    rx.el.h2(
                                        "یادداشت‌ها",
                                        class_name="text-lg font-bold text-[#182D32]",
                                    ),
                                    rx.el.p(
                                        f"{WorkspaceState.pinned_note_count} یادداشت سنجاق‌شده",
                                        class_name="mt-0.5 text-xs text-[#758386]",
                                    ),
                                ),
                                class_name="flex items-center gap-3",
                            ),
                        ),
                        rx.el.div(class_name="my-5 h-px bg-[#E9EAE4]"),
                        note_form(),
                        rx.cond(
                            WorkspaceState.visible_notes.length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    WorkspaceState.visible_notes, note_card
                                ),
                                class_name="mt-5 flex flex-col gap-3",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "notebook",
                                    class_name="h-8 w-8 text-[#A3AEAA]",
                                ),
                                rx.el.p(
                                    "یادداشتی برای نمایش نیست.",
                                    class_name="mt-3 text-sm font-semibold text-[#53666A]",
                                ),
                                rx.el.p(
                                    "یادداشت‌هایتان را اینجا نگه دارید.",
                                    class_name="mt-1 text-xs leading-6 text-[#8A9797]",
                                ),
                                class_name="mt-5 flex flex-col items-center justify-center rounded-xl border border-dashed border-[#DDE1DA] bg-[#FCFCF9] px-5 py-10 text-center",
                            ),
                        ),
                        class_name="min-w-0 rounded-2xl border border-[#E4E5DE] bg-white p-4 sm:p-6",
                    ),
                    class_name="grid grid-cols-1 items-start gap-5 xl:grid-cols-2",
                ),
                rx.el.footer(
                    rx.el.p(
                        "فضایی آرام برای برنامه‌ها و فکرهای شما.",
                        class_name="text-xs text-[#879294]",
                    ),
                    class_name="mt-8 border-t border-[#E6E7E0] pt-5 text-center",
                ),
                class_name="mx-auto w-full max-w-[1440px] px-4 py-7 sm:px-8 sm:py-10",
            ),
            class_name="min-h-0 flex-1 overflow-y-auto",
        ),
        delete_dialog(),
        dir="rtl",
        class_name="flex h-dvh flex-col overflow-hidden bg-[#F8F7F3] font-['Vazirmatn'] text-[#182D32]",
    )


app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/", on_load=WorkspaceState.load_data)
