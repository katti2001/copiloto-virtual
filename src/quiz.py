import random
from typing import Tuple, List


QUESTIONS: List[Tuple[str, str, int]] = []


def _generate_questions():
    global QUESTIONS
    QUESTIONS = []
    
    for a in range(1, 11):
        for b in range(1, 11):
            if a + b <= 20:
                QUESTIONS.append((f"Cuanto es {a} mas {b}", a + b))
            if a - b >= 1:
                QUESTIONS.append((f"Cuanto es {a} menos {b}", a - b))
    
    random.shuffle(QUESTIONS)


_generate_questions()
_q_index = 0


def get_question() -> Tuple[str, str]:
    global _q_index
    if _q_index >= len(QUESTIONS):
        _generate_questions()
        _q_index = 0
    
    q, answer = QUESTIONS[_q_index]
    _q_index += 1
    return q, str(answer)


def check_answer(response: str, correct: str) -> bool:
    if not response:
        return False
    
    try:
        if float(response) == float(correct):
            return True
    except:
        pass
    
    resp_clean = ''.join(c for c in response.lower() if c.isdigit() or c == '-')
    try:
        if float(resp_clean) == float(correct):
            return True
    except:
        pass
    
    return False
