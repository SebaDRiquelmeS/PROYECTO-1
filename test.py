# -------------------------------------------------
# Proyecto 01 - Teoría de la Computación
# Implementación de un Analizador Sintáctico para Expresiones Aritméticas
# -------------------------------------------------

# --- PASO 1: DEFINICIÓN DE TOKENS ---
# Estos son los tipos de "palabras" que nuestro analizador puede reconocer.
# EOF (End-Of-File) marca el final de la entrada.
TOKEN_NUM = 'NUM'      # Números (ej. 10, 3.14)
TOKEN_ID = 'ID'        # Identificadores (ej. variable, resultado)
TOKEN_PLUS = 'PLUS'    # Símbolo de suma '+'
TOKEN_MINUS = 'MINUS'  # Símbolo de resta '-'
TOKEN_MUL = 'MUL'      # Símbolo de multiplicación '*'
TOKEN_DIV = 'DIV'      # Símbolo de división '/'
TOKEN_MOD = 'MOD'      # Símbolo de módulo '%'
TOKEN_LPAREN = 'LPAREN' # Paréntesis izquierdo '('
TOKEN_RPAREN = 'RPAREN' # Paréntesis derecho ')'
TOKEN_EOF = 'EOF'      # Fin de la cadena de entrada

# --- PASO 2: CLASE TOKEN ---
# Un objeto simple para almacenar la información de cada token: su tipo y su valor.
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)})'

# --- PASO 3: LEXER (ANALIZADOR LÉXICO) ---
# Su trabajo es tomar el texto de entrada (código fuente) y dividirlo en una secuencia de tokens.
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        """Avanza el puntero 'pos' y actualiza 'current_char'."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Fin del archivo/texto
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """Salta los espacios en blanco."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Devuelve un número (entero o flotante) consumido de la entrada."""
        result = ''
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return Token(TOKEN_NUM, float(result))

    def identifier(self):
        """Devuelve un identificador."""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return Token(TOKEN_ID, result)

    def get_next_token(self):
        """El corazón del Lexer. Reconoce el próximo token en la entrada."""
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

            # Si no reconoce el caracter, lanza un error.
            raise Exception(f'Error léxico: Caracter no válido "{self.current_char}"')

        # Si se llega al final del texto, devuelve el token EOF.
        return Token(TOKEN_EOF, None)

# --- PASO 4: PARSER (ANALIZADOR SINTÁCTICO) ---
# Implementa la gramática mediante un método para cada no-terminal.
# Este es un analizador de "Descenso Recursivo".
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, expected_type):
        """Lanza un error de sintaxis."""
        raise Exception(f'Error de sintaxis: se esperaba {expected_type}, pero se encontró {self.current_token.type}')

    def eat(self, token_type):
        """
        Consume el token actual si es del tipo esperado.
        Si no, lanza un error.
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(token_type)

    # --- MÉTODOS QUE IMPLEMENTAN LA GRAMÁTICA ---
    # Gramática:
    # E  -> T E'
    # E' -> + T E' | - T E' | ε
    # T  -> F T'
    # T' -> * F T' | / F T' | % F T' | ε
    # F  -> ( E ) | num | id

    def F(self):
        """Regla para F -> ( E ) | num | id"""
        token = self.current_token
        if token.type == TOKEN_LPAREN:
            self.eat(TOKEN_LPAREN)
            self.E()
            self.eat(TOKEN_RPAREN)
        elif token.type == TOKEN_NUM:
            self.eat(TOKEN_NUM)
        elif token.type == TOKEN_ID:
            self.eat(TOKEN_ID)
        else:
            self.error(f'{TOKEN_LPAREN}, {TOKEN_NUM} o {TOKEN_ID}')

    def T_prime(self):
        """Regla para T' -> * F T' | / F T' | % F T' | ε"""
        token = self.current_token
        if token.type == TOKEN_MUL:
            self.eat(TOKEN_MUL)
            self.F()
            self.T_prime()
        elif token.type == TOKEN_DIV:
            self.eat(TOKEN_DIV)
            self.F()
            self.T_prime()
        elif token.type == TOKEN_MOD:
            self.eat(TOKEN_MOD)
            self.F()
            self.T_prime()
        # Si no es ninguno de los anteriores, es la producción ε (vacía),
        # por lo que no hacemos nada.

    def T(self):
        """Regla para T -> F T'"""
        self.F()
        self.T_prime()

    def E_prime(self):
        """Regla para E' -> + T E' | - T E' | ε"""
        token = self.current_token
        if token.type == TOKEN_PLUS:
            self.eat(TOKEN_PLUS)
            self.T()
            self.E_prime()
        elif token.type == TOKEN_MINUS:
            self.eat(TOKEN_MINUS)
            self.T()
            self.E_prime()
        # Si no es ni '+' ni '-', es la producción ε (vacía),
        # por lo que no hacemos nada.

    def E(self):
        """Regla para E -> T E'"""
        self.T()
        self.E_prime()

    def parse(self):
        """
        Punto de entrada del análisis. Comienza con la regla inicial 'E'
        y verifica que al final se llegue al fin de la entrada (EOF).
        """
        print("Iniciando análisis sintáctico...")
        self.E()
        if self.current_token.type != TOKEN_EOF:
            self.error(TOKEN_EOF)
        print("Análisis sintáctico completado con éxito. La cadena es válida.")


# --- PASO 5: EJECUCIÓN PRINCIPAL ---
if __name__ == '__main__':
    # El código fuente que se va a analizar.
    # Puedes cambiar esta línea para probar diferentes expresiones.
    # Este texto simula ser el contenido de un archivo .java
    input_text = "resultado = (valor1 + 100) * 2 % 5 - otra_variable / 3;"
    
    # Ignoramos lo que está fuera de la expresión aritmética para este ejemplo
    # En un compilador real, se analizaría toda la línea.
    expression_to_parse = "(valor1 + 100) * 2 % 5 - otra_variable / 3"

    print(f"Analizando la expresión: '{expression_to_parse}'\n")

    # 1. Crear el analizador léxico (Lexer)
    lexer = Lexer(expression_to_parse)

    # (Opcional) Imprimir todos los tokens para depuración
    print("--- Tokens generados por el Lexer ---")
    temp_lexer = Lexer(expression_to_parse)
    token = temp_lexer.get_next_token()
    while token.type != TOKEN_EOF:
        print(token)
        token = temp_lexer.get_next_token()
    print(token) # Imprime el token EOF
    print("-------------------------------------\n")

    # 2. Crear el analizador sintáctico (Parser)
    parser = Parser(lexer)

    # 3. Iniciar el análisis
    try:
        parser.parse()
    except Exception as e:
        print(f"\nError durante el análisis: {e}")

    print("\n--- Prueba con una expresión inválida ---")
    invalid_expression = "a + * 5"
    print(f"Analizando la expresión: '{invalid_expression}'\n")
    lexer_invalid = Lexer(invalid_expression)
    parser_invalid = Parser(lexer_invalid)
    try:
        parser_invalid.parse()
    except Exception as e:
        print(f"Error detectado correctamente: {e}")
