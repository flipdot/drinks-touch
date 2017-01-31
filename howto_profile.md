
    pip2 install line_profiler

then add @profile to the methods you are interested in.

run with:

    kernprof -l game.py

analyze results:

    python2 -m line_profiler game.py.lprof | less
