import random
from typing import Tuple


def random_math_question() -> Tuple[str, int]:
    a = random.randint(2, 9)
    b = random.randint(2, 9)
    op = random.choice(["+", "*"])
    if op == "+":
        return f"¿Cuánto es {a} + {b}?", a + b
    return f"¿Cuánto es {a} x {b}?", a * b


def random_trivia_question() -> Tuple[str, str]:
    questions = [
        ("¿Capital de Francia?", "paris"),
        ("¿Color del cielo despejado?", "azul"),
        ("¿Cuántos días tiene una semana?", "7"),
    ]
    return random.choice(questions)


def next_question() -> Tuple[str, str]:
    if random.random() < 0.6:
        q, ans = random_math_question()
    else:
        q, ans = random_trivia_question()
    return q, str(ans).strip().lower()
