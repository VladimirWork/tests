import cProfile


def profile(func):
    def wrapper(*args, **kwargs):
        # profile_filename = func.__name__ + '.profile'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        # profiler.dump_stats(profile_filename)
        profiler.print_stats()
        return result
    return wrapper
