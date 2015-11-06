import functools as fn
import itertools as it

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

def gcd(a, b):
    while b:
        a, b  = b, a % b
    return a

def lcm(a, b):
    return a * b // gcd(a, b)

def gcd_i(nums):
    return fn.reduce(gcd, nums, 0)

def lcm_i(nums):
    return fn.reduce(lcm, nums, 1)


