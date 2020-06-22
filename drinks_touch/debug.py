import signal
import sys

import traceback


def debug(sig, frame):
    code = ""
    for threadId, stack in sys._current_frames().items():
        code += "\n# ThreadID: %s" % threadId
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code += '\nFile: "%s", line %d, in %s' % (filename,
                                                      lineno, name)
            if line:
                code += "  %s" % (line.strip())
    print >> sys.stderr, code


def listen():
    signal.signal(signal.SIGUSR1, debug)  # Register handler
