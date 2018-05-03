## @file
## @brief FVM: Fenix Virtual Machine /Python implementation/
## @author (c) Dmitry Ponyatov <<dponyatov@gmail.com>>, 2018, All rights reserved

import os,sys

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
        ## `attr{}`ibutes /associative/
        self.attr = {}
        ## `nest[]`ed elements /ordered/
        self.nest = []
    
    ## print object
    def __repr__(self): return self.dump()

    ## dump object in tree-like form
    ## @returns string tree dump
    ## @param[in] depth padding for recursive tree walk    
    def dump(self,depth=0):
        S = '\n'+self.pad(depth)+self.head()
        for i in self.attr:
            S += '\n'+self.pad(depth+1)+self.attr[i].head('%s = '%i)
        for j in self.nest:
            S += j.dump(depth+1)
        return S
    
    ## left pad every tree dump element
    def pad(self,N): return '\t'*N

    ## print object in short form
    ## @returns `<T:V>` string
    def head(self, prefix=''): return '%s<%s:%s>' % (prefix, self.tag, self.val)
    
    ## push to `nest[]` stack-like
    ## @param[in] o object to be pushed
    def push(self,o): self.nest.append(o) ; return self
    ## pop from `nest[]` stack-like
    ## @return top nest element
    def pop(self): return self.nest.pop()
    ## get top element without popping it from the stack
    def top(self): return self.nest[-1]
    
    ## lookup object in `attr{}`ibutes
    ## @param[in] K index key
    ## @returns `self.attr[K]`
    def __getitem__(self,K): return self.attr[K]
    ## assign `attr{}`ibute
    ## @param[in] K index key
    ## @param[in] o object to be stored
    def __setitem__(self,K,o): self.attr[K] = o ; return self

## data container
class Container(Sym): pass

## LIFO stack
class Stack(Container): pass

## Vocabulary /associative array, unordered/
class Voc(Container):
    ## `<<` operator: `vocabulary << method`
    def __lshift__(self,F):
        FN = F.__name__
        self.attr[FN] = Method(FN,F)

## @}

## @defgroup syntax PLY-based Syntax parser /lexer only/
## @{

import ply.lex  as lex

## token types
tokens = ['SYM']

## drop spaces
t_ignore = ' \t\r'

## line comment can start with `#` and `\` 
t_ignore_COMMENT = '[\\\#].+'

## count lines
def t_newline(t):
    r'\n'
    t.lexer.lineno += 1

## symbol token
def t_SYM(t):
    r'[^ \t\r\n\#\\]+'
    t.value = Sym(t.value) ; return t

## lexer error callback
def t_error(t): raise SyntaxError(t)

## @}

## @defgroup fvm FVM: Fenix Virtual Machine
## @{

## Fenix Virtual Machine
class FVM(Sym):
    
    ## construct VM
    ## @param[in] V virtual machine name
    ## @param[in] SRC script should be processed /optional/
    def __init__(self,V,SRC=''):
        Sym.__init__(self, V)
        ## fill vocabulary with wrapped FVM methods 
        def defer(method): self.attr[method.__name__] = Method(method)
        defer(self.INTERPRET)
        defer(self.WORD)
        self['USE:'] = Method(self.USE)
#         self.W << self.WORD
#         self.W << self.FIND
#         self.W << self.EXECUTE
        ## start interpreter
        self.INTERPRET(SRC)

    ## interpreter        
    def INTERPRET(self,SRC=''):
        ## feed new lexer with fiven script code
        self.lexer = lex.lex() ; self.lexer.input(SRC)
        # REPL loop
        while True:
            if not self.WORD(): break
            self.FIND() 
            self.EXECUTE()
            
    ## fetch next word from source code stream
    ## @returns flag True on word ready, False on EOF
    def WORD(self):
        token = self.lexer.token()
        if not token: return False
        self.push(token.value) ; return True
    
    ## lookup executable definition in vocabulary
    def FIND(self):
        WN = self.pop()                             # get a name to be searched
        try: EX = self[WN.val]                      # try lookup
        except KeyError: EX = self[WN.val.upper()]  # upcase fallback
        self.push(EX)                               # push executable object
        
    ## execute topmost object it it callable
    def EXECUTE(self): self.pop()()
        
    ## import Python module
    def USE(self):
        self.WORD() ; ModuleName = self.pop().val   # look forward module name
        mod = pyModule(__import__(ModuleName))      # import via function call
        self[mod.val] = mod                         # push in vocabulary

## @}

## @defgroup gui GUI: wxPython

## @defgroup meta META: metaprogramming
## @{

## metaprogramming object
class Meta(Sym): pass

## software module (= PYTHON MODULE)
class Module(Meta): pass

## wrapped Python module
class pyModule(Module):
    ## wrap (imported) module
    ## @param[in] V module
    def __init__(self,V):
        Module.__init__(self, V.__name__)
        ## hold module
        self.mod = V

## object method
class Method(Meta):
    ## wrap Python object method
    ## @param[in] F `class Object: def method(self)`
    ## @param[in] self for method: pointer to FVM as executable context 
    def __init__(self,F):
        Meta.__init__(self, F.__name__)
        ## hidden pointer to executable method (function)
        self.fn = F
    ## define execution semantics (callable obejct)
    def __call__(self): self.fn()

## @}

## @defgroup llvm LLVM: managed compilation

if __name__ == '__main__':
    try: SRC = sys.argv[1]
    except IndexError: SRC = 'Fenix.src'
    print FVM(SRC,open(SRC).read())
