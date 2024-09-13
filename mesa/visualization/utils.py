import solara

update_counter = solara.reactive(0)


def force_update():
    update_counter.value += 1
