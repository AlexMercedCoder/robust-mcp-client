import typer
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from core.chat_engine import ChatEngine

app = typer.Typer()
console = Console()

async def chat_loop():
    engine = ChatEngine()
    await engine.initialize()
    
    console.print("[bold green]Robust MCP Client[/bold green]")
    console.print("Type 'exit' or 'quit' to leave.")
    
    try:
        while True:
            user_input = typer.prompt("You")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            with Live(console=console, refresh_per_second=10) as live:
                response_text = ""
                async for chunk in engine.chat(user_input):
                    response_text += chunk
                    live.update(Markdown(response_text))
            
            console.print() # Newline
            
    finally:
        await engine.cleanup()

@app.command()
def chat():
    """
    Start a chat session.
    """
    asyncio.run(chat_loop())

@app.command()
def serve():
    """
    Start the Web UI server.
    """
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    app()
