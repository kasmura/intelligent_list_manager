from list_interact_tools import tools
from openai import OpenAI
import os
import time
from json import loads as json_loads
from lists_management_datastructure import *

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY)
OPENAI_ASSISTANT_ID = None 

import os
import shlex

def speak(text, rate=350):
    safe_text = shlex.quote(text)
    os.system(f'say -r {rate} {safe_text}')


#print('tools', tools)
if OPENAI_ASSISTANT_ID is None:
    #print('No assitant id yet')
    assistant = openai_client.beta.assistants.create(
        name="List interactor",
        instructions="You are a helpful assistant that helps the user make and edit lists. You have access to functional calls that allow you to make and see lists, add and delete and edit items. You have a tendency to make lists. If the user mentions something you always see whether there might be a relevant list to check, update or create, you don't even ask you just do it. Unless you know for sure which list name is approriate you always check which lists are already created. You usually dont show the snake case names of the lists to the user you usually present them in some more readable way.",
        tools=tools,
        model="gpt-4-1106-preview"
    )
    #print(assistant)
    OPENAI_ASSISTANT_ID = assistant.id

assistant_thread = openai_client.beta.threads.create()
#print('thread', assistant_thread)

all_thread_msg_ids = []

def terminal_interaction():
    while True:
        user_input = input('user > ')
        if user_input.lower() == 'exit':
            print("Exiting the program.")
            break
        else:
            # Process the input and give a response
            response = process_input(user_input)


def respond_to_thread_action(run):
    while run.status != "completed" and run.status != "requires_action":
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=assistant_thread.id,
            run_id=run.id
        )
        time.sleep(0.1)
    if run.status == 'completed':
        new_messages = openai_client.beta.threads.messages.list(
            thread_id=assistant_thread.id
        )
        new_std_outs = []
        for thread_message in new_messages.data:
            if thread_message.id in all_thread_msg_ids: continue
            all_thread_msg_ids.append(thread_message.id)
            for context_text in thread_message.content:
                new_std_outs.append((thread_message.role, context_text.text.value))
        new_std_outs.reverse()
        for role, value in new_std_outs:
            if role == 'assistant':
                print(role, '>', value)
    elif run.status == 'requires_action':
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        function_call_outputs = []
        for tool_call in tool_calls:
            tool_call_arguments = json_loads(tool_call.function.arguments)
            if tool_call.function.name == 'make_empty_list':
                assert 'list_name' in tool_call_arguments, "Error in make_empty_list"
                function_call_output = make_empty_list(tool_call_arguments['list_name'])
            elif tool_call.function.name == 'see_all_list_names':
                function_call_output = see_all_list_names()
            elif tool_call.function.name == 'see_all_items_in_list':
                function_call_output = see_all_items_in_list(tool_call_arguments['list_name'])
            elif tool_call.function.name == 'add_element':
                function_call_output = add_element(tool_call_arguments['list_name'], tool_call_arguments['item_name'])
            elif tool_call.function.name == 'edit_element':
                function_call_output = edit_element(tool_call_arguments['list_name'], tool_call_arguments['item_index'], tool_call_arguments['new_name'])
            elif tool_call.function.name == 'delete_element':
                function_call_output = delete_element(tool_call_arguments['list_name'], tool_call_arguments['item_index'])
            else:
                raise Exception('Unknown function name', tool_call)
            print('tool use > ', tool_call.function.name)
            print('\t Input: ', tool_call_arguments)
            print('\t Output: ', function_call_output)
            function_call_outputs.append({
                'output':function_call_output,
                'tool_call_id':tool_call.id
            })
        submit_obj = openai_client.beta.threads.runs.submit_tool_outputs(
            run_id = run.id,
            thread_id = assistant_thread.id,
            tool_outputs = function_call_outputs)
        respond_to_thread_action(submit_obj)
    else:
        print('run status', run.status)

def process_input(user_input):
    openai_client.beta.threads.messages.create(
            thread_id=assistant_thread.id,
            role="user",
            content=user_input
    )
    run_obj = openai_client.beta.threads.runs.create(
                thread_id=assistant_thread.id,
                assistant_id=assistant.id
    )
    respond_to_thread_action(run_obj)
    #return f"You said: {user_input}"

terminal_interaction()