"""Solara related utils."""

import solara

update_counter = solara.reactive(0)


def force_update():  # noqa
    update_counter.value += 1
