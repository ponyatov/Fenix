## @file
## @brief FVM: Fenix Virtual Machine /Python implementation/
## @author (c) Dmitry Ponyatov <<dponyatov@gmail.com>>, 2018, All rights reserved

## @defgroup sym SYM: Symbolic object system
## @{

## base <b>sym</b>bolic class
class Sym:

    ## construct symbol in `<T:V>` form
    ## @param[in] V value
    def __init__(self, V):
        ## type/class <b>tag</b>
        self.tag = self.__class__.__name__.lower()
        ## single <b>val</b>ue
        self.val = V

    def __repr__(self): return self.dump()

    def dump(self): return self.head()

    def head(self, prefix=''): return '%s<%s:%s>' % (prefix, self.tag, self.val)


print Sym('symbolic')

## @}

## @defgroup fvm FVM: Fenix Virtual Machine

## @defgroup gui GUI: wxPython

## @defgroup meta META: metaprogramming
## @{

## metaprogramming object
class Meta(Sym): pass

## software module
class Module(Meta): pass

## @}

## @defgroup llvm LLVM: managed compilation
