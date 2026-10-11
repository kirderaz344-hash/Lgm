import os
from collections.abc import Sequence

import reflex as rx
import reflex_enterprise as rxe
from reflex_enterprise.auth import AuthUserState

_PROVIDER_NAME = os.environ.get("OIDC_PROVIDER_NAME", "")
_LOGIN_LABEL = (
    f"Continue with {_PROVIDER_NAME}" if _PROVIDER_NAME else "Sign in"
)


class LoginRedirectState(rx.State):
    @rxe.event(auth=False)
    def continue_to_app(self):
        raw = self.router.page.params.get("redirect_to", "/")
        target = (
            raw
            if isinstance(raw, str)
            and raw.startswith("/")
            and not raw.startswith("//")
            and not any(c in raw for c in "\t\r\n\\")
            else "/"
        )
        return rx.redirect(target)


def login_page(*, providers: Sequence, **context) -> rx.Component:
    return rx.fragment(
        rx.el.main(
            rx.el.section(
                rx.el.div(
                    rx.icon(
                        "square_check", class_name="h-6 w-6 text-[#137C73]"
                    ),
                    rx.el.span(
                        "کارها و یادداشت‌ها",
                        class_name="text-lg font-semibold text-[#182D32]",
                    ),
                    class_name="mb-8 flex items-center justify-center gap-2",
                ),
                rx.el.div(
                    rx.el.h1(
                        "خوش آمدید",
                        class_name="text-2xl font-semibold tracking-tight text-[#182D32]",
                    ),
                    rx.el.p(
                        "برای ورود به فضای شخصی خود، وارد حساب شوید.",
                        class_name="mt-2 text-sm font-medium text-[#53666A]",
                    ),
                    rx.el.div(
                        *[
                            provider.get_login_button(
                                rx.el.button(
                                    _LOGIN_LABEL,
                                    rx.icon("arrow-left", class_name="h-4 w-4"),
                                    class_name="flex w-full items-center justify-center gap-2 rounded-lg bg-[#137C73] px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#0F665F] focus:outline-hidden focus:ring-2 focus:ring-[#137C73] focus:ring-offset-2",
                                ),
                            )
                            for provider in providers
                        ],
                        class_name="mt-8",
                    ),
                    class_name="w-full rounded-2xl border border-[#E4E5DE] bg-white p-8 text-center sm:p-10",
                ),
                class_name="w-full max-w-md",
            ),
            dir="rtl",
            class_name="flex min-h-screen items-center justify-center bg-[#F8F7F3] px-4 py-12 font-['Vazirmatn'] text-[#182D32]",
        ),
        rx.cond(
            AuthUserState.provider_name != "",
            rx.el.div(on_mount=LoginRedirectState.continue_to_app),
        ),
    )
