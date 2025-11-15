# 🧩 Analizador Sintáctico LL(1)  
Proyecto 01 — Teoría de la Computación  
Python + Tkinter

Este proyecto implementa un **analizador sintáctico LL(1)** para expresiones aritméticas, junto con una **interfaz gráfica** que permite cargar código, visualizar la traza del análisis y consultar la gramática, conjuntos FIRST, FOLLOW y la tabla LL(1).

---

## 🚀 Características Principales

### ✔ Analizador Léxico (Lexer)
Tokeniza expresiones aritméticas con soporte para:
- Identificadores (`variable`, `valor_1`)
- Números enteros y decimales (`123`, `45.6`)
- Operadores: `+`, `-`, `*`, `/`, `%`
- Paréntesis: `(`, `)`

### ✔ Analizador Sintáctico LL(1)
Incluye:
- Eliminación de recursión por la izquierda  
- Gramática sin ambigüedades  
- Cálculo automático de:
  - Conjuntos **FIRST**
  - Conjuntos **FOLLOW**
  - **Tabla de predicción LL(1)**
- Motor LL(1) implementado con pila

### ✔ Interfaz gráfica (Tkinter)
Permite:
- Cargar archivos `.java`
- Ver el código fuente
- Ejecutar el parser paso a paso
- Mostrar la traza completa del análisis
- Abrir archivos JSON generados automáticamente:
  - `resultado_gramatica.json`
  - `resultado_conjunto_first.json`
  - `resultado_conjunto_follow.json`
  - `resultado_tabla_sintactica.json`

---

## 📁 Estructura del Proyecto

