"""
app.py — Gradio web interface for the UNCC Elective Finder.

Run: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from generate import ask


def handle_query(question: str) -> tuple[str, str]:
    if not question.strip():
        return "Please enter a question.", ""

    try:
        result = ask(question)
        answer = result["answer"]
        sources = "\n".join(f"• {s}" for s in result["sources"]) or "No sources retrieved."
        return answer, sources
    except Exception as e:
        return f"Error: {e}", ""


with gr.Blocks(title="UNCC Elective Finder") as demo:
    gr.Markdown(
        """
        # UNCC Elective Finder
        Ask questions about courses, professors, and electives at UNC Charlotte.
        Answers are grounded in real student discussions from r/UNCCharlotte.
        """
    )

    with gr.Row():
        question_box = gr.Textbox(
            label="Your question",
            placeholder=(
                "e.g. What are easy electives at UNCC? "
                "Which professors do students recommend? "
                "What satisfies the writing requirement?"
            ),
            lines=2,
            scale=4,
        )
        submit_btn = gr.Button("Ask", variant="primary", scale=1)

    with gr.Row():
        answer_box = gr.Textbox(
            label="Answer (from student discussions)",
            lines=12,
            scale=3,
        )
        sources_box = gr.Textbox(
            label="Source threads (r/UNCCharlotte)",
            lines=12,
            scale=2,
        )

    submit_btn.click(handle_query, inputs=question_box, outputs=[answer_box, sources_box])
    question_box.submit(handle_query, inputs=question_box, outputs=[answer_box, sources_box])

    gr.Markdown(
        """
        ---
        *Answers are generated from r/UNCCharlotte student posts.
        Always verify course information with your advisor or the official UNCC course catalog.*
        """
    )

if __name__ == "__main__":
    demo.launch()
