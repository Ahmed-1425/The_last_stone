# nim_core.py
import random
import math
from typing import List, Tuple, Dict
from collections import deque

# ===================== أساسيات لعبة Nim =====================

def is_terminal(piles: List[int]) -> bool:
    """ترجع True إذا انتهت اللعبة (كل الأكوام = 0)."""
    return all(p == 0 for p in piles)

def generate_moves(piles: List[int]) -> List[Tuple[int, int]]:
    """
    توليد جميع الحركات الممكنة من حالة معيّنة.
    كل حركة عبارة عن (index, remove)
    index = رقم الكومة
    remove = عدد الأحجار التي سيتم إزالتها من هذه الكومة
    """
    moves: List[Tuple[int, int]] = []
    for i, p in enumerate(piles):
        for r in range(1, p + 1):
            moves.append((i, r))
    return moves

def apply_move(piles: List[int], move: Tuple[int, int]) -> List[int]:
    """تنفيذ حركة معينة على نسخ من الأكوام."""
    i, r = move
    new_piles = piles[:]
    new_piles[i] -= r
    return new_piles

def piles_key(piles: List[int]) -> Tuple[int, ...]:
    """
    مفتاح للحالة لتقليل التكرار في الـ memoization.
    نرتب الأكوام تنازلياً لأن ترتيبها ما يهم في Nim.
    """
    return tuple(sorted(piles, reverse=True))

# ===================== Minimax + Alpha-Beta =====================

def minimax(piles: List[int],
            maximizing: bool,
            alpha: int,
            beta: int,
            memo: Dict[Tuple[Tuple[int, ...], bool], int]) -> int:
    """
    خوارزمية Minimax مع تقليم Alpha-Beta.

    ترجع:
        +1  → فوز للـ AI (اللاعب الأعظمي)
        -1  → فوز للإنسان (اللاعب التصغري)
         0  → تعادل (نادر في Nim القياسية)

    parameters:
        piles      : حالة الأكوام الحالية
        maximizing : True إذا كان دور الـ AI، False إذا كان دور الإنسان
        alpha/beta : حدود التقليم
        memo       : قاموس لتخزين نتائج الحالات (memoization)
    """
    key = (piles_key(piles), maximizing)
    if key in memo:
        return memo[key]

    # حالة نهائية
    if is_terminal(piles):
        # اللاعب الذي عليه الدور الآن لا يستطيع اللعب → خاسر
        val = -1 if maximizing else +1
        memo[key] = val
        return val

    if maximizing:
        value = -math.inf
        for move in generate_moves(piles):
            child = apply_move(piles, move)
            score = minimax(child, False, alpha, beta, memo)
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        memo[key] = value
        return value
    else:
        value = math.inf
        for move in generate_moves(piles):
            child = apply_move(piles, move)
            score = minimax(child, True, alpha, beta, memo)
            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha:
                break
        memo[key] = value
        return value

def best_move_minimax(piles: List[int]) -> Tuple[int, int]:
    """
    اختيار أفضل حركة للـ AI باستخدام Minimax.
    ترجع (index, remove)
    """
    memo: Dict[Tuple[Tuple[int, ...], bool], int] = {}
    best_value = -math.inf
    best_moves: List[Tuple[Tuple[int, int], int]] = []

    for move in generate_moves(piles):
        child = apply_move(piles, move)
        score = minimax(child, False, -math.inf, math.inf, memo)
        if score > best_value:
            best_value = score
            best_moves = [(move, score)]
        elif score == best_value:
            best_moves.append((move, score))

    # لو فيه أكثر من حركة بنفس القيمة، نختار واحدة عشوائية
    move, _ = random.choice(best_moves)
    return move

# ===================== BFS Strategy =====================

def best_move_bfs(piles: List[int], max_depth: int = 4) -> Tuple[int, int]:
    """
    استراتيجية ثانية تعتمد على BFS (Breadth-First Search).

    تبحث في شجرة الحالات مستوى مستوى حتى عمق max_depth.
    إذا وُجد مسار يفوز فيه الـ AI خلال هذا العمق، نرجّع أول حركة في هذا المسار.
    إذا لم يُوجد، نرجع حركة عشوائية من الحركات المتاحة.

    مفيدة لشرح الفرق بين بحث موجّه (Minimax) وبحث غير موجّه (BFS).
    """
    initial_state = (tuple(piles), True)  # (state, is_ai_turn)
    queue = deque()
    queue.append((initial_state, []))  # ((state, turn), path_of_moves)
    visited = {initial_state}

    while queue:
        (state, is_ai_turn), path = queue.popleft()
        current_piles = list(state)

        # عدد حركات الـ AI في هذا المسار
        ai_moves_count = sum(1 for m in path if isinstance(m, tuple))
        if ai_moves_count > max_depth:
            continue

        # حالة نهائية
        if is_terminal(current_piles):
            # إذا الدور الحالي هو الإنسان → هذا يعني أن الـ AI لعب آخر مرة وفاز
            if not is_ai_turn:
                for m in path:
                    if isinstance(m, tuple):
                        return m
            continue

        # توسعة العقدة الحالية
        if is_ai_turn:
            for move in generate_moves(current_piles):
                child_piles = apply_move(current_piles, move)
                child_state = (tuple(child_piles), False)
                if child_state not in visited:
                    visited.add(child_state)
                    queue.append((child_state, path + [move]))
        else:
            # حركات الإنسان، نضيفها للمسار بعلامة "H" (للفصل عن حركات الـ AI)
            for move in generate_moves(current_piles):
                child_piles = apply_move(current_piles, move)
                child_state = (tuple(child_piles), True)
                if child_state not in visited:
                    visited.add(child_state)
                    queue.append((child_state, path + [("H", move)]))

    # إذا لم نجد مسار فوز واضح، نرجع حركة عشوائية بسيطة
    return random.choice(generate_moves(piles))