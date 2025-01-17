import os
import shlex
from subprocess import check_call
from celery import Celery

app = Celery('worker', backend='amqp', broker='amqp://')
app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json'
)


@app.task(name='worker.process_part')
def process_part(is_video, input_path, output_format, start_at, stop_at):
    input_part_path = extract_part(is_video, input_path, start_at, stop_at)
    output_part_path = convert_part(input_part_path, output_format)

    return output_part_path


def extract_part(is_video, input_path, start_at, stop_at):
    # Input part path
    base_name = os.path.basename(input_path)
    input_name = os.path.splitext(base_name)[0]
    input_format = os.path.splitext(base_name)[1]

    input_part_path = "/data/tmp/{}-{}{}".format(input_name, start_at, input_format)

    # Command
    template = "ffmpeg -y -i {} -ss {} -t {} {}"
    t = '%.2f' % round(stop_at - start_at, 2)
    command = template.format(input_path, start_at, t, input_part_path)
    check_call(shlex.split(command), universal_newlines=True)

    return input_part_path


def convert_part(input_part_path, output_format):
    # Output part path
    base_name = os.path.basename(input_part_path)
    input_name = os.path.splitext(base_name)[0]

    output_part_path = "/data/tmp/{}.{}".format(input_name, output_format)

    # Command
    template = "ffmpeg -y -i {} -qscale 0 -strict -2 {}"
    command = template.format(input_part_path, output_part_path)
    check_call(shlex.split(command), universal_newlines=True)

    # Remove input part
    os.remove(input_part_path)

    return output_part_path
