# A Puzzle A Day

A solver for [A-Puzzle-A-Day](https://www.dragonfjord.com/product/a-puzzle-a-day/) implementing a simple SAT-based technique using [z3](https://z3prover.github.io/) and a depth-first search solver.

Example:
```
python puzzle.py -d 1 -m 1
```
Use `-n` for the number of solutions to print and `-s` to specify the solver (`z3` or `dfs`). See `-h` for all options.

If you have the `termcolor` package installed, you get coloured output.