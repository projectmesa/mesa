import solara
import threading
import reacton.ipywidgets as widgets


@solara.component
def ModelController(
    model, play_interval, current_step, set_current_step, reset_counter
):
    playing = solara.use_reactive(False)
    thread = solara.use_reactive(None)
    # We track the previous step to detect if user resets the model via
    # clicking the reset button or changing the parameters. If previous_step >
    # current_step, it means a model reset happens while the simulation is
    # still playing.
    previous_step = solara.use_reactive(0)

    def on_value_play(change):
        if previous_step.value > current_step and current_step == 0:
            # We add extra checks for current_step == 0, just to be sure.
            # We automatically stop the playing if a model is reset.
            playing.value = False
        elif model.running:
            do_step()
        else:
            playing.value = False

    def do_step():
        model.step()
        previous_step.value = current_step
        set_current_step(model.schedule.steps)

    def do_play():
        model.running = True
        while model.running:
            do_step()

    def threaded_do_play():
        if thread is not None and thread.is_alive():
            return
        thread.value = threading.Thread(target=do_play)
        thread.start()

    def do_pause():
        if (thread is None) or (not thread.is_alive()):
            return
        model.running = False
        thread.join()

    def do_reset():
        reset_counter.value += 1

    with solara.Column():
        with solara.Row(gap="10px", justify="center"):
            solara.Button(
                label="Step",
                color="primary",
                text=True,
                outlined=True,
                on_click=do_step,
            )
            # This style is necessary so that the play widget has almost the same
            # height as typical Solara buttons.
            solara.Button(
                label="Reset",
                color="primary",
                text=True,
                outlined=True,
                on_click=do_reset,
            )

            # with solara.Row(gap="10px", justify="center"):
            solara.Style(
                """
            .widget-play {
                height: 35px;
            }
            """
            )
            widgets.Play(
                value=0,
                interval=play_interval,
                repeat=True,
                show_repeat=False,
                on_value=on_value_play,
                playing=playing.value,
                on_playing=playing.set,
            )


# threaded_do_play is not used for now because it
# doesn't work in Google colab. We use
# ipywidgets.Play until it is fixed. The threading
# version is definite a much better implementation,
# if it works.
# solara.Button(label="▶", color="primary", on_click=viz.threaded_do_play)
# solara.Button(label="⏸︎", color="primary", on_click=viz.do_pause)
# solara.Button(label="Reset", color="primary", on_click=do_reset)
