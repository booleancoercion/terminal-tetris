colors = [' ', 'cyan', 'yellow', 'magenta', 'green', 'red', 'blue', 'grey']
CLOCKWISE = 1
COUNTERCLOCKWISE = -1

def runtest(grid, px, test):
    """Tests if applying test to px moves px to unoccupied space"""
    for p in px:
        if(p[0]+test[0] >= grid.n or p[0]+test[0] < 0):
            return False
        if(p[1]-test[1] >= grid.m or p[1]-test[1] < 0):
            return False
        if(isoccupied([p[0]+test[0], p[1]-test[1]], grid)):
            return False
    return True

def isoccupied(pixel, grid):
    p = grid(pixel[1], pixel[0])
    if(p > 0 and p < 8):
        return True
    return False

class OccupiedError(Exception):
    pass

class RotationError(Exception):
    pass

class TetrisBlock:
    """Base for block classes. THIS CLASS SHOULD NOT BE INSTANTIATED."""

    rotdict = {0:[]}

    testdict = {0:[]}

    col = 0

    def __init__(self, grid):
        """Initiates the block on the given grid.\
         Defines _grid, _center, _pixels, _col and _rot"""
        self._grid = grid
        self._center = [0,0]
        self._pixels = []
        self._rot = 0
    
    def move(self, x, y):
        """Moves the block x times right and y times down.\
         Raises OccupiedError if desired pixels are occupied."""

        for p in self._pixels:
            if(p[1]+y >= self._grid.m or p[0]+x >= self._grid.n):
                raise IndexError("Cannot move block outside of grid.")
            if(p[1]+y < 0 or p[0]+x < 0):
                raise IndexError("Cannot move block outside of grid.")

        self.remself()

        for p in self._pixels:
            if(isoccupied([p[0]+x, p[1]+y], self._grid)):
                self.updategrid()
                raise OccupiedError("Can't move block to ["+str(p[0]+x)+","+str(p[1]+y)+"].")

        self._center[0] += x
        self._center[1] += y

        for p in self._pixels:
            p[0] += x
            p[1] += y
        
        self.updategrid()
    
    def rot(self, direction=CLOCKWISE):
        """Rotates the block clockwise.\
         COUNTERCLOCKWISE (-1) should rotate counterclockwise.
        
        Default:
        *  direction=CLOCKWISE"""

        prev = self._rot
        self._rot = (self._rot + direction)%4
        tests = self.testdict[(prev, self._rot)]

        self.remself()

        x, y = self._center
        pixels = [[int(p[0]+x), int(p[1]+y)] for p in self.rotdict[self._rot]]

        for t in tests:
            if(runtest(self._grid, pixels, t)):
                self._center[0] += t[0]
                self._center[1] -= t[1]
                for p in pixels:
                    p[0] += t[0]
                    p[1] -= t[1]
                break
        else:
            self._rot = prev
            self.updategrid()
            raise RotationError("Cannot rotate block.")

        self._pixels = pixels
        self.updategrid()
    
    def updategrid(self):
        """Updates the grid with the current _pixels list."""
        for p in self._pixels:
            self._grid[p[1]][p[0]] = self.col
    
    def remself(self):
        """Removes the current pixels from the grid. To be used with self.updategrid() to\
         properly modify the grid without leaving remnants."""
        for p in self._pixels:
            self._grid[p[1]][p[0]] = 0

class IBlock(TetrisBlock):
    rotdict = {0:[[-1.5, -0.5], [-0.5, -0.5], [0.5, -0.5], [1.5, -0.5]],
               1:[[0.5, -1.5], [0.5, -0.5], [0.5, 0.5], [0.5, 1.5]],
               2:[[-1.5, 0.5], [-0.5, 0.5], [0.5, 0.5], [1.5, 0.5]],
               3:[[-0.5, -1.5], [-0.5, -0.5], [-0.5, 0.5], [-0.5, 1.5]]}
    
    testdict = {(0, 1):[[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
                (1, 0):[[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
                (1, 2):[[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]],
                (2, 1):[[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
                (2, 3):[[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
                (3, 2):[[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
                (3, 0):[[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
                (0, 3):[[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]]}
    
    col = 1

    def __init__(self, grid):
        self._grid = grid
        self._center = [4.5, 1.5]
        self._pixels = [[3, 1], [4, 1], [5, 1], [6, 1]]
        self._rot = 0
        
class OBlock(TetrisBlock):
    col = 2

    def __init__(self, grid):
        self._grid = grid
        self._center = [4, 1]
        self._pixels = [[4, 0], [5, 0], [4, 1], [5, 1]]

    def rot(self):
        pass

globaltestdict = {(0, 1):[[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
             (1, 0):[[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
             (1, 2):[[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
             (2, 1):[[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
             (2, 3):[[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
             (3, 2):[[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
             (3, 0):[[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
             (0, 3):[[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]]}

class TBlock(TetrisBlock):
    rotdict = {0:[[0, -1], [-1, 0], [0, 0], [1, 0]],
               1:[[0, -1], [0, 0], [1, 0], [0, 1]],
               2:[[-1, 0], [0, 0], [1, 0], [0, 1]],
               3:[[0, -1], [-1, 0], [0, 0], [0, 1]]}
    
    testdict = globaltestdict
    
    col = 3

    def __init__(self, grid):
        self._grid = grid
        self._center = [4, 1]
        self._pixels = [[4, 0], [3, 1], [4, 1], [5, 1]]
        self._rot = 0

class SBlock(TetrisBlock):
    rotdict = {0:[[0, -1], [1, -1], [-1, 0], [0, 0]],
               1:[[0, -1], [0, 0], [1, 0], [1, 1]],
               2:[[0, 0], [1, 0], [-1, 1], [0, 1]],
               3:[[-1, -1], [-1, 0], [0, 0], [0, 1]]}

    testdict = globaltestdict

    col = 4

    def __init__(self, grid):
        self._grid = grid
        self._center = [4, 1]
        self._pixels = [[4, 0], [5, 0], [3, 1], [4, 1]]
        self._rot = 0

class ZBlock(TetrisBlock):
    rotdict = {0:[[-1, -1], [0, -1], [0, 0], [1, 0]],
               1:[[1, -1], [0, 0], [1, 0], [0, 1]],
               2:[[-1, 0], [0, 0], [0, 1], [1, 1]],
               3:[[0, -1], [-1, 0], [0, 0], [-1, 1]]}

    testdict = globaltestdict

    col = 5

    def __init__(self, grid):
        self._grid = grid
        self._center = [4, 1]
        self._pixels = [[3, 0], [4, 0], [4, 1], [5, 1]]
        self._rot = 0

class JBlock(TetrisBlock):
    rotdict = {0:[[-1, -1], [-1, 0], [0, 0], [1, 0]],
               1:[[0, -1], [1, -1], [0, 0], [0, 1]],
               2:[[-1, 0], [0, 0], [1, 0], [1, 1]],
               3:[[0, -1], [0, 0], [-1, 1], [0, 1]]}

    testdict = globaltestdict

    col = 6
    
    def __init__(self, grid):
        self._grid = grid
        self._center = [4, 1]
        self._pixels = [[3, 0], [3, 1], [4, 1], [5, 1]]
        self._rot = 0

class LBlock(TetrisBlock):
    rotdict = {0:[[1, -1], [-1, 0], [0, 0], [1, 0]],
               1:[[0, -1], [0, 0], [0, 1], [1, 1]],
               2:[[-1, 0], [0, 0], [1, 0], [-1, 1]],
               3:[[-1, -1], [0, -1], [0, 0], [0, 1]]}

    testdict = globaltestdict

    col = 7

    def __init__(self, grid):
        self._grid = grid
        self._center = [4, 1]
        self._pixels = [[5, 0], [3, 1], [4, 1], [5, 1]]
        self._rot = 0

def isin(pixel, pixels):
    for p in pixels:
        if(p[0] == pixel[0] and p[1] == pixel[1]):
            return True
    return False

class Ghost:
    def __init__(self, block):
        self._block = block
        self._grid = block._grid
        self._pixels = None
        self.update()
    
    def update(self):
        if(self._pixels != None):
            self.remself()
        self._pixels = [p[:] for p in self._block._pixels]

        ok = True
        while True:
            for p in self._pixels:
                if(p[1]+1 >= self._grid.m):
                    ok = False
                    break
                occ = isoccupied([p[0], p[1]+1], self._grid)
                if(occ and not isin([p[0], p[1]+1], self._block._pixels)):
                    ok = False
                    break
            if(ok == False): break
            
            for p in self._pixels:
                p[1] += 1
        
        for p in self._pixels:
            if(isin(p, self._block._pixels)): continue
            self._grid[p[1]][p[0]] = 8

    def remself(self):
        for p in self._pixels:
            if(isin(p, self._block._pixels)): continue
            self._grid[p[1]][p[0]] = 0