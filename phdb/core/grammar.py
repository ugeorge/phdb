import ply.lex as lex


tokens = [ 'TAG', 'RPAR', 'LPAR', 'NOT', 'AND','OR' ]
t_TAG = r'[a-zA-Z_][a-zA-Z0-9_-]*'
t_RPAR = r'\)'
t_LPAR = r'\('
t_NOT = r'/'
t_AND = r'&'
t_OR = r'\|'
t_ignore  = ' \t\v\r' # whitespace

def t_error(t):
    print "Illegal character " + t.value[0]
    t.lexer.skip(1)


lex.lex() # Build the lexer

lex.input("(tag2 | tag1) & /ceva")

while True:
	tok = lex.token()
	if not tok: break
	print tok.type

import ply.yacc as yacc

def p_exp_or(p):
	'''expr : term OR term'''
	p[0] = ('|',p[1], p[3])

def p_exp_term(p):
	'''expr : term'''
	p[0] = p[1]

def p_term_and(p):
	'''term : factor AND factor'''
	p[0] = ('&',p[1], p[3])

def p_term_factor(p):
	'''term : factor'''
	p[0] = p[1]

def p_factor_tag(p): 
	'''factor : TAG'''
	p[0] = ('TAG',p[1])

def p_not(p):
	'''factor : NOT factor'''
	p[0] = ('/',p[2])

def p_par(p): 
	'''factor : LPAR expr RPAR'''
	p[0] = p[2]
	
def p_error(t): 
	raise NameError("Syntax error at '%s'" % t.value)

yacc.yacc() 
data = "/(tag2 | tag1 & tag0) & /ceva"
#data = "/(tag2 / tag1 & tag0) & /ceva"
t = yacc.parse(data)
print t
