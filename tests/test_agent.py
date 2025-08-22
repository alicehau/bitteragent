import asyncio

from bitteragent.agent import Agent
from bitteragent.tools import ToolRegistry
from bitteragent.native_tools.shell import ShellTool
from bitteragent.providers.base import Provider


class DummyProvider(Provider):
    """Provider that first requests a shell tool then returns text."""

    def __init__(self) -> None:
        self.step = 0

    async def complete(self, messages, tools=None):  # type: ignore[override]
        if self.step == 0:
            self.step += 1
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "shell",
                        "id": "1",
                        "input": {"command": "echo hello"},
                    }
                ]
            }
        return {"content": [{"type": "text", "text": "done"}]}


def test_shell_tool_execution():
    tool = ShellTool()
    result = asyncio.run(tool.execute(command="echo test"))
    assert result.success
    assert result.output.strip() == "test"


def test_agent_tool_loop():
    registry = ToolRegistry()
    registry.register(ShellTool())
    agent = Agent(provider=DummyProvider(), registry=registry)
    output = asyncio.run(agent.run("run shell"))
    assert output == "done"
