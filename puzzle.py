import argparse
import sys

from itertools import product

pieces = [
    [ 'F..', 'F..', 'FFF' ],
    [ 'TTTT', '.T..' ],
    [ 'SS..', '.SSS' ],
    [ 'QQQ', 'QQQ' ],
    [ 'Z..', 'ZZZ', '..Z' ],
    [ 'L...', 'LLLL' ],
    [ 'U.U', 'UUU' ],
    [ 'BB.', 'BBB' ]
]

def piece_id(piece):
    return next(c for l in piece for c in l if c != '.')

def piece_positions(piece):
    def flip(piece):
        return [row[::-1] for row in piece]
    def transpose(piece):
        return [''.join(row) for row in zip(*piece)]
    def rotate(piece):
        return transpose(flip(piece))
    for p in [piece, flip(piece)]:
        for _ in range(4):
            yield tuple(p)
            p = rotate(p)

positions = [ set(x for x in piece_positions(p)) for p in pieces ]

colors = [
    'red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'white', 'dark_grey'
]
assert len(pieces) <= len(colors)
color_map = { piece_id(p): c for p, c in zip(pieces, colors) }

board = [
    '......#',
    '......#',
    '.......',
    '.......',
    '.......',
    '.......',
    '...####',
]
board = [ list(r) for r in board ]

def iter_r(board):
    return range(len(board))

def iter_c(board):
    return range(len(board[0]))

blk_str = lambda p: p + p
if sys.stdout.isatty():
    try:
        import termcolor
        blk_str = lambda p: termcolor.colored('██', color_map[p])
    except ImportError:
        pass

def print_board(board):
    def cell_str(c):
        match c:
            case 'M': return f'{month + 1:02}'
            case 'D': return f'{day + 1:02}'
            case '#' | '.' : return '  '
            case _: return blk_str(c) if c in color_map else c + c
    for row in board:
        print(''.join(cell_str(p) for p in row))

def fit(board, piece, r, c):
    W = len(board[0])
    H = len(board)
    occ = []
    for dr in iter_r(piece):
        rr = r + dr
        for dc in iter_c(piece):
            cc = c + dc
            if not (0 <= rr < H and 0 <= cc < W):
                return []
            if piece[dr][dc] != '.':
                if board[rr][cc] != '.':
                    return []
                else:
                    occ += [ (rr, cc) ]
    return occ

try:
    from z3 import *
    set_param("parallel.enable", True)

    def solver_z3(b):
        def var(r, c):
            return Const(f'occ_{r}_{c}', sort)
        def clause(piece, k, r, c):
            r = [ var(r, c) == k for r, c in fit(b, piece, r, c) ]
            return And(r) if r else BoolVal(False)

        sort, kinds = EnumSort('Occ', [ piece_id(p) for p in pieces ])
        s = SolverFor('QF_FD')
        for pos, kind in zip(positions, kinds):
            s.add(Or([ clause(p, kind, r, c) \
                        for r in iter_r(b) \
                        for c in iter_c(b) \
                        for p in pos]))
        assert s.check() == sat
        m = s.model()
        def get(r, c):
            v = m[var(r, c)]
            return str(v) if not v is None else b[r][c]
        yield [ ''.join(str(get(r, c)) for c in iter_c(b)) for r in iter_r(b) ]
except ImportError:
    pass

def solver_dfs(b):
    def dfs(b, i):
        if i == len(pieces):
            yield b
            return
        for r, c in product(iter_r(b), iter_c(b)):
            for p in positions[i]:
                occ = fit(b, p, r, c)
                if not occ:
                    continue
                for rr, cc in occ:
                    b[rr][cc] = piece_id(p)
                yield from dfs(b, i + 1)
                for rr, cc in occ:
                    b[rr][cc] = '.'
    yield from dfs(b, 0)

prefix = 'solver_'
solvers = [ n[len(prefix):] for n in dict(globals()) if n.startswith(prefix) ]

parser = argparse.ArgumentParser(
                    prog='a_puzzle_a_day',
                    description='Solve a puzzle a day')

parser.add_argument('-d', '--day', type=int, action='store', help='day (1-31)')
parser.add_argument('-m', '--month', type=int, action='store', help='month (1-12)')
parser.add_argument('-n', '--solutions', type=int, action='store', default=1, help='number of solutions')
parser.add_argument('-s', '--solver', help='specify solver (default: dfs)')
parser.add_argument('-l', '--list', action='store_true', help='list solvers')

args = parser.parse_args()

if args.list:
    for s in solvers:
        print(s)
    exit()

solver = globals()[prefix + args.solver] if args.solver else solver_dfs

if not args.day or not args.month:
    print('you must specify day and month: -d <day> -m <month>')
    exit(1)

day   = args.day - 1
month = args.month - 1
assert 0 <= day < 31
assert 0 <= month < 12
board[month // 6][month % 6] = 'M'
board[2 + day // 7][day % 7] = 'D'

for _, sol in zip(range(args.solutions), solver(board)):
    print_board(sol)