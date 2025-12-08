import mlrun


def func(context):
    for i in range(20):
        context.logger.info(str(i) * 100)

    return 1