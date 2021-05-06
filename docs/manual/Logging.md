# Logging

At the default state, the program will emit important messages about
assumptions it made in creating or modifying the grid in memory.

This library, and many other python libraries, heavily leverage the
built-in [logging](https://docs.python.org/3/library/logging.html)
library.

The logging mechanism in this application and GridUtils() is slightly complex.  For messages
emitted to the "Information" panel or using iterative means, you can control the amount of
detail presented to you or logged in a file.  The logging levels from low to high are: NOTSET,
DEBUG, INFO, WARNING, ERROR and CRITICAL.  The level set means only messages of that level or higher
will be shown or logged.  If you want to see all available detail, use NOTSET.  NOTE: The detail sent
to the applications "Information" window by default is INFO or higher.  The detail sent to a log file,
if enabled, is WARNING or higher.  The function for emitting messages is `GridUtils.printMsg()`.

# Log file

You can only change the log file name or delete the log file when the logging system is disabled.
To assist the software developers, we request that you provide a log file of activity to help us
discover problems with the code.  The log file will continue to grow over time.  It is a good idea
to periodically erase the log file.

# Debug level

This is a special feature mainly for developers.  If you are planning to "hack" this code, you can
utilize this feature to assist with debugging existing or new code.  The available debug levels
do not operate like the logging levels.  For operational use, the debug level is usually OFF.  You
can use the MESSAGE level to simply emit messsages for debugging.  The debug level RAISE, can emit a
message and then raise a python exception.  This can normally be done in a try/except block where you
can try a bit of code and in the except block raise the exception after emitting a debugging message.
The last level is BREAKPOINT.  This is similar to RAISE except that after the message is emitted, the
program will attempt to start the python debugger (pdb) using `pdb.set_trace()`.  All messages sent
via `GridUtils.debugMsg()` are shown at the DEBUG level.

Please review the [mkGridsExample2.py](../gridTools/mkGridsExample2.py)
python script for an example on how to work with the
messaging and logging portion of the library.

If you discover a bug or problem with the, we will want to be provided as much
information as possible to help us fix the issue.  Please see the
[reporting](Reporting.md) section of the user manual to assist developers.
