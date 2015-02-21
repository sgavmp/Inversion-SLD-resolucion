#
#Autor: Sergio Garcia Alonso
#Correo: sga.vmp(at)gmail.com
#Clase: Ingenieria del Software 3 - Grupo 1
#Fecha: 02/06/2013
#Fecha Revision: 16/12/2013
#
"""
Sistema de representacion: El sistema de representacion elegido es una implementacion basada en los algoritmos del libro Inteligencia Artificial: Un Enfoque moderno. 
Se basa en una clase Expr la cual tiene 2 parametros:
	-op:un string o integer, que puede ser un operador logico, una funcion, una variable o una constante.
	-args: array de Expr, si esta vacio significa que la Expr es una cosntante sino, contiene a las Expr que forman parte de la operacion logica o los parametros de la funcion o constante.
Para construir desde string a una serie de Expr existe una funcion llamada expr que transforma un string a las Expr necesaria para representarlo. 
Las expresiones tienen que ser escritas sin espacios a no ser que se quiera crear un hecho por lo que el lado qe iria vacio tiene que tener un espacio en blanco, por ejemplo:
>>>expr("P(x,y)<==T(x,y)") (Funciona)
>>>expr("P(x,y)<== T(x,y)") (Falla por el espacio entre = y T)
>>>expr("P(x,y)<==") (Falla ya que la transforma como (<==P(x,y))
>>>expr("P(x,y)<== ") (Funciona)
Los predicados tienen que tener la primera letra en mayuscula.
Las funciones tienen que tener todas las letras en minuscula.
"""
import itertools, re
import copy
###################################################################################################################################################################
#Funciones auxiliares obtenidas de la libreria utils
#utils.py
def num_or_str(x):
    """The argument is a string; convert to a number if possible, or strip it.
    >>> num_or_str('42')
    42
    >>> num_or_str(' 42x ')
    '42x'
    """
    if isnumber(x): return x
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return str(x).strip()

def isnumber(x):
    "Is x a number? We say it is if it has a __int__ method."
    return hasattr(x, '__int__')
	
def issequence(x):
    "Is x a sequence? We say it is if it has a __getitem__ method."
    return hasattr(x, '__getitem__')

def some(predicate, seq):
    """If some element x of seq satisfies predicate(x), return predicate(x).
    >>> some(callable, [min, 3])
    1
    >>> some(callable, [2, 3])
    0
    """
    for x in seq:
        px = predicate(x)
        if px: return px
    return False
#/utils.py
###################################################################################################################################################################
#Sistema de representacion obtenido del documento localizado en http://aima-python.googlecode.com/svn/trunk/logic.py.
#Este codigo implemente los algoritmos del libro Inteligencia Artificial: Un Enfoque Moderno
#Algunas funciones han tenido que ser modificadas ya que estaba disenado para funcionar sobre Python 2.7, ademas de adaptarlas para el problema planteado.
#logic.py
class Expr:
    """A symbolic mathematical expression.  We use this class for logical
    expressions, and for terms within logical expressions. In general, an
    Expr has an op (operator) and a list of args.  The op can be:
      Null-ary (no args) op:
        A number, representing the number itself.  (e.g. Expr(42) => 42)
        A symbol, representing a variable or constant (e.g. Expr('F') => F)
      Unary (1 arg) op:
        '~', '-', representing NOT, negation (e.g. Expr('~', Expr('P')) => ~P)
      Binary (2 arg) op:
        '>>', '<<', representing forward and backward implication
        '+', '-', '*', '/', '**', representing arithmetic operators
        '<', '>', '>=', '<=', representing comparison operators
        '<=>', '^', representing logical equality and XOR
      N-ary (0 or more args) op:
        '&', '|', representing conjunction and disjunction
        A symbol, representing a function term or FOL proposition

    Exprs can be constructed with operator overloading: if x and y are Exprs,
    then so are x + y and x & y, etc.  Also, if F and x are Exprs, then so is
    F(x); it works by overloading the __call__ method of the Expr F.  Note
    that in the Expr that is created by F(x), the op is the str 'F', not the
    Expr F.   See http://www.python.org/doc/current/ref/specialnames.html
    to learn more about operator overloading in Python.

    WARNING: x == y and x != y are NOT Exprs.  The reason is that we want
    to write code that tests 'if x == y:' and if x == y were the same
    as Expr('==', x, y), then the result would always be true; not what a
    programmer would expect.  But we still need to form Exprs representing
    equalities and disequalities.  We concentrate on logical equality (or
    equivalence) and logical disequality (or XOR).  You have 3 choices:
        (1) Expr('<=>', x, y) and Expr('^', x, y)
            Note that ^ is bitwose XOR in Python (and Java and C++)
        (2) expr('x <=> y') and expr('x =/= y').
            See the doc string for the function expr.
        (3) (x % y) and (x ^ y).
            It is very ugly to have (x % y) mean (x <=> y), but we need
            SOME operator to make (2) work, and this seems the best choice.

    WARNING: if x is an Expr, then so is x + 1, because the int 1 gets
    coerced to an Expr by the constructor.  But 1 + x is an error, because
    1 doesn't know how to add an Expr.  (Adding an __radd__ method to Expr
    wouldn't help, because int.__add__ is still called first.) Therefore,
    you should use Expr(1) + x instead, or ONE + x, or expr('1 + x').
    """

    def __init__(self, op, *args):
        "Op is a string or number; args are Exprs (or are coerced to Exprs)."
        assert isinstance(op, str) or (isnumber(op) and not args)
        self.op = num_or_str(op)
        [*self.args] = map(expr, args) ## Coerce args to Exprs
        if (self.op=="<<" or self.op==">>") and len(self.args)==2:
            if self.args[0].op=="&":
                self.args[0]=associate(self.args[0].op,self.args[0].args)
            if self.args[1].op=="&":
                self.args[1]=associate(self.args[1].op,self.args[1].args)

    def __call__(self, *args):
        """Self must be a symbol with no args, such as Expr('F').  Create a new
        Expr with 'F' as op and the args as arguments."""
        assert is_symbol(self.op) and not self.args
        return Expr(self.op, *args)

    def __repr__(self):
        "Show something like 'P' or 'P(x, y)', or '~P' or '(P | Q | R)'"
        if not self.args:         # Constant or proposition with arity 0
            return str(self.op)
        elif is_symbol(self.op):  # Functional or propositional operator
            return '%s(%s)' % (self.op, ', '.join(map(repr, self.args)))
        elif len(self.args) == 1: # Prefix operator
            return self.op + repr(self.args[0])
        else:                     # Infix operator
            return '(%s)' % (' '+self.op+' ').join(map(repr, self.args))

    def __eq__(self, other):
        """x and y are equal iff their ops and args are equal."""
        return (other is self) or (isinstance(other, Expr)
            and self.op == other.op and self.args == other.args)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        "Need a hash method so Exprs can live in dicts."
        return hash(self.op) ^ hash(tuple(self.args))

    # See http://www.python.org/doc/current/lib/module-operator.html
    # Not implemented: not, abs, pos, concat, contains, *item, *slice
    def __lt__(self, other):     return Expr('<',  self, other)
    def __le__(self, other):     return Expr('<=', self, other)
    def __ge__(self, other):     return Expr('>=', self, other)
    def __gt__(self, other):     return Expr('>',  self, other)
    def __add__(self, other):    return Expr('+',  self, other)
    def __sub__(self, other):    return Expr('-',  self, other)
    def __and__(self, other):    return Expr('&',  self, other)
    def __div__(self, other):    return Expr('/',  self, other)
    def __truediv__(self, other):return Expr('/',  self, other)
    def __invert__(self):        return Expr('~',  self)
    def __lshift__(self, other): return Expr('<<', self, other)
    def __rshift__(self, other): return Expr('>>', self, other)
    def __mul__(self, other):    return Expr('*',  self, other)
    def __neg__(self):           return Expr('-',  self)
    def __or__(self, other):     return Expr('|',  self, other)
    def __pow__(self, other):    return Expr('**', self, other)
    def __xor__(self, other):    return Expr('^',  self, other)
    def __mod__(self, other):    return Expr('<=>',  self, other)
			
def expr(s):
    """Create an Expr representing a logic expression by parsing the input
    string. Symbols and numbers are automatically converted to Exprs.
    In addition you can use alternative spellings of these operators:
      'x ==> y'   parses as   (x >> y)    # Implication
      'x <== y'   parses as   (x << y)    # Reverse implication
      'x <=> y'   parses as   (x % y)     # Logical equivalence
      'x =/= y'   parses as   (x ^ y)     # Logical disequality (xor)
    But BE CAREFUL; precedence of implication is wrong. expr('P & Q ==> R & S')
    is ((P & (Q >> R)) & S); so you must use expr('(P & Q) ==> (R & S)').
    >>> expr('P <=> Q(1)')
    (P <=> Q(1))
    >>> expr('P & Q | ~R(x, F(x))')
    ((P & Q) | ~R(x, F(x)))
    """
    if isinstance(s, Expr): return s
    if isnumber(s): return Expr(s)
    ## Replace the alternative spellings of operators with canonical spellings
    s = s.replace('==>', '>>').replace('<==', '<<')
    s = s.replace('<=>', '%').replace('=/=', '^')
    ## Replace a symbol or number, such as 'P' with 'Expr("P")'
	#Modificado para que acepte clausulas vacias
    s = re.sub(r'([a-zA-Z0-9_. ]+)', r'Expr("\1")', s)
    ## Now eval the string.  (A security hole; do not use with an adversary.)
    return eval(s, {'Expr':Expr})

def is_symbol(s):
    "A string s is a symbol if it starts with an alphabetic char."
    return isinstance(s, str) and s[:1].isalpha()

def is_var_symbol(s):
    "A logic variable symbol is an initial-lowercase string."
    return is_symbol(s) and s[0].islower()

def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string other than
    TRUE or FALSE."""
    return is_symbol(s) and s[0].isupper() and s != 'TRUE' and s != 'FALSE'

def variables(s):
    """Return a set of the variables in expression s.
    >>> ppset(variables(F(x, A, y)))
    set([x, y])
    >>> ppset(variables(F(G(x), z)))
    set([x, z])
    >>> ppset(variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, z)')))
    set([x, y, z])
    """
    result = set([])
    def walk(s):
        if is_variable(s):
            result.add(s)
        else:
            for arg in s.args:
                walk(arg)
    walk(s)
    return result	
	
def unify(x, y, s):
    """Unify expressions x,y with substitution s; return a substitution that
    would make x,y equal, or None if x,y can not unify. x and y can be
    variables (e.g. Expr('x')), constants, lists, or Exprs. [Fig. 9.1]
    >>> ppsubst(unify(x + y, y + C, {}))
    {x: y, y: C}
    """
	#Modificado para que funcione correctamente con el problema planteado
    if s is None:
        return None
    elif x == y:
        return s
    elif is_variable(x):
        return unify_var(x, y, s)
    elif is_variable(y):
        return unify_var(y, x, s)
    elif isinstance(x, Expr) and isinstance(y, Expr):
        return unify(x.args, y.args, unify(x.op, y.op, s))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif issequence(x) and issequence(y) and len(x) == len(y):
        if not x: return s
        return unify(x[1:], y[1:], unify(x[0], y[0], s))
    else:
        return None

def is_variable(x):
    "A variable is an Expr with no args and a lowercase symbol as the op."
    return isinstance(x, Expr) and not x.args and is_var_symbol(x.op)

def unify_var(var, x, s):
    if var in s:
        return unify(s[var], x, s)
    elif occur_check(var, x, s):
        return None
    else:
        return extend(s, var, x)

def occur_check(var, x, s):
    """Return true if variable var occurs anywhere in x
    (or in subst(s, x), if s has a binding for x)."""
    if var == x:
        return True
    elif is_variable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, Expr):
        return (occur_check(var, x.op, s) or
                occur_check(var, x.args, s))
    elif isinstance(x, (list, tuple)):
        return some(lambda element: occur_check(var, element, s), x)
    else:
        return False

def extend(s, var, val):
    """Copy the substitution s and extend it by setting var to val;
    return copy.
    >>> ppsubst(extend({x: 1}, y, 2))
    {x: 1, y: 2}
    """
    s2 = s.copy()
    s2[var] = val
    return s2

def subst(s, x):
    """Substitute the substitution s into the expression x.
    >>> subst({x: 42, y:0}, F(x) + y)
    (F(42) + 0)
    """
	#Modificado para que funcione correctamente con el problema planteado
    if len(s)==0:
        return x
    if isinstance(x, list):
        return [subst(s, xi) for xi in x]
    elif isinstance(x, tuple):
        return tuple([subst(s, xi) for xi in x])
    elif not isinstance(x, Expr):
        return x
    elif is_var_symbol(x.op):
        if x in s:
            return s.get(x,x)
        elif not is_variable(x):
            return Expr(x.op, *[subst(s, arg) for arg in x.args])
        else:
        	return x
    elif isinstance(x.op,int):
        return s.get(x,x)
    else:
        return Expr(x.op, *[subst(s, arg) for arg in x.args])
	
def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return Expr(op)
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)

def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args)."""
    result = []
    def collect(subargs):
        for arg in subargs:
            if arg.op == op: collect(arg.args)
            else: result.append(arg)
    collect(args)
    return result
#/logic.py
###################################################################################################################################################################
#Funciones auxiliares
def constants(s):
    """Devuelve un set de constantes en la expresion s.
	EJ:
    >>> ppset(variables(F(x, A, y)))
    set([A])
    >>> ppset(variables(F(G(0), z)))
    set([])
    >>> ppset(variables(expr('F(x, x) & G(x, y) & h(B) & R(A, z, z)')))
    set([h(B),A])
    """
    result = set([])
    def walk(s):
        if is_constant(s):
            result.add(s)
        for arg in s.args:
            walk(arg)
    walk(s)
    return result

def is_constant(s):
	"""Devueve si s es una constante o no.
	s es constante si su operador no es una variable y no tiene argumentos o si el operador es tipo strinf slfabetico y en minuscula y solo tiene un argumento
	EJ:
	>>>is_constant(s(x))
	False
	>>>is_constant(s(0))
	True
	>>>is_constant(0)
	True
	"""
	return (not is_variable(s.op) and not s.args) or (is_var_symbol(s.op) and is_constant(s.args[0]) and len(s.args)==1)
	
def get_head(s):
	"""Devuelve la cabeza de la expresion
	EJ:
	>>>get_head(F(x,Z)<<P(k,z))
	[F(x,z)]
	"""
	if s.op=="<<":
		return s.args[0]
	elif s.op==">>":
		return s.args[1]
	else:
		return None

def get_body(s):
	"""Devuelve el cuerpo de la expresion
	EJ:
	>>>get_head(F(x,Z)<<P(k,z))
	[P(k,z)]
	>>>get_head(F(x,Z)<<P(k,z)&T(z,k))
	[P(k,z),T(z,k)]
	"""
	if s.op=="<<":
		if s.args[1].op=="&":
			return s.args[1].args
		else:
			return [s.args[1]]
	elif s.op==">>":
		if s.args[1].op=="&":
			return s.args[0].args
		else:
			return [s.args[0]]
	else:
		return s

def new_variable_unify(u):
	"""Dada la unificacion de expresiones recibida, de cada par clave valor(k:v) se crea 2 pares nuevo, 
	uno con la clave original y de valor una variable nueva y otro con el valor original y una variable nueva
	EJ: 
	>>new_variable_unify({x:y})
	{x:a,y:a}
	"""
	newU=dict()
	lVar=set('abcdefg')
	for a in u.keys():
		if (is_variable(u[a])):
			var=lVar.pop()
			newU[a]=Expr(var)
			newU[u[a]]=Expr(var)
		else:
			newU[a]=u[a]
	return newU
		
def create_unify(s,t):
	"""Encuentra la constante con mayor profundida que se encuentre en ambas expresiones y le asigna una variable.
	EJ:
	>>>create_unify(T(s(s(0))),k),P(s(0)))
	{s(0):a}
	"""
	cS=constants(s)
	cT=constants(t)
	uni=cS&cT
	maxL=-1
	maxE=None
	for c in uni:
		l=len_expr(c)
		if l>maxL: 
			maxL=l
			maxE=c
	return {maxE:Expr('a')}
		
def len_expr(s):
	"""Devuelve la profundida de una expresion.
	EJ:
	>>>len_expr(s(s(s(0))))
	3
	>>>len_expr(s(s(0)))
	2
	>>>len_expr(0)
	0
	"""
	l=-1
	for arg in s.args:
		t=len_expr(arg)
		if t>l: l=t
	return (l+1)
		
def interseccion_operadores(s, t):
	"""Devuelve la interseccion entre las expresiones s y t.
	s y t son listas
	Devuelve la interseccion con las expresiones de la lista s
	EJ:
	>>>interseccion_operadores([T(a,k),P(a,k),R(a,k)],[T(x,y),P(x,y),S(a,k)])
	[T(a,k),P(a,k)]
	>>>interseccion_operadores([T(x,y),P(x,y),S(a,k)],[T(a,k),P(a,k),R(a,k)])
	[T(x,y),P(x,y)]
	"""
	list=[]
	oper=[]
	if isinstance(s,Expr):
		s=[s]
	if isinstance(t,Expr):
		t=[t]
	for a in s:
		for e in t:
			if a.op==e.op and a.op!=" ":	
				if not a.op in oper:
					list.append(a)
					oper.append(a.op)
	return list

def constante_profunda(s):
	"""Localiza la constante mas profunda de la expresion s
	Ej:
	>>constante_profunda(Nat(s(s(0))))
	0
	(s(s(0)), s(0) y 0 son constantes pero la mas profunda es 0)
	"""
	if (not is_variable(s.op)) and len(s.args)==0:
		return s
	else:
		return constante_profunda(s.args[0])
	
def remove_op_blank(s):
	"""Esta funcion borra las expresiones cuyo operador sea un espacio en blanco o un caracter vacio. 
	Esta funcion se ha creado para poder crear expresiones sin cuerpo
	"""
	list=[]
	for c in s:
		if c.op!=" " and c.op!="":
			list.append(c)
	return list
	
def resta_sin_op(a,b):
	return [item for item in a if item not in b]
	
def resta(a,b):
	"""if a.op=="<<" or a.op==">>":
		return [item for item in a.args[1].args if item not in b]
	else:
		return [item for item in a.args[1] if item not in b]"""
	return [item for item in a if item not in b]
		
###################################################################################################################################################################
#Funciones de los 4 operadores implementados
#Identificacion		
def v_operator_iden(c,c2):
	"""Aplica el V-operador de identificacion a las clausulas c y c2 para obtener c1
	"""
	#La cabeza de C y C2 es p
	p=get_head(c)
	p2=get_head(c2)
	#Obtenemos los cuerpos de cada expresion
	cuerpoC=remove_op_blank(get_body(c))
	cuerpoC2=remove_op_blank(get_body(c2))
	#Tenemos que saber que argumentos de C son de C1 y cuales de C2, para ello obtenemos B que son los argumentos de C procedentes de C2
	#Para obtener B realizamos la interseccion entre los cuerpos de C y C2
	B=interseccion_operadores(cuerpoC,cuerpoC2)
	#Tambien hacemos la interseccion pero con las sentencias intercambiadas (c2,c), obteniendo B1
	B1=interseccion_operadores(cuerpoC2,cuerpoC)
	#Para obtener los valores de C que son de C1 realizamos la operacion C.cuerpo-B
	A=resta(cuerpoC,B)
	#Para obtener la cabeza de C1 realizamos la operacion C2.operacion-B1
	if len(B1)==0 and len(cuerpoC2)==1:
		q=cuerpoC2
	else:
		q=resta(cuerpoC2,B1)
	#Comenzando formando c1 partiendo del operador implicacion
	c1=Expr("<<")
	#Anadimos a los argumentos la cabeza de la funcion
	if isinstance(q,Expr):
		c1.args.append(q)
	else:
		c1.args.append(q[0])
	#Anadimos una nueva expresion vacia de operador & que sera donde almacenemos el resto de expresiones (las expresiones de A y q)
	if len(A)>1:
		c1.args.append(Expr("&"))
		#Anadimos el cuerpo de C1
		[c1.args[1].args.append(item) for item in A]
	elif len(A)==0:
		c1.args.append(Expr(""))
	else:
		#Anadimos el cuerpo de C1
		c1.args.append(A[0])
	#Realizamos las unificaciones de los terminos comunes en C y C2 que son p y B
	uniP=unify(p,p2,{})
	uniB=unify(B,B1,{})
	uniP.update(uniB)
	unificacion=uniP
	if len(variables(c))==len(uniP) or len(variables(c2))==len(uniP):
		if len(uniP)==0:
			#Si no hay variables creamos la unificacion maxima posible a realizar
			unificacion=create_unify(c,c1)
		else:
			#Si hay variables asignamos variables nuevas a la sustituciones existente entre C y C2
			unificacion=new_variable_unify(uniP)
		if len(A)>0:
			c1=subst(unificacion,c1)
		else:
			#En el caso de que A este vacio, C es un hecho por tanto se aplica la sustitucion entre C y C2 sin cambiar variables
			c1=subst(uniP,c1)
	print("La unificacion necesaria a aplicar a C y C2 es:",unificacion)
	#Devolvemos c1
	return c1
	
#Absorcion
def v_operator_abs(c,c1):
	"""Aplica el V-operador de identificacion a las clausulas c y c2 para obtener c1
	"""
	#La cabeza de C es p
	p=c.args[0]
	#La cabeza de C1 es q
	q=c1.args[0]
	#Tenemos que saber que argumentos de C son de C1 y cuales de C2, para ello obtenemos A que son los argumentos de C procedentes de C1
	#Para obtener A realizamos la interseccion entre los cuerpos de C y C2
	cuerpoC=remove_op_blank(get_body(c))
	cuerpoC1=remove_op_blank(get_body(c1))
	A=interseccion_operadores(cuerpoC,cuerpoC1)
	A1=interseccion_operadores(cuerpoC1,cuerpoC)
	#Para obtener los valores de C que son de C2 realizamos la operacion C.cuerpo-A
	B=resta(cuerpoC,A)
	#Comenzando formando c2 partiendo del operador implicacion
	c2=Expr("<<")
	#Anadimos a los argumentos la cabeza de la funcion
	c2.args.append(p)
	#Anadimos una nueva expresion vacia de operador & que sera donde almacenemos el resto de expresiones (las expresiones de B y q)
	if len(B)>=1:
		c2.args.append(Expr("&"))
		#Anadimos el cuerpo de C1
		c2.args[1].args.append(q)
		[c2.args[1].args.append(item) for item in B]
	elif len(B)==0:
		c2.args.append(q)
	else:
		#Anadimos el cuerpo de C1
		c1.args.append(B[0])
	#Realizamos las unificaciones de los terminos en comun entre C y C1 que es A
	uniA=unify(A,A1,{})
	unificacion=uniA
	if len(variables(c))==len(uniA) or len(variables(c1))==len(uniA):
		if len(uniA)==0:
			#Si no hay variables se crea la unificacion maxima posible
			unificacion=create_unify(c,c1)
		else:
			unificacion=new_variable_unify(uniA)
		c2=subst(unificacion,c2)
	#Devolvemos c2
	print("La unificacion necesaria a aplicar a C y C1 es:",unificacion)
	return c2

#Decisiones tomadas en Intra-Construccion: A la hora de crear la propisicion(q) se crea con el nombre indicado por parametros y para asignar las variables se le asigna
#los mismos parametros que tenga p, ya sean variables o constantes.	
#Intra-Construccion
def w_operator_intra(B1,B2,s):
	"""Dado las expresiones B1 y B2 y un nombre s para la proposicion que hay que inventar se aplica Intra-Construccion
	para encontrar C,C1 y C2.
	"""
	#Se crea un diccionario donde guardar las soluciones
	expresiones={}
	#Se sacan las cabezas de B1 y B2, ambos son p
	p1=get_head(B1)
	p2=get_head(B2)
	#Se consigue los cuerpos de B1 y B2
	cuerpoB1=get_body(B1)
	cuerpoB2=get_body(B2)
	#Se calcula A entre los cuerpos de B1 y B2,al tener B1 y B2 variables distintas habra dos A distintas, A y A1
	A=interseccion_operadores(cuerpoB1,cuerpoB2)
	A1=interseccion_operadores(cuerpoB2,cuerpoB1)
	#Se calcula B del cuerpo de B1
	B=resta_sin_op(cuerpoB1,A)
	#Se calcula C(como conjunto de expresiones) del cuerpo de B2
	c=resta_sin_op(cuerpoB2,A1)
	#Inventamos una proposicion segun el nombre s proporcionado
	q=Expr(s)
	lVar=set('abcdefg')
	#Se anade el mismo numero de variables que tiene p1
	for i in p1.args:
		q.args.append(Expr(lVar.pop()))
	#Creamos C con los conjuntos p,A y q
	C=Expr("<<")
	C.args.append(copy.copy(p1))
	C.args[0].args=q.args
	cA=None
	if len(remove_op_blank(A))>0:
		C.args.append(Expr("&"))
		for i in A:
			ci=copy.copy(i)
			ci.args=q.args
			C.args[1].args.append(ci)
		cA=copy.copy(C.args[1].args)
		C.args[1].args.append(q)
	else:
		C.args.append(q)
	#Anadimos C al diccionario de expresiones
	expresiones['C']=C
	#Creamos C1 con los conjuntos q,A y B
	C1=Expr("<<")
	q1=copy.copy(q)
	q1.args=p1.args
	C1.args.append(q1) 
	if len(A)>0 and len(B)>0:
		C1.args.append(Expr("&"))
		C1.args[1].args.extend(A)
		C1.args[1].args.extend(B)
	else:
		C1.args.append(Expr(" "))
	#Anadimos C1 al diccionario de expresiones
	expresiones['C1']=C1
	#Creamos C2 con los conjuntos q,A y C(como conjunto de expresiones)
	C2=Expr("<<")
	q2=copy.copy(q)
	q2.args=p2.args
	C2.args.append(q2) 
	if len(A1)>0 and len(c)>0:
		C2.args.append(Expr("&"))
		C2.args[1].args.extend(A1)
		C2.args[1].args.extend(c)
	else:
		C2.args.append(Expr(" "))
	#Anadimos C al diccionario de expresiones
	expresiones['C2']=C2
	uni1=unify(q,q1,{})
	uniA=unify(cA,A,{})
	if (uniA!=None):
		uni1.update(uniA)
	uni2=unify(q,q2,{})
	uniA=unify(cA,A1,{})
	if (uniA!=None):
		uni2.update(uniA)
	print("La unificacion necesaria a aplicar a C y C1 para obtener B1 es:",uni1)
	print("La unificacion necesaria a aplicar a C y C2 para obtener B2 es:",uni2)
	return expresiones

#Decisiones tomado en Inter-Construccion: A la hora de construir la proposicion nueva(r) se elige como nombre el indicado por parametro y para las variables se anade tanta variables
#como tenga la primera funcion de A. Si A esta vacia se anade una constante, seleccionando la constante mas profunda de B1.
#Inter-Construccion
def w_operator_inter(B1,B2,s):
	"""Dado las expresiones B1 y B2 y un nombre s para la proposicion que hay que inventar se aplica Inter-Construccion
	para encontrar C,C1 y C2.
	"""
	#Creamos un diccionario vacio donde guardar las expresiones resultantes
	expresiones={}
	#Obtenemos la cabeza de B1 y B2
	p=get_head(B1)
	q=get_head(B2)
	#Obtenemos los cuerpos
	cuerpoB1=remove_op_blank(get_body(B1))
	cuerpoB2=remove_op_blank(get_body(B2))
	#Obtenemos de los cuerpos de B1 y B2 los conjuntos de expresiones A, B y C. Habra A y A1 con los conjuntos con la notacion usada en B1 y B2 respectivamente.
	A=interseccion_operadores(cuerpoB1,cuerpoB2)
	A1=interseccion_operadores(cuerpoB2,cuerpoB1)
	B=resta_sin_op(cuerpoB1,A)
	c=resta_sin_op(cuerpoB2,A1)
	#La proposicion inventada con el nombre indicado en s
	r=Expr(s)
	#Si no tiene cuerpo es un hecho por tanto se crea la proposicion con constante
	if len(A)!=0:
		#Variable
		lVar=set('abcdefg')
		#Se anade el mismo numero de variables que tiene A
		for i in p.args:
			r.args.append(Expr(lVar.pop()))
	else:
		#Constante
		r.args.append(constante_profunda(B1))
	#Crea C
	C=Expr("<<")
	#Anade la cabeza
	C.args.append(r)
	#Se anade el cuerpo
	if len(A)>1:
		C.args.append(Expr("&"))
	else:
		#Si no tiene cuerpo se anade una expresion vacia
		C.args.append(Expr(""))
	for i in A:
		ci=copy.copy(i)
		ci.args=r.args
		C.args[1].args.append(ci)
	cA=copy.copy(C.args[1].args)
	#Se anade al diccionario de expresiones
	expresiones['C']=C
	#Crea C1
	C1=Expr("<<")
	#Anade la cabeza
	C1.args.append(p)
	#Se anade el cuerpo
	if len(A)!=0 or len(B)!=0:
		C1.args.append(Expr("&"))
		C1.args[1].args.append(r)
	else:
		C1.args.append(r)
	#Se anaden los conjuntos A y B al cuerpo, si esta vacio no agrega nada
	C1.args[1].args.extend(A)
	C1.args[1].args.extend(B)
	#Se anade al diccionario de expresiones
	expresiones['C1']=C1
	#Crea C2
	C2=Expr("<<")
	#Anade la cabeza
	C2.args.append(q)
	#Se anade el cuerpo
	if len(A)!=0 or len(c)!=0:
		C2.args.append(Expr("&"))
		C2.args[1].args.append(r)
	else:
		C2.args.append(r)
	#Se anaden los conjuntos A y C al cuerpo, si esta vacio no agrega nada
	C2.args[1].args.extend(A1)
	C2.args[1].args.extend(c)
	#Se anade al diccionario de expresiones
	expresiones['C2']=C2
	print("La unificacion necesaria a aplicar a C y C1 para obtener B1 es:",unify(cA,A,{}))
	print("La unificacion necesaria a aplicar a C y C2 para obtener B2 es:",unify(cA,A1,{}))
	return expresiones
	
###################################################################################################################################################################
#Funciones que se ejecutan desde consola.
def v_operator(s, t):
	"""Dado 2 expresiones identificamos si corresponde aplicar absorcion o identificacion
	"""
	uni=unify(get_head(s),get_head(t),{})
	if get_head(s).op==get_head(t).op and uni!=None:
		print("===============Se aplica identificacion=================")
		return v_operator_iden(s,t)
	else:
		print("==================Se aplica absorcion===================")
		return v_operator_abs(s,t)
	
def w_operator(s, t, e):
	"""Dado 2 expresiones identificamos si corresponde aplicar intra-construccion o interconstruccion
	"""
	if get_head(s).op==get_head(t).op:
		print("===============Se aplica Intra-Construccion=================")
		return w_operator_intra(s,t,e)
	else:
		print("==================Se aplica Inter-Construccion===================")
		return w_operator_inter(s,t,e)
	
###################################################################################################################################################################	
#Bibliografia
"""
Inductive Logic Programming: Theory and methods; STEPHEN MUGGLETON,LUC DE RAEDT
Machine Invention of First-Order Predicates by Inverting Resolution; STEPHEN MUGGLETON, WRAY BUNTINE
Simple Improvements of a Simple Solution for Inverting Resolution; JAN C. BIOCH, PATRICK R.J. VAN DER LAAG
Resolucion lineal y, en particular, Resolucion SLD;Facultad de Ciencias Exactas y Naturales Universidad de Buenos Aires
Operadores de generalizacion para el aprendizaje clausal;MIGUEL ANGEL GUTIERREZ NARANJO
	
"""	
###################################################################################################################################################################
#Pruebas
print("========================================================================================")
print("==============================Inteligencia Artificial 3 Grupo 1=========================")
print("====================================Sergio Garcia Alonso================================")
print("")
print("")
print("")
print("========================================================")
print("=======================V-Operador 1=====================")
print("========================================================")
print("")
expc1=expr('Progenitor(x,y)<==(Madre(x,y))')
expc2=expr('Hija(t,r)<==(Progenitor(r,t)&Mujer(t))')
expc=expr('Hija(v,w)<==(Madre(w,v)&Mujer(v))')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("")
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("========================================================")
print("=======================V-Operador 2=====================")
print("========================================================")
print("")
expc1=expr('Nat(s(0))<== ')
expc2=expr('Nat(s(x))<==Nat(x)')
expc=expr('Nat(s(s(0)))<== ')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("========================================================")
print("=======================V-Operador 3=====================")
print("========================================================")
print("")
expc1=expr('ApruebaTeoria(x)<==(ApruebaP1(x)&ApruebaP2(x))')
expc2=expr('ApruebaIA(z)<==(ApruebaTeoria(z)&ApruebaPractica(z))')
expc=expr('ApruebaIA(y)<==(ApruebaP1(y)&ApruebaP2(y)&ApruebaPractica(y))')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("")
print("")
print("========================================================")
print("=======================W-Operador 4=====================")
print("========================================================")
print("")
b1=expr("Descendiente(x1,y1)<==(Mujer(x1)&Madre(y1,x1))")
b2=expr("Descendiente(x2,y2)<==(Mujer(x2)&Padre(y2,x2))")
expc1=expr('Hija(a,b)<==(Mujer(a)&Madre(b,a))')
expc2=expr('Hija(a,b)<==(Mujer(a)&Padre(b,a))')
expc=expr('Descendiente(a,b)<==(Mujer(a)&Hija(a,b))')
print("===== B1:",b1)
print("===== B2:",b2)
print("===== C:",expc)
print("===== C1:",expc1)
print("===== C2:",expc2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"Hija")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("========================================================")
print("=======================W-Operador 5=====================")
print("========================================================")
print("")
b1=expr("Nat(s(0))<== ")
b2=expr("Nat(s(s(0)))<== ")
expc1=expr('Nat(s(x))<==Nat(x)')
expc2=expr('Nat(s(s(x)))<==Nat(x)')
expc=expr('Nat(0)<== ')
print("===== B1:",b1)
print("===== B2:",b2)
print("===== C:",expc)
print("===== C1:",expc1)
print("===== C2:",expc2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Inter-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"Tan")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("========================================================")
print("=======================W-Operador 6=====================")
print("========================================================")
print("")
b1=expr("Abuelo(x,y)<==(Padre(x,z)&Padre(z,y))")
b2=expr("Abuelo(x2,y2)<==(Padre(x2,z2)&Madre(z2,y2))")
expc1=expr('Nieto(x3,y3)<==(Padre(x3,z3)&Padre(z3,y3))')
expc2=expr('Nieto(x4,y4)<==(Padre(x4,z4)&Madre(z4,y4))')
expc=expr('Abuelo(x5,y5)<==(Padre(x5,z5)&Nieto(y5,x5))')
print("===== B1:",b1)
print("===== B2:",b2)
print("===== C:",expc)
print("===== C1:",expc1)
print("===== C2:",expc2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"Nieto")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("========================================================")
print("=======================W-Operador 7=====================")
print("========================================================")
print("")
b1=expr("Mortal(x)<==(Filosofo(x)&Real(x))")
b2=expr("Inmortal(y)<==(Filosofo(y)&Irreal(y))")
expc1=expr('Mortal(z)<==(Humano(z)&Filosofo(z)&Real(z))')
expc=expr('Humano(t)<==(Filosofo(t))')
expc2=expr('Inmortal(r)<==(Humano(r)&Filosofo(r)&Irreal(r))')
print("===== B1:",b1)
print("===== B2:",b2)
print("===== C:",expc)
print("===== C1:",expc1)
print("===== C2:",expc2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"Humano")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("========================================================")
print("=======================V-Operador 8=====================")
print("========================================================")
print("")
expc1=expr('Nat(s(y))<==Nat(y)')
expc2=expr('Nat(s(s(z)))<== ')
expc=expr('Nat(s(s(s(z))))<== ')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("")
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("========================================================")
print("=======================V-Operador 9=====================")
print("========================================================")
print("")
expc1=expr('q<==(p1&p2)')
expc2=expr('p<==(q&p3&p4)')
expc=expr('p<==(p1&p2&p3&p4)')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("")
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("========================================================")
print("=======================W-Operador 10=====================")
print("========================================================")
print("")
b1=expr("P(x)<==(Q(x)&R(x))")
b2=expr("P(x)<==(Q(x)&S(x))")
print("===== B1:",b1)
print("===== B2:",b2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"T")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("========================================================")
print("=======================W-Operador 11=====================")
print("========================================================")
print("")
b1=expr("P(x)<==(R(x)&T(x)&S(x))")
b2=expr("P(z)<==(R(z)&S(z)&V(z))")
print("===== B1:",b1)
print("===== B2:",b2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"Q")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("========================================================")
print("=======================W-Operador 12=====================")
print("========================================================")
print("")
b1=expr("R(A,x)<==(T(A,x)&S(x))")
b2=expr("R(B,z)<==(T(B,z)&Q(z))")
print("===== B1:",b1)
print("===== B2:",b2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"P")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("========================================================")
print("=======================V-Operador 13=====================")
print("========================================================")
print("")
expc1=expr('(R(A,z))<==(T(z,z))')
expc2=expr('(P(f(x,B)))<==(R(x,B))')
expc=expr('(P(f(A,B)))<==(T(B,B))')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("")
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("========================================================")
print("=======================V-Operador 14=====================")
print("========================================================")
print("")
expc1=expr('(R(z,A))<==(T(z,z))')
expc2=expr('(P(f(B,x)))<==(R(B,x))')
expc=expr('(P(f(B,A)))<==(T(B,B))')
print("===== C1:",expc1)
print("===== C2:",expc2)
print("===== C:",expc)
print("")
print("======================")
print("La expresion correspondiente a C1 aplicando el operador Identificacion a C y C2")
print("")
print("===== C1:",v_operator(expc,expc2))
print("")
print("======================")
print("La expresion correspondiente a C2 aplicando el operador Absorcion a C y C1")
print("")
print("===== C2:",v_operator(expc,expc1))
print("")
print("")
print("========================================================")
print("=======================W-Operador 15=====================")
print("========================================================")
print("")
b1=expr("R(A,x)<==(T(A,x)&S(x))")
b2=expr("C(B,z)<==(T(B,z)&Q(z))")
print("===== B1:",b1)
print("===== B2:",b2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"P")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("")
print("========================================================")
print("=======================W-Operador 16=====================")
print("========================================================")
print("")
b1=expr("R(y,x)<==(T(y,x)&S(x))")
b2=expr("C(y,z)<==(T(y,z)&Q(z))")
print("===== B1:",b1)
print("===== B2:",b2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"P")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print("")
print("========================================================")
print("=======================W-Operador 17=====================")
print("========================================================")
print("")
b1=expr("R(A,B)<==(T(A,B))")
b2=expr("C(C,D)<==(T(C,D))")
print("===== B1:",b1)
print("===== B2:",b2)
print("======================")
print("La expresion correspondiente a C,C1 y C2 aplicando el operador Intra-construccion a B1 y B2")
print("")
expresiones=w_operator(b1,b2,"P")
for k in expresiones.keys():
	print("")
	print("El valor de ",k," es:")
	print(expresiones[k])
print("")
print(is_variable(expr("x")))
print(is_variable(expr("x1")))
print(is_variable(expr("x23123")))
print(is_variable(expr("xasda2231")))
print(is_variable(expr("12")))
print(is_variable(expr("12x")))
print(is_variable(expr("12x31")))
print(is_variable(expr("A")))
