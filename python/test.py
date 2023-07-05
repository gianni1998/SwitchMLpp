

def record_time(func):

    def wrapper():

        func()

    return wrapper


@record_time
def test():
    pass