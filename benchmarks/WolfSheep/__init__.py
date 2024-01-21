from wolf_sheep import WolfSheep

if __name__ == "__main__":
    # for profiling this benchmark model
    import time

    # model = WolfSheep(15, 25, 25, 60, 40, 0.2, 0.1, 20)
    model = WolfSheep(15, 100, 100, 1000, 500, 0.4, 0.2, 20)

    start_time = time.perf_counter()
    for _ in range(100):
        model.step()

    print(time.perf_counter() - start_time)
