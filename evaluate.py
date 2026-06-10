"""
evaluate.py — Run all 5 evaluation questions and print results.

Output is formatted for pasting directly into README Evaluation Report.
Run: python evaluate.py
"""

from generate import ask

EVAL_QUESTIONS = [
    {
        "n": 1,
        "question": "What GPA booster classes do students recommend at UNCC?",
        "expected": "Specific course names mentioned as easy A's: e.g. GEOG 3180, THEA 1502/LBST 1104, business ethics, film courses, ROTC, LBST geography with Barbara John",
    },
    {
        "n": 2,
        "question": "Which professors do UNCC students recommend for undergraduate courses?",
        "expected": "Names of specific professors with positive comments about teaching style or course difficulty, e.g. John Taylor (Calc 1), Aileen Benedict (ITCS 3162), Morong (THEA)",
    },
    {
        "n": 3,
        "question": "What do UNCC students say about the easiest liberal studies (LBST) courses?",
        "expected": "Mentions of specific LBST courses students found easy: LBST 1104, LBST 2301, geography with Barbara John, or similar",
    },
    {
        "n": 4,
        "question": "What do students say about John Taylor's Calculus 1 class at UNCC?",
        "expected": "Discussion of the hype around John Taylor for Calc 1 — popular among students, specific opinions on his teaching or exam style",
    },
    {
        "n": 5,
        "question": "What is the best sushi restaurant in Charlotte?",  # intentional out-of-scope
        "expected": "System should refuse: 'I don't have enough information in the available student discussions to answer that.'",
    },
]


def run_evaluation():
    for item in EVAL_QUESTIONS:
        n = item["n"]
        q = item["question"]
        expected = item["expected"]

        print(f"\n{'='*70}")
        print(f"Q{n}: {q}")
        print(f"Expected: {expected}")
        print("-" * 70)

        result = ask(q)
        print(f"System response:\n{result['answer']}")
        print(f"\nRetrieved from:")
        for s in result["sources"][:3]:
            print(f"  - {s}")

        print("\n[Chunks retrieved and their distances:]")
        for i, c in enumerate(result["chunks"], 1):
            print(f"  [{i}] dist={c['distance']:.3f} | {c['title'][:55]}")


if __name__ == "__main__":
    run_evaluation()
