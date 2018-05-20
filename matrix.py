# matrix module
from numbers import Number

class InputError(Exception):
    pass

class SizeError(Exception):
    pass

class Row(list):
    def __init__(self, row):
        if(type(row) != list):
            raise TypeError("Input must be a list.")
        for e in row:
            if(not isinstance(e, Number)):
                raise TypeError("Row elements must be numbers.")
        self._row = row
    
    def __getitem__(self, i):
        if(type(i) == int):
            if(i < 0 or i > len(self)-1):
                raise IndexError("Index out of bounds.")
        else:
            if(i.start < 0 or i.stop > len(self)):
                raise IndexError("Index out of bounds.")
        return self._row[i]
    
    def __setitem__(self, i, v):
        if(type(i) == int):
            if(i < 0 or i > len(self)-1):
                raise IndexError("Index out of bounds.")
        else:
            if(i.start < 0 or i.stop > len(self)):
                raise IndexError("Index out of bounds.")

        if(type(v) == int):
            if(not isinstance(v, Number)):
                    raise TypeError("Row elements must be numbers.")
        else:
            for e in v:
                if(not isinstance(e, Number)):
                    raise TypeError("Row elements must be numbers.")
        self._row[i] = v
    
    def __len__(self):
        return len(self._row)
    
    def __str__(self):
        return str(self._row)
    
    def __repr__(self):
        return repr(self._row)
    
    def __iter__(self):
        return iter(self._row)


class Matrix:
    def __init__(self, rows):
        self.m = len(rows)
        self.n = len(rows[0])
        temp = []
        for r in rows:
            if(len(r) != self.n):
                raise InputError("Matrix rows don't have the same length.")
            temp.append(Row(r[:]))
        self.rows = temp
    
    def __call__(self, k, l):
        """For convenicence: returns the kl-th element of the matrix.
        This is equivelant to matrix.rows[k][l]."""
        return self.rows[k][l]
    
    def __getitem__(self, k):
        return self.rows[k]

    def __add__(self, other):
        """Adds two matrices together."""
        if(not isinstance(other, Matrix)):
            raise TypeError("Cannot add Matrix and " + type(other))
        if(self.m != other.m or self.n != other.n):
            raise SizeError("Cannot add matrices of different sizes")

        return Matrix([[self(i,j)+other(i,j) for j, _ in enumerate(r)]
            for i, r in enumerate(self.rows)])

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if(isinstance(other, Number)): # matrix * number
            if(other == 1): return self
            return Matrix([[other*self(i,j) for j, _ in enumerate(r)]
                for i, r in enumerate(self.rows)])
        
        elif(isinstance(other, Matrix)): # matrix * matrix
            if(self.n != other.m):
                raise SizeError("Invalid matrix sizes for multiplication")
            A = self.rows
            B = other.rows
            ret = [[] for a in enumerate(A)]
            for i, _ in enumerate(A):
                for j, _ in enumerate(B[0]):
                    c = 0
                    for k, _ in enumerate(A[0]):
                        c += A[i][k]*B[k][j]
                    ret[i].append(c)
            return Matrix(ret)
        else:
            raise TypeError("Cannot multiply Matrix and " + type(other))

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return -1*self
    
    def __sub__(self, other):
        return self + (-other)

    def __abs__(self):
        return self.det()

    def __pow__(self, other):
        if(self.m != self.n):
            raise SizeError("Cannot exponentiate a non-square matrix.")
        if(not isinstance(other, int)):
            raise TypeError("Cannot exponentiate matrix by a non-integer.")
        if(other == 0):
            return IdentityMatrix(self.m)
        elif(other == -1):
            d = abs(self)
            if(d == 0):
                raise Exception("Matrix doesn't have an inverse.")
            return (1/d) * Matrix([[((-1)**(i+j))*self.minor(i, j).det() for j, _ in enumerate(r)]
            for i, r in enumerate(self.rows)]).transpose()
        else:
            ret = IdentityMatrix(self.n)
            for _ in range(other):
                ret *= self
            return ret
    
    def __str__(self):
        longest = []
        hasneg = []
        for c in self.transpose().rows:
            lo = 1
            neg = False
            for e in c:
                lo = max(len(str(round(e,2))), lo)
                if(e < 0):
                    neg = True
            longest.append(lo)
            hasneg.append(neg)
        out = "┌" + " "*(self.n+1+sum(longest)) + "┐\n"
        for r in self.rows:
            out += "│ "
            for c, e in enumerate(r):
                if(hasneg[c] and e >= 0):
                    out += " "
                out += (str(round(e, 2))+" "*longest[c])[:longest[c]+1-(hasneg[c] and e >= 0)]
            out += "│\n"
        out += "└" + " "*(self.n+1+sum(longest)) + "┘"
        return out
    
    def __repr__(self):
        return "Matrix("+str(self.m)+"x"+str(self.n)+")"

    def minor(self, k, l):
        M = self.rows
        ret = [[] for a in range(len(M)-1)]
        
        i_ = 0
        for i, _ in enumerate(M):
            if(i == k): continue
            for j, e in enumerate(M[i]):
                if(j == l): continue
                ret[i_].append(e)
            i_ += 1
        return Matrix(ret)

    def det(self):
        if(self.m != self.n):
            raise TypeError("Cannot take determinant of non-square matrix")
        if(self.m == 1): return self(0, 0)
        ret = 0
        for i, _ in enumerate(self.rows):
            ret += ((-1)**i)*self(i, 0)*self.minor(i, 0).det()
        return ret
    
    def transpose(self):
        """Returns the transposed version of the matrix."""
        newm = [[] for a in range(self.n)]
        for r in self.rows:
            for j, v in enumerate(r):
                newm[j].append(v)
        return Matrix(newm)


class IdentityMatrix(Matrix):
    def __init__(self, size):
        if(not isinstance(size, Number)):
            raise TypeError("IdentityMatrix size must be an integer.")
        if(size <= 0):
            raise InputError("IdentityMatrix size must be at least 1.")
        row = [0]*size + [1] + [0]*size
        rows = [[] for _ in range(size)]
        for i, r in enumerate(rows):
            r[:] = row[size-i:len(row)-1-i]
        super().__init__(rows)

def blank(m, n):
    return Matrix([[0 for j in range(n)] for i in range(m)])