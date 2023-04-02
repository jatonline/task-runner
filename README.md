# task-runner

A basic task runner implementation in Python.

Tasks are checked in the order they were defined. Usually only the tasks with missing or out of date outputs actually get run, however execution can be forced with the `force` argument.

## Usage

Create a Python script `my_file.py`:

```python
from tasks import task, run_tasks

@task(inputs=['input.txt'], outputs=['output.txt'])
def my_task():
    ...

if __name__ == '__main__':
    run_tasks()
```

Then run from the command line:

```
$ python my_file.py
Running task my_task (out of date outputs: output.txt)...
```

The task will only run once:

```
$ python my_file.py
Skipped task my_task
```

If you update the inputs or source code, or remove the outputs then the task will run again.

You can also force it to run again:

```
$ python my_file.py --force
Running task my_tast (forced)...
```
