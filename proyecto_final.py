import json
import os

# -------------------------------------------------
# Proyecto 01 - Teoría de la Computación
# Analizador Sintáctico LL(1) para Expresiones Aritméticas
# -------------------------------------------------

# --- DEFINICIÓN DE CONSTANTES Y TOKENS ---
TOKEN_NUM = 'NUM'
TOKEN_ID = 'ID'
TOKEN_PLUS = 'PLUS'
TOKEN_MINUS = 'MINUS'
TOKEN_MUL = 'MUL'
TOKEN_DIV = 'DIV'
TOKEN_MOD = 'MOD'
TOKEN_LPAREN = 'LPAREN'
TOKEN_RPAREN = 'RPAREN'
TOKEN_EOF = '$'  # Fin de archivo
TOKEN_EPSILON = 'ε' # Epsilon (vacío)

# --- CLASE TOKEN ---
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

# --- CLASE LEXER (ANALIZADOR LÉXICO) ---
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return Token(TOKEN_NUM, float(result))

    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(TOKEN_ID, result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            if self.current_char.isdigit():
                return self.number()
            if self.current_char == '+':
                self.advance()
                return Token(TOKEN_PLUS, '+')
            if self.current_char == '-':
                self.advance()
                return Token(TOKEN_MINUS, '-')
            if self.current_char == '*':
                self.advance()
                return Token(TOKEN_MUL, '*')
            if self.current_char == '/':
                self.advance()
                return Token(TOKEN_DIV, '/')
            if self.current_char == '%':
                self.advance()
                return Token(TOKEN_MOD, '%')
            if self.current_char == '(':
                self.advance()
                return Token(TOKEN_LPAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(TOKEN_RPAREN, ')')
            
            raise Exception(f'Error léxico: Caracter no válido "{self.current_char}"')
        return Token(TOKEN_EOF, None)

# --- DEFINICIÓN DE LA GRAMÁTICA ---
# Gramática sin recursión por la izquierda
# E  -> T E'
# E' -> + T E' | - T E' | ε
# T  -> F T'
# T' -> * F T' | / F T' | % F T' | ε
# F  -> ( E ) | num | id

GRAMMAR = {
    'E': [['T', "E'"]],
    'E\'': [['PLUS', 'T', "E'"], ['MINUS', 'T', "E'"], [TOKEN_EPSILON]],
    'T': [['F', "T'"]],
    'T\'': [['MUL', 'F', "T'"], ['DIV', 'F', "T'"], ['MOD', 'F', "T'"], [TOKEN_EPSILON]],
    'F': [['LPAREN', 'E', 'RPAREN'], ['NUM'], ['ID']]
}

START_SYMBOL = 'E'
TERMINALS = {TOKEN_NUM, TOKEN_ID, TOKEN_PLUS, TOKEN_MINUS, TOKEN_MUL, 
            TOKEN_DIV, TOKEN_MOD, TOKEN_LPAREN, TOKEN_RPAREN, TOKEN_EOF}
NON_TERMINALS = set(GRAMMAR.keys())

# --- ALGORITMOS GENERADORES (FIRST, FOLLOW, TABLA) ---

def calculate_first_sets(grammar, non_terminals):
    """Calcula el conjunto First de forma iterativa."""
    first_sets = {nt: set() for nt in non_terminals}
    
    while True:
        changed = False
        for nt in non_terminals:
            for production in grammar[nt]:
                for symbol in production:
                    # Caso 1: Terminal
                    if symbol in TERMINALS:
                        if symbol not in first_sets[nt]:
                            first_sets[nt].add(symbol)
                            changed = True
                        break 
                    # Caso 2: Epsilon
                    elif symbol == TOKEN_EPSILON:
                        if TOKEN_EPSILON not in first_sets[nt]:
                            first_sets[nt].add(TOKEN_EPSILON)
                            changed = True
                        continue
                    # Caso 3: No-Terminal
                    elif symbol in non_terminals:
                        first_of_symbol = first_sets[symbol]
                        added_new = first_of_symbol - {TOKEN_EPSILON}
                        if not added_new.issubset(first_sets[nt]):
                            first_sets[nt].update(added_new)
                            changed = True
                        if TOKEN_EPSILON not in first_of_symbol:
                            break
                else:
                    # Si llegamos aquí, todos eran anulables (podían ser epsilon)
                    if TOKEN_EPSILON not in first_sets[nt]:
                        first_sets[nt].add(TOKEN_EPSILON)
                        changed = True
        if not changed:
            break
    return first_sets

def calculate_follow_sets(grammar, start_symbol, first_sets):
    """Calcula el conjunto Follow de forma iterativa."""
    follow_sets = {nt: set() for nt in NON_TERMINALS}
    follow_sets[start_symbol].add(TOKEN_EOF) 

    while True:
        changed = False
        for nt in NON_TERMINALS:
            for production in grammar[nt]:
                for i in range(len(production)):
                    symbol = production[i]
                    if symbol in NON_TERMINALS:
                        beta = production[i+1:]
                        if beta:
                            # Calcular First(beta)
                            first_of_beta = set()
                            for s in beta:
                                first_of_s = first_sets[s] if s in NON_TERMINALS else {s}
                                first_of_beta.update(first_of_s - {TOKEN_EPSILON})
                                if TOKEN_EPSILON not in first_of_s:
                                    break
                            else:
                                # Si beta es anulable, añadir Follow(A) a Follow(B)
                                if not follow_sets[nt].issubset(follow_sets[symbol]):
                                    follow_sets[symbol].update(follow_sets[nt])
                                    changed = True
                            
                            if not first_of_beta.issubset(follow_sets[symbol]):
                                follow_sets[symbol].update(first_of_beta)
                                changed = True
                        else:
                            # Producción A -> alpha B
                            if not follow_sets[nt].issubset(follow_sets[symbol]):
                                follow_sets[symbol].update(follow_sets[nt])
                                changed = True
        if not changed:
            break
    return follow_sets

def build_ll1_table(grammar, first_sets, follow_sets):
    """Construye la tabla de análisis sintáctico LL(1)."""
    table = {nt: {} for nt in NON_TERMINALS}
    
    for nt in NON_TERMINALS:
        for production in grammar[nt]:
            # Calcular First de la producción actual
            first_of_production = set()
            for symbol in production:
                first_of_symbol = first_sets[symbol] if symbol in NON_TERMINALS else {symbol}
                first_of_production.update(first_of_symbol - {TOKEN_EPSILON})
                if TOKEN_EPSILON not in first_of_symbol:
                    break
            else:
                first_of_production.add(TOKEN_EPSILON)

            # Regla 1: Para cada terminal en First(prod)
            for terminal in first_of_production:
                if terminal != TOKEN_EPSILON:
                    if terminal in table[nt]:
                        print(f"ADVERTENCIA: Conflicto en tabla [{nt}, {terminal}]")
                    table[nt][terminal] = production
            
            # Regla 2: Si epsilon está en First(prod), usar Follow(A)
            if TOKEN_EPSILON in first_of_production:
                for terminal in follow_sets[nt]:
                    table[nt][terminal] = production

    return table

# --- MOTOR DEL PARSER LL(1) ---
class LL1Parser:
    def __init__(self, table, lexer, start_symbol):
        self.table = table
        self.lexer = lexer
        self.start_symbol = start_symbol
        self.current_token = self.lexer.get_next_token()
        self.stack = []
        self.stack.append(TOKEN_EOF)      
        self.stack.append(self.start_symbol) 

    def parse(self):
        print("--- INICIANDO ANÁLISIS SINTÁCTICO (Motor LL(1)) ---")
        print(f"{'PILA':<40} | {'TOKEN ACTUAL':<15} | ACCIÓN")
        print("-" * 70)
        
        while self.stack:
            top_of_stack = self.stack[-1]
            token_type = self.current_token.type
            
            stack_str = str(self.stack)
            
            # Caso 1: Cima es Terminal o EOF
            if top_of_stack in TERMINALS or top_of_stack == TOKEN_EOF:
                if top_of_stack == token_type:
                    print(f"{stack_str:<40} | {token_type:<15} | Match: {token_type}")
                    self.stack.pop()
                    self.current_token = self.lexer.get_next_token()
                else:
                    raise Exception(f"Error de sintaxis: Se esperaba '{top_of_stack}' pero se encontró '{token_type}'")
            
            # Caso 2: Cima es No-Terminal
            elif top_of_stack in NON_TERMINALS:
                try:
                    production = self.table[top_of_stack][token_type]
                    print(f"{stack_str:<40} | {token_type:<15} | Regla: {top_of_stack} -> {' '.join(production)}")
                    self.stack.pop()
                    if production != [TOKEN_EPSILON]:
                        for symbol in reversed(production):
                            self.stack.append(symbol)
                except KeyError:
                    raise Exception(f"Error de sintaxis: No hay regla para [{top_of_stack}, {token_type}]")
            else:
                raise Exception(f"Símbolo desconocido en la pila: {top_of_stack}")

        print("-" * 70)
        return True

# --- UTILIDADES DE ARCHIVO ---
def read_source_file(filename):
    # Crea el archivo si no existe para facilitar la prueba
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("(valor1 + 100) * 2 % 5 - otra_variable / 3")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_to_file(data, filename):
    print(f"Generando archivo: {filename}")
    data_serializable = json.loads(json.dumps(data, default=list))
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data_serializable, f, indent=4)

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == '__main__':
    print("=========================================")
    print("      PROYECTO 01 - COMPILADORES         ")
    print("=========================================")

    # 1. Guardar Gramática
    write_to_file(GRAMMAR, "resultado_gramatica.json")

    # 2. Generar Conjuntos First
    print("\n[Calculando First...]")
    first_sets = calculate_first_sets(GRAMMAR, NON_TERMINALS)
    write_to_file(first_sets, "resultado_conjunto_first.json")

    # 3. Generar Conjuntos Follow
    print("[Calculando Follow...]")
    follow_sets = calculate_follow_sets(GRAMMAR, START_SYMBOL, first_sets)
    write_to_file(follow_sets, "resultado_conjunto_follow.json")

    # 4. Generar Tabla Sintáctica
    print("[Generando Tabla LL(1)...]")
    ll1_table = {}
    try:
        ll1_table = build_ll1_table(GRAMMAR, first_sets, follow_sets)
        write_to_file(ll1_table, "resultado_tabla_sintactica.json")
    except Exception as e:
        print(f"Error Crítico: {e}")
        exit()

    # 5. Ejecutar Parser
    print("\n[Ejecutando Parser con archivo de entrada...]")
    input_filename = "mi_codigo.java"
    input_text = read_source_file(input_filename)
    print(f"Entrada leída: {input_text}\n")

    lexer = Lexer(input_text)
    parser = LL1Parser(ll1_table, lexer, START_SYMBOL)

    try:
        if parser.parse():
            print("\n>>> RESULTADO: El código es SINTÁCTICAMENTE CORRECTO. <<<")
    except Exception as e:
        print(f"\n>>> RESULTADO: ERROR DE SINTAXIS: {e} <<<")