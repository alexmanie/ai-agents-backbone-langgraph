import gradio as gr
from fastapi import FastAPI

from utils.call_api import CallApi

app = FastAPI()

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("Agente"):
            with gr.Row() as row_one:
                chatbot = gr.Chatbot(
                    [],
                    elem_id="chatbot",
                    bubble_full_width=False,
                    height=500
                )
                
                outout_txt = gr.Textbox(
                    placeholder="Output text",
                    container=False,
                    interactive=False,
                    autoscroll=True,
                    lines=24
                )

            with gr.Row() as row_two:
                input_txt = gr.Textbox(
                    placeholder="Enter text and press enter",
                    container=False,
                    interactive=True,
                )

            with gr.Row() as row_three:
                text_submit_btn = gr.Button(value="Submit text")
                clear_button = gr.ClearButton([input_txt, chatbot])

            with gr.Row() as row_four:
                # lbl_last_call_tokens = gr.Label(label="Call tokens", elem_id="lbl_last_call_tokens")
                lbl_conversation_id = gr.Label(label="conversation", elem_id="lbl_conversation_id")
                lbl_total_tokens = gr.Label(label="Total tokens", elem_id="lbl_total_tokens")

            ##############
            # Process:
            ##############
            input_txt.submit(fn=CallApi.chat, inputs=[chatbot, input_txt, lbl_conversation_id], outputs=[input_txt, chatbot, lbl_conversation_id, outout_txt], queue=False)
            text_submit_btn.click(fn=CallApi.chat, inputs=[chatbot, input_txt, lbl_conversation_id], outputs=[input_txt, chatbot, lbl_conversation_id, outout_txt], queue=False)
            # lbl_last_call_tokens.change(fn=UIUtils.accumulate_totals, inputs=[lbl_last_call_tokens, lbl_total_tokens], outputs=[lbl_total_tokens])

demo.title = "Agente IA - UI"
# app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    demo.launch()
