import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import ollama

SYSTEM_PROMPT = """
You are a personal finance assistant with access to tools that read real transaction data.
You MUST call the appropriate tool before answering ANY financial question.
NEVER invent, estimate, or guess financial figures under any circumstances.
When a tool returns results, present them EXACTLY and VERBATIM to the user. Do not summarise, reformat, or replace the tool output.
Do not mention knowledge cutoff dates — your data comes from tools, not your training data.
If you cannot find the right tool for a question, say so honestly.
Never show raw JSON or code blocks in your response. Present tool results in plain conversational text only.
Always convert relative time references like 'last month', 'this month', or 'this year' into the actual month name before calling any tool. The data available is from January 2024 and February 2024.
"""

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in tools_result.tools
            ]

            conversation_history = []
            print("Finance Assistant ready. Type 'quit' to exit.")

            while True:
                user_input = input("\nYou: ")
                
                if user_input.lower() == "quit":
                    break
                
                conversation_history.append({
                    "role": "user",
                    "content": user_input
                })

                response = ollama.chat(
                    model="llama3.1",
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
                    tools=tools
                )

                if response.message.tool_calls:
                    for tool_call in response.message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = tool_call.function.arguments
                        
                        tool_result = await session.call_tool(tool_name, tool_args)
                        
                        conversation_history.append({
                            "role": "tool",
                            "content": str(tool_result.content[0].text)
                        })
                        
                        final_response = ollama.chat(
                            model="llama3.1",
                            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
                            tools=tools
                        )
                        
                        print(f"\nAssistant: {final_response.message.content}")
                        conversation_history.append({
                            "role": "assistant",
                            "content": final_response.message.content
                        })

                else:
                    print(f"\nAssistant: {response.message.content}")
                    conversation_history.append({
                        "role": "assistant",
                        "content": response.message.content
                    })
asyncio.run(main())