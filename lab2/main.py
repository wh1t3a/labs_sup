import re
from typing import List, Union, Any

# Определение типа для нашего AST (Abstract Syntax Tree)
# Это может быть строка (атом) или список других атомов/списков
AST = Union[str, List['AST']]


class MiniLispToPython:
    """
    Класс-транслятор.
    Преобразует S-выражения (Lisp-like) в валидный код Python.
    """

    def __init__(self):
        self.indent_level = 0

    def tokenize(self, code: str) -> List[str]:

        # Экранируем скобки пробелами и разбиваем
        formatted = code.replace('(', ' ( ').replace(')', ' ) ')
        return formatted.split()

    def parse(self, tokens: List[str]) -> AST:

        if not tokens:
            raise SyntaxError("Неожиданный конец программы")

        token = tokens.pop(0)

        if token == '(':
            sub_ast = []
            # Пока не встретим закрывающую скобку, парсим рекурсивно
            while tokens[0] != ')':
                sub_ast.append(self.parse(tokens))
            tokens.pop(0)  # Удаляем закрывающую ')'
            return sub_ast
        elif token == ')':
            raise SyntaxError("Неожиданная закрывающая скобка")
        else:
            return token  # Это атом (число, строка или идентификатор)

    def translate_node(self, node: AST) -> str:
        """
        Генерация кода: рекурсивно превращает узел AST в строку Python кода.
        Здесь мы используем match/case (Python 3.10+) для обработки конструкций.
        """
        # Если узел - это просто строка (число или переменная), возвращаем как есть
        if isinstance(node, str):
            return node

        if not node:
            return ""

        # Lisp: (operator arg1 arg2 ...)
        operator = node[0]
        args = node[1:]

        match operator:
            # 1. Арифметика и сравнение (Префикс -> Инфикс)
            # Lisp: (+ 1 2) -> Python: (1 + 2)
            case '+' | '-' | '*' | '/' | '>' | '<' | '==' as op:
                translated_args = [self.translate_node(arg) for arg in args]
                # Оборачиваем в скобки для сохранения приоритета операций
                return f"({f' {op} '.join(translated_args)})"

            # 2. Условное выражение
            # Lisp: (if condition true_branch false_branch)
            # Python: (true_branch if condition else false_branch)
            case 'if':
                if len(args) != 3:
                    raise ValueError(f"Operator 'if' requires 3 arguments, got {len(args)}")
                cond = self.translate_node(args[0])
                true_val = self.translate_node(args[1])
                false_val = self.translate_node(args[2])
                return f"({true_val} if {cond} else {false_val})"

            # 3. Вывод на экран
            # Lisp: (print val) -> Python: print(val)
            case 'print':
                translated_args = [self.translate_node(arg) for arg in args]
                return f"print({', '.join(translated_args)})"

            # Поддержка вложенных списков без операторов (редко, но бывает)
            case _:
                # Если функция неизвестна, пробуем вызвать её как функцию Python
                translated_args = [self.translate_node(arg) for arg in args]
                return f"{operator}({', '.join(translated_args)})"

    def compile(self, source_code: str) -> str:
        """
        Основной метод: Токенизация -> Парсинг -> Трансляция
        """
        tokens = self.tokenize(source_code)
        # Обрабатываем список выражений верхнего уровня
        python_code_lines = []

        while tokens:
            ast = self.parse(tokens)
            python_line = self.translate_node(ast)
            python_code_lines.append(python_line)

        return "\n".join(python_code_lines)


# --- Демонстрация работы ---

if __name__ == "__main__":
    lisp_code = """
    (print "Результат вычислений:")
    (print (+ 10 (* 2 5)))
    (print (if (> 10 5) "Больше" "Меньше"))
    """

    translator = MiniLispToPython()

    print(f"{'=' * 10} Исходный код (Lisp-subset) {'=' * 10}")
    print(lisp_code.strip())

    print(f"\n{'=' * 10} Трансляция в Python {'=' * 10}")
    try:
        py_code = translator.compile(lisp_code)
        print(py_code)

        print(f"\n{'=' * 10} Выполение полученного кода {'=' * 10}")
        exec(py_code)

    except Exception as e:
        print(f"Ошибка трансляции: {e}")
