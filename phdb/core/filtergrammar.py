import os
import logging
import ply.lex  as lex
import ply.yacc as yacc
'''
try:
	confPath = os.path.join(os.getenv('PHDB_CFG_PATH'), "logger.conf")
	logging.config.fileConfig(confPath)
except AttributeError:
	log.warn("PHDB_CFG_PATH was not set. Cannot log events.")
log = logging.getLogger('')
'''
tokens = [ 'TAG', 'RPAR', 'LPAR', 'NOT', 'AND','OR', 'WILD' ]
t_TAG = r'[a-zA-Z_][a-zA-Z0-9_-]*'
t_RPAR = r'\)'
t_LPAR = r'\('
t_NOT = r'/'
t_AND = r'&'
t_OR = r'\|'
t_WILD = r'\*'
t_ignore  = ' \t\v\r' # whitespace

def t_error(t):
    log.warn ("Ignoring illegal character " + str(t.value[0]))
    t.lexer.skip(1)

lex.lex() # Build the lexer

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
	'''factor : wildtag'''
	p[0] = p[1]

def p_not(p):
	'''factor : NOT factor'''
	p[0] = ('/',p[2])

def p_par(p): 
	'''factor : LPAR expr RPAR'''
	p[0] = ('()',p[2])

def p_wildtag_tag(p): 
	'''wildtag : TAG'''
	p[0] = ('TAG',p[1])

def p_wildtag_wildb(p): 
	'''wildtag : WILD TAG'''
	p[0] = ('WILDB',p[2])

def p_wildtag_wilda(p): 
	'''wildtag : TAG WILD'''
	p[0] = ('WILDA',p[1])


def p_error(t): 
	raise NameError("Syntax error at '%s'" % t.value)

yacc.yacc() 


def getExpTree(filtExp):
	return yacc.parse(filtExp)


