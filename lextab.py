# lextab.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'FALSE': 1, 'LPAREN': 1, 'SEMI': 1, 'MACRO': 1, 'INLINE_STRING': 1, 'COMMA': 1, 'PRAGMA': 1, 'RPAREN': 1, 'TRUE': 1, 'ID': 1}
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive', 'pragma': 'exclusive'}
_lexstatere   = {'INITIAL': [("(?P<t_PRAGMA>(?i)PRAGMA)|(?P<t_ANY_SEMI>;)|(?P<t_ANY_ID>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<t_ANY_COMMENT>--.*|\\/\\*(.|\\n)*?\\*\\/)|(?P<t_ANY_INLINE_STRING>\\'(.|\\n|\\'\\')*?\\')", [None, ('t_PRAGMA', 'PRAGMA'), ('t_ANY_SEMI', 'SEMI'), ('t_ANY_ID', 'ID'), ('t_ANY_COMMENT', 'COMMENT'), None, ('t_ANY_INLINE_STRING', 'INLINE_STRING')])], 'pragma': [("(?P<t_ANY_SEMI>;)|(?P<t_ANY_ID>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<t_ANY_COMMENT>--.*|\\/\\*(.|\\n)*?\\*\\/)|(?P<t_ANY_INLINE_STRING>\\'(.|\\n|\\'\\')*?\\')|(?P<t_pragma_LPAREN>\\()|(?P<t_pragma_RPAREN>\\))|(?P<t_pragma_COMMA>,)", [None, ('t_ANY_SEMI', 'SEMI'), ('t_ANY_ID', 'ID'), ('t_ANY_COMMENT', 'COMMENT'), None, ('t_ANY_INLINE_STRING', 'INLINE_STRING'), None, (None, 'LPAREN'), (None, 'RPAREN'), (None, 'COMMA')])]}
_lexstateignore = {'INITIAL': ' \n\t', 'pragma': ' \n\t'}
_lexstateerrorf = {'INITIAL': 't_error', 'pragma': 't_ANY_error'}
