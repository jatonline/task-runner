from functools import wraps
import inspect
from os.path import exists, getmtime
import sys


# This dictionary holds all defined the tasks
tasks = {}


def task(inputs=None, outputs=None):
    """
    Define a task that (if necessary) will be executed when `run_tasks()` is called.

    Args:
        inputs: optional list of files (strings or Path objects)
            The task only needs to run if all the specified input files exist.
        outputs: optional list of files (strings or Path objects)
            The task only needs to run if an output file is missing, or if any of
            the input files are newer than any of the output files.

    Usage:
        ```
        @task(inputs=['input.txt'], outputs=['output.txt'])
        def my_task():
            ...
        ```
    """
    def decorator(func):
        tasks[func.__name__] = {
            'callable': func,
            'inputs': inputs or [],
            'outputs': outputs or [],
        }
        return func
    return decorator


def run_tasks(force=False):
    """
    Execute any tasks that need to be run.

    Tasks are checked in the order they were defined. Usually only the tasks with missing
    or out of date outputs actually get run, however execution can be forced with the
    `force` argument.

    Args:
        force: bool (default: False)
            Force every task to run. Can also be specified by using `--force` at the
            command line.

    Usage:
        ```
        @task(inputs=['input.txt'], outputs=['output.txt'])
        def my_task():
            ...

        if __name__ == '__main__':
            run_tasks()
        ```
    """
    force = force or '--force' in sys.argv

    for task_name, task in tasks.items():
        if missing := _missing_paths(task['inputs']):
            raise FileNotFoundError(
                f'Cannot run task {task_name} because the '
                f'following inputs are missing: {", ".join(missing)}'
            )

        # We need to run the task, if...
        if (
            # we are being forced to run:
            force
            # some outputs are missing:
            or (missing := _missing_paths(task['outputs']))
            # some outputs are out of date:
            or (outdated := _out_of_date_outputs(task))
            # the task has no outputs
            or not outputs
        ):
            if force:
                print(f'Running task {task_name} (forced)...')
            elif missing:
                missing = ', '.join(str(f) for f in missing)
                print(f'Running task {task_name} (missing outputs: {missing})...')
            elif outdated:
                outdated = ', '.join(str(f) for f in outdated)
                print(f'Running task {task_name} (out of date outputs: {outdated})...')
            task['callable']()
        else:
            print(f'Skipped task {task_name}')


def _missing_paths(paths):
    return [path for path in paths if not exists(path)]


def _out_of_date_outputs(task):
    newest_input = max((getmtime(path) for path in task['inputs']), default=0)
    source_modified = getmtime(source_filename) if exists(source_filename := inspect.getfile(task['callable'])) else 0
    modification_threshold = max(newest_input, source_modified)
    return [output for output in task['outputs'] if getmtime(output) < modification_threshold]
