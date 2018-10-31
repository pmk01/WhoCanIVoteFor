from contextlib import contextmanager
import json


@contextmanager
def show_data_on_error(variable_name, data):
    """A context manager to output problematic data on any exception

    If there's an error when importing a particular person, say, it's
    useful to have in the error output that particular structure that
    caused problems. If you wrap the code that processes some data
    structure (a dictionary called 'my_data', say) with this:

        with show_data_on_error('my_data', my_data'):
            ...
            process(my_data)
            ...

    ... then if any exception is thrown in the 'with' block you'll see
    the data that was being processed when it was thrown."""

    try:
        yield
    except:
        message = "An exception was thrown while processing {0}:"
        print(message.format(variable_name))
        print(json.dumps(data, indent=4, sort_keys=True))
        raise
