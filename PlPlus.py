from Parser import Parser
class D(dict):
    def __init__(self,p,arr,repr):
        for i,a in enumerate(arr):
            self[arr[i]] = p[i+1]
        #self = self.append(zip(arr,p))
        self["repr"] = repr
    def __getattr__(self,name):
        return self[name] if self[name] is not None else ''
    def __repr__(self):
        return self["repr"] if not callable(self["repr"]) else self["repr"](self)

class PlPlus(Parser):

    keywords = (#'PRAGMA','MACRO','SUBSTITUTE',
        'FUNCTION','PROCEDURE','RETURN','BEGIN',
        'END','IS','BODY','IN','OUT','REF','DEFAULT','NULL',
        )

    oracle_types = ('NUMBER','INTEGER',
        'DATE','STRING','VARCHAR2','RAW','BOOLEAN','EXCEPTION',
        'INTERVAL','TIMESTAMP','BLOB','CLOB','BFILE','LONG','LONG_RAW',
        )

    tokens = keywords + oracle_types + (
        #'NUMBER',
        'ID','LPAREN', 'RPAREN','LBRACKET', 'RBRACKET','COMMA', 
        'PERIOD', 'SEMI', 'COLON','DIGIT','COMMENT','INLINE_STRING',
        'PRAGMA_MACRO',
    )

    states = (
        ('preprocessing','exclusive'),
        ('body'         ,'exclusive'),
        ('is'           ,'exclusive'),
    )

    t_DIGIT     = r'\d+'
    t_ignore    = r' '
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LBRACKET  = r'\['
    t_RBRACKET  = r'\]'
    t_COMMA     = r','
    t_PERIOD    = r'\.'
    t_SEMI      = r';'
    t_COLON     = r':'

    def t_ANY_COMMENT(self,t):
        r'--.*|\/\*(.|\n)*?\*\/'

    def t_body_is_INLINE_STRING(self,t):
        r'\'.*?\''
        return t
    #def t_body_INLINE_STRING(self,t):
    #    r'\'.*?\''
    #def t_is_INLINE_STRING(self,t):
    #    r'\'.*?\''

    def t_preprocessing_PRAGMA_MACRO(self,t):
        r'(?i)PRAGMA\s+MACRO'
        print 'MACRO!',t.value,t.type        
        return t

    t_ANY_ignore = " \t\n"
    def t_ANY_error(self,t):    # For bad characters, we just skip over it
        t.lexer.skip(1)
        #print "ERROR! t=",t.value

    def begin_state(self,t,name):
        t.lexer.code_start = t.lexer.lexpos        # Record the starting position
        #t.lexer.level = 1                          # Initial brace level
        t.lexer.begin(name)                        # Enter 'ccode' state
        return t

    def next_state(self,t,state_name,type_name):
        t.value = t.lexer.lexdata[t.lexer.code_start:t.lexer.lexpos-5]
        t.type = type_name
        t.lexer.lineno += t.value.count('\n')
        t.lexer.begin(state_name)
        t.lexer.lexpos -= 5
        return t
    macro_stack = ['ROOT']
    def t_body_is_ID(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        if t.lexer.current_state() == 'INITIAL':
            t.lexer.begin('preprocessing')
            return t
        state = t.lexer.current_state()
        value = t.value.upper()
        stack = self.stack
        #print "ID",value

        if state in ['is','body']:
            if not value in ['FUNCTION','PROCEDURE','BEGIN','END','CASE','LOOP','IF' ]:
                return

        if value in self.keywords or value in self.oracle_types:
            t.type = value
        if state == 'INITIAL':
            
            if value == 'IS':
                self.begin_state(t,'is')
                return 
            elif value == 'BEGIN':
                self.begin_state(t,'body')
        elif state == 'body':
            if value == 'BEGIN':
                if stack[-1] in ['FUNCTION','PROCEDURE']:
                    return
                else:
                    stack.append('ANANYMUS_BLOCK')
                    return
            elif value in ['CASE']:
                stack.append(value)
                return
            elif value in ['LOOP','IF']:
                if stack[-1] == 'END':
                    stack.pop()
                    stack.pop()
                else:
                    stack.append(value)
                return
            elif value in ['FUNCTION','PROCEDURE']:
                stack.append(value)
                return
            elif value =='END':
                if stack[-1] in ['CASE','FUNCTION','PROCEDURE','ANANYMUS_BLOCK']:
                    stack.pop()
                elif stack[-1] == 'ROOT':
                    return self.next_state(t,'INITIAL','BODY')
                else:
                    stack.append(value)
                return
        elif state == 'is':
            if value == 'BEGIN':
                if stack[-1] in ['FUNCTION','PROCEDURE']:
                    return
                elif stack[-1] == 'ROOT':
                    return self.next_state(t,'INITIAL','IS')
                else:
                    stack.append('ANANYMUS_BLOCK')
                    return
            elif value in ['CASE']:
                stack.append(value)
                return
            elif value in ['LOOP','IF']:
                if stack[-1] == 'END':
                    stack.pop()
                    stack.pop()
                else:
                    stack.append(value)
                return
            elif value in ['FUNCTION','PROCEDURE']:
                stack.append(value)
                return
            elif value =='END':
                #print " ",value,stack
                if stack[-1] in ['CASE','FUNCTION','PROCEDURE','ANANYMUS_BLOCK']:
                    stack.pop()
                elif stack[-1] == 'ROOT':
                    return
                else:
                    stack.append(value)
                return
        elif state == 'preprocessing':
            return
        #print "T=",t.__dict__
        return t

    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    class param_class(object):
        def __repr__(self):
            if self.param_type:
                return "%s %s %s"%(self.name,self.param_type,self.data_type)
            else:
                return "%s %s"%(self.name,self.data_type)

    #exprs = []
    def p_expr(self,p):
        'expression : declarations'
        #print "EXPR=%s"%p[1]
        p[0]=p[1]
    def p_optional(self,p):    
        '''
        declarations : 
        param_list :
        param_list_paren :
        param_type :
        two_digit_list :
        default_section :
        '''
    def p_declarations_declare_element(self,p):
        '''
        declarations : declare_element
        param_list : param
        '''
        p[0] = [p[1]]
    def p_declarations_declarations_declare_element(self,p):
        '''
        declarations : declarations declare_element    
        '''
        p[1].append(p[2])
        p[0] = p[1]            

    def p_declare_element(self,p):
        '''
        declare_element : declare_function
                        | variable_def
                        | declare_procedure
                        
        '''#| pragma_macro
        #exprs.append(p[1])
        p[0] = p[1]


    def p_f(self,p):
        '''
        declare_function : FUNCTION ID param_list_paren RETURN datatype IS declarations BEGIN BODY END SEMI
                         | FUNCTION ID param_list_paren RETURN datatype SEMI
        '''
        def repr(self):
            params = "".join(["\n\t%s"%a for a in self.params])
            #params = "\n\t".join("%s"%a for a in self.params)
            return "function %s(%s) return %s"%(self.name,params,self.return_type)
        p[0] = D(p,["type","name","params","return","return_type"],repr)

    def p_proc(self,p):
        '''
        declare_procedure : PROCEDURE ID param_list_paren IS declarations BEGIN BODY END SEMI
                          | PROCEDURE ID param_list_paren SEMI
        '''
        def repr(self):
            params = "".join(["\n\t%s"%a for a in self.params])
            return "procedure %s(%s)"%(self.name,params)
        p[0] = D(p,["type","name","params"],repr)

    def p_param_list_paren(self,p):
        'param_list_paren : LPAREN param_list RPAREN'
        #print "paren=%s"%p[2]
        p[0] = p[2]
    #def p_param_list_param(p):
    #    'param_list : param'
    def p_param_list_param_list(self,p):
        'param_list : param_list COMMA param'
        p[1].append(p[3])
        p[0] = p[1]

    def p_param_type_in_out(self,p):
        'param_type : IN OUT'
        p[0] = 'in out'

    def p_param_type(self,p):
        '''param_type : IN
                      | OUT
        '''
        p[0] = p[1]
    def p_default_section(self,p):
        'default_section : DEFAULT NULL'


    def p_param(self,p):
        'param : ID param_type datatype default_section'
        
        param = self.param_class()
        param.name = p[1]
        param.data_type = p[3]
        param.param_type = p[2]
        p[0] = param

    def p_one_digit_list(self,p):
        'one_digit_list : LPAREN DIGIT RPAREN'
        p[0] = '(' + p[2] + ')'

    def p_two_digit_list_one(self,p):
        'two_digit_list : one_digit_list'
        p[0] = p[1]

    def p_two_digit_list_two(self,p):
        'two_digit_list : LPAREN DIGIT COMMA DIGIT RPAREN'
        p[0] = '(' + p[2] + ',' + p[4] + ')'

    def p_number_type(self,p):
        '''datatype : NUMBER two_digit_list
                    | VARCHAR2 two_digit_list
                    | STRING two_digit_list
                    | RAW one_digit_list
                    | INTERVAL two_digit_list
                    | TIMESTAMP two_digit_list
        '''
        #p[0] = (p[1],p[2])
        if p[2]:
            p[0] = p[1]+p[2]
        else:
            p[0] = p[1]

    def p_oracle_type(self,p):
        '''
        datatype : INTEGER
                 | DATE
                 | BOOLEAN
                 | EXCEPTION
                 | BLOB
                 | CLOB
                 | BFILE
                 | LONG
                 | LONG_RAW
                 | NULL
        '''
        p[0] = p[1]

    def p_user_data_type(self,p):
        'datatype : LBRACKET ID RBRACKET'
        p[0] = p[2]
    def p_user_data_type_ref(self,p):
        'datatype : REF LBRACKET ID RBRACKET'
        p[0] = "ref " + p[3]
    def p_user_data_type_variable(self,p):
        'datatype : variable'
        p[0] = 'VAR:' + p[1]
    def p_variable(self,p):
        'variable : ID'
        p[0] = p[1]
        


    def p_variable_defination(self,p):
        'variable_def : ID datatype SEMI'
        p[0] = 'variable %s of %s'%(p[1],p[2])

    #def p_pragma_macro(self,p):
    #    'pragma_macro : PRAGMA MACRO LPAREN ID COMMA INLINE_STRING COMMA SUBSTITUTE RPAREN SEMI'
    #    p[0] = D(p,["pragma","macro","LP","name","comma","string"],lambda self:"macros %s = %s"%(self.name,self.string))
        #print "lexdata=",self.lexer.lexdata

    def p_error(self,p):
        print "Syntax error in input!"


