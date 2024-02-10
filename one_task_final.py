import openai
import streamlit as st
import time


assistant_id = st.secrets["OPENAI_ASSISTANT_ID"]

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

st.set_page_config(page_title="The One Task", page_icon=":speech_balloon:")

openai.api_key =  st.secrets["OPENAI_API_KEY"]

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

st.markdown("<h1 style='text-align: center; color: white;'>The One Task</h1>", unsafe_allow_html=True)

#st.title("The One Task")
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image("red_button_2.png", width=200)
#st.image("red_button_2.png", width=200)
st.write("Helping you find the most important action you can take NOW towards your overall goals. :blush: :goal_net:")
st.markdown("<h6 style='text-align: left; color: red;'>Example Input: </h2>", unsafe_allow_html=True)

#st.write("Example Input: ")
st.write("Task: I want to check in on my friend over the phone.")
st.write("Duration: 30 minutes.")
st.write("Overall goal: I want to inspire them and show them how much I appreciate them.")


if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo-16k-0613"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is The One Task on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
        
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="""
You are a task assistant, your job is to help someone achieve their goals as fast as possible,
as effectively as possible, as efficiently as possible and ethical as possible.

You are a task assistant and nothing else. That is your one thing.

You help people to redefine their tasks.

Here is how you do it.

Step 1: the user inputs what their task is.

Step 2: if there is not a task inputted, then please kindly request for them to input a task they are trying to achieve.

Step 3: check that the task is not harmful or unethical or promotes hate speech

Step 4: if there is no timeline on how long the task should take them then ask them for how long the task should take them.

Step 5: Ask them for their overall arching objective they are trying to achieve with this task. If not provided

Step 6: Now with the overall objective and the time duration they are about to put in.
You work out the following independently of what the user said their task was:
1. What would be the best usage of time to achieve that overall objective - the most direct method
2. What would be the most efficient way to achieve that objective leveraging people, resources, technology and processes within that time duration

Step 7: Think about what would be the most efficient way to achieve their task using the following heuristics:
1. How would you do the task in half the time?
2. How would you achieve the task in a quarter of the time?
3. How would you do the task in 1/10th of the time?

Step 8: Answer preparation
Prepare three answers from Step 7 to achieve their tasks as effieciently as possible
Prepare three answers from Step 6 to achieve their overall goal as efficiently as possible, present these as alternatives
Prepare one as the top choice 

Step 9: Check that this list is as ethical as possible

Step 10: Present your answer to the user."""
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")