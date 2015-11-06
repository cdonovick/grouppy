import itertools as it
import functools as fn
from util import lcm_i
from util import classproperty

class permutation: 
    def __init__(self, *d):
        if d is None or len(d) == 0:
            self.__map = dict()
            self.__cycles = ()
            self.__support = frozenset()
            self.__even = True
        elif len(d) == 1:
            d=d[0]
            if len(d) != len(set(d)):
                raise Exception('Bad cycle, has repeated value')
            self.__map = {k: d[(idx+1)%len(d)] for idx,k in enumerate(d)}
            self.__support = frozenset(d)
            self.__cycles = (d,)
            self.__even = len(d) - 1 % 2 == 0

        else:
            ps = (permutation(i) for i in d)
            p = permutation.compose(*ps)
            self.__map = p.__map
            self.__support = p.__support
            self.__cycles = p.__cycles
            self.__even = p.__even

    @classmethod
    def from_dict(cls, d):
        if len(d.values()) != len(set(d.values())):
            raise Exception('Bad mapping, is not injective')
        cycle_lst = []
        closed = set()
        for k,v in d.items():
            if k != v and k not in closed:
                c = []
                while k not in closed:
                    c.append(k)
                    closed.add(k)
                    k = d[k]
                cycle_lst.append(tuple(c))
        p = permutation()
        p.__map = d
        p.__support = frozenset(closed)
        p.__cycles = tuple(cycle_lst)
        p.__even = sum(len(i) - 1 for i in cycle_lst ) % 2 == 0
        return p

    __identity = None
    @classproperty
    def identity(cls):
        if cls.__identity is None:
            cls.__identity = cls()
        return cls.__identity
    
    @classmethod
    def compose(cls, *ps):
        if ps is None or len(ps) == 0:
            return cls.identity

        lst = list(ps)
        rlst = list(reversed(lst))
        support = fn.reduce(lambda s, p: s | p.support, lst, frozenset())
        d = {i: fn.reduce(lambda v, f: f(v), rlst, i) for i in support} 
        return permutation.from_dict(d)
    
    @property
    def cycles(self):
        return self.__cycles

    @property
    def factor(self):
        return tuple(t for t in it.chain.from_iterable(zip(i, i[1:]) for i in self.cycles))

    @property
    def support(self):
        return self.__support

    @property
    def inverse(self):    
        return permutation.from_dict({self(k): k for k in self.support})

    @property
    def order(self):
        return lcm_i(len(i) for i in self.cycles)
    
    @property
    def even(self):
        return self.__even

    def __call__(self, idx):
        if idx in self.support:
            return self.__map[idx]
        else:
            return idx

    def __mul__(self, other):
        return permutation.compose(self, other)

    def __repr__(self):
        if self == permutation.identity:
            return u'\u03B5'
        return '(' + ') ('.join(' '.join(str(e) for e in i) for i in self.cycles) + ')'

    @property
    def table_str(self):
        s = ' '.join(str(i) for i in self.support)
        d = ' '.join(str(self(i)) for i in self.support)
        return '|' + s + '|\n' + '|' + d + '|\n'

    
    def __eq__(self, other):
        if self.support != other.support:
            return False
        for i in self.support:
            if self(i) != other(i):
                return False
        return True
    
    def __hash__(self):
        h =  hash(frozenset(self.cycles))
        return h

    def __pow__(self, n):
        if n == 0:
            return permutation.identity
        elif n > 0:
            return permutation.compose(*(self for _ in range(n)))
        else:
            return self.__pow__(-n).inverse 
