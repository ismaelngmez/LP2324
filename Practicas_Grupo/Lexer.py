# coding: utf-8

from sly import Lexer
import os
import re
import sys





class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST,ASSIGN, TYPEID,
            ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
            INHERITS, ISVOID, LET, LOOP, NEW, OF,
            POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ERROR,COMMENT_1LINEA}
    #ignore = '\t '
    literals = {'==', '+', '-', '*', '/', '(', ')', '<', '>', '.',' ' ,';', ':', '@', ',','{', '}', '[', ']', '~'}
    # Ejemplo
    INT_CONST   = r'\d+'
    LE          = r'[<][=]'
    DARROW      = r'[=][>]'
    ASSIGN      = r'[<][-]'
    IF          = r'\b[iI][fF]\b'
    FI          = r'\b[fF][iI]\b'
    THEN        = r'\b[tT][hH][eE][nN]\b'
    NOT         = r'\b[nN][oO][tT]\b'
    IN          = r'\b[iI][nN]\b'
    CASE        = r'\b[cC][aA][sS][eE]\b'
    ELSE        = r'\b[eE][lL][sS][eE]\b'
    ESAC        = r'\b[eE][sS][aA][cC]\b'
    CLASS       = r'\b[cC][lL][aA][sS][sS]\b'
    INHERITS    = r'\b[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    ISVOID      = r'\b[iI][sS][vV][oO][iI][dD]\b'
    LET         = r'\b[lL][eE][tT]\b'
    LOOP        = r'\b[lL][oO][oO][pP]\b'
    NEW         = r'\b[nN][eE][wW]\b'
    OF          = r'\b[oO][fF]\b'
    POOL        = r'\b[pP][oO][oO][lL]\b'
    WHILE       = r'\b[wW][hH][iI][lL][eE]\b'

    CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                        for i in ['0', '1']
                        for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]

    @_(r'\b[t][rR][uU][eE]|[f][aA][lL][sS][eE]\b')
    def BOOL_CONST(self, t):
        t.type = 'BOOL_CONST'
        if t.value[0] == 't':
            t.value = True
        elif t.value[0] == 'f':
            t.value = False
        return t
    
    @_('[A-Z]([a-zA-Z0-9_])*')
    def TYPEID(self, t):
        return t

    @_(r'[a-z]([a-zA-Z0-9_])*')
    def OBJECTID(self, t):
        return t
    
    

    
    @_(r'[_]|[!]|[#]|[$]|[%]|[&]|[>]|[?]|[`]|[[]|[]]|[\\]|[|]|[\^]|[\\x*[a-zA-Z0-9]+]|[]|[]|[]|[]')
    def ERROR(self, t):
        t.type = 'ERROR'
        if t.value == '\\':
            t.value = '\\\\'
        elif t.value in self.CARACTERES_CONTROL:
            t.value = f'\\{t.value}'
        return t
    
    @_(r'--.*')
    def COMENT_1LINEA(self, t):
        pass

    @_(r"\s")
    def spaces(self, t):
        pass

    @_(r'"')
    def STR_CONST(self, t):
        self.begin(StringLexer)

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    
    def error(self, t):
        self.index += 1

    def salida(self, texto):
        lexer = CoolLexer()
        list_strings = []
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\' '
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings

class StringLexer(Lexer):
    tokens = {STR_CONST, ERROR}
    _acumulado = ""

    @_(r'\\\n')
    def SALTOESCAPADO(self, t):
        self._acumulado += "\\n"
        self.lineno += 1
    
    @_(r'\\[btrn"]')
    def caracter_escapado1(self, t):
        self._acumulado += t.value[1]
    
    @_(r'\\\\')
    def DOBLE_BARRA(self, t):
        self._acumulado += t.value[0:]

    @_(r'\t')
    def TABULADORESCAPADO(self, t):
        self._acumulado += '\\t'
    
    @_(r'\\.') # El punto no representa el salto de linea
    def COMILLASESCAPADO(self, t):
        self._acumulado += t.value

    @_(r'"')
    def CIERRE(self, t):
        t.type = "STR_CONST"
        t.value = self._acumulado
        self._acumulado = ""
        self.begin(CoolLexer)
        return t

    @_(r'.')
    def CUALQUIER_COSA(self, t):
        self._acumulado += t.value
    
    def error(self, t):
        self.index += 1


    

