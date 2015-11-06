import itertools as it
import functools as fn
import operator
import util
class algebra_iter:
    def __init__(self, gp):
        self.__iter = iter(gp)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.__iter)

class Magma:
    def __init__(self, gp, op=operator.mul):
        self._gp = frozenset(gp)
        self._op = op
        self._attest_cbs = {0:[],1:[],2:[]}

    @property
    def gp(self):
        return self._gp
    
    @property
    def op(self):
        return self._op

    def __contains__(self, elem):
        return elem in self._gp

    def __iter__(self):
        return algebra_iter(self.gp)
    
    def __hash__(self):
        return hash(self._gp)

    def attest(self):
        cbs = self._attest_cbs

        for cb in cbs[0]:
            cb()
        for i in self:
            for cb in cbs[1]:
                cb(i)

            for j in self:
                ij = self.op(i, j)
                if ij not in self:
                    raise Exception('Fails closure of the operation, {i}{j} == {ij} not in set'.format(i=i, j=j, ij=ij))

                for cb in cbs[2]:
                    cb(i, j)

    def attest_abelian(self):
        op = self.op
        for i in self:
            for j in self:
                ij = op(i, j)
                ji = op(j, i)
                if ij != ji:
                    raise Exception('Not abelian, {i}{j} == {ij} != {ji} == {j}{i}'.format(i=i, j=j, ij=ij, ji=ji))

class Semigroup(Magma):
    def __init__(self, gp, op=operator.mul):
        super().__init__(gp, op)
        self._attest_cbs[3] = []
        def __cb2(i, j):
            for k in self:
                a = op(op(i,j), k)
                b = op(i, op(j, k))
                if a != b:
                    raise Exception('Not asssociative, ({i}{j}){k} == {a} != {b} == {i}({j}{k})'.format(i=i,j=j,k=k,a=a,b=b))
                for cb in self._attest_cbs[3]:
                    cb(self, i, j, k)

        self._attest_cbs[2].append(__cb2)

class Monoid(Semigroup):
    def __init__(self, gp, op=operator.mul, identity=None):
        super().__init__(gp, op)

        if identity is None:
            for i in self:
                if all(op(j, i) == op(i, j) == j for j in self):
                    identity = i
                    break
            self._identity = identity

            def __cb_ident():
                if self.identity not in self:
                    raise Exception('idenity element not in set')
            self._attest_cbs[0].append(__cb_ident)

        else:
            self._identity = identity
            def __cb_ident(i):
                iid = op(i, self.identity)
                if iid != i:
                    raise Exception('Bad identity, {0}{1} == {2} != {0}'.format(i, self.identity, iid))
                idi = op(self.identity, i)
                if idi != i:
                    raise Exception('Bad identity, {1}{0} == {2} != {0}'.format(i, self.identity, idi))
            self._attest_cbs[1].append(__cb_ident)

    @property
    def identity(self):
        return self._identity

    @property
    def units(self):
        pass

class Group(Monoid):
    '''class for finite groups'''
    def __init__(self, gp=None, op=operator.mul, identity=None, inverse=None, generators=(), lazy=False):

        if generators and not lazy:
            gp, identity = self.__generate(generators, op, inverse)
        elif generators:
            raise Exception('Not implemented')

        super().__init__(gp, op, identity)

        if inverse is None:
            def __cb_inverse(i):
                if not any(op(i,j) == self.identity for j in self):
                    raise Exception('Fails closure of inverse, {} has no inverse in grp'.format(i))
        else:
            self._inverse = inverse
            def __cb_inverse(i):
                if self.inverse(i) not in self:
                    raise Exception('Fails closure of inverse, inverse {} == {} not in grp'.format(i, ii))

        self._attest_cbs[1].append(__cb_inverse)

    @staticmethod
    def __generate(generators, op, inverse):   

        stack = [i for i in generators]
        identity = op(stack[0], inverse(stack[0]))
        seen = set(stack)
        seen.add(identity)
        gp = set(stack)

        def do_update(x):
            if x not in seen:
                stack.append(x)
                seen.add(x)

        while stack:
            elem = stack.pop()
            for i in gp:
                do_update(op(i, elem))
                do_update(op(elem, i))
            do_update(inverse(elem))
            gp.add(elem)

        gp.add(identity)
        return frozenset(gp), identity
 
    @property
    def inverse(self):
        if self._inverse is None:
            @fn.lru_cache(maxsize=None)
            def __i(x):
                for i in self:
                    if self.op(i, x) == self.identity:
                        return i
            self._inverse = __i
        return self._inverse

    def __le__(self, other):
        try:
            Group.attest(other)
        except:
            return False
        return self.gp <= other.gp

    def R_cosets(self, other):
        if not (other <= self):
            raise Exception('{} is not a subgroup of {}'.format(other, self))
        return {frozenset(self.op(g, h) for h in other) for g in self}

    def L_cosets(self, other):
        if not (other <= self):
            raise Exception('{} is not a subgroup of {}'.format(other, self))
        return {frozenset(self.op(h, g) for h in other) for g in self}

    def attest_normal(self, other):
        if self.R_cosets(other) != self.L_cosets(other):
            raise Exception('{} is not a  normal subroug {}'.format(other, self))
