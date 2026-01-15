import llama_index.core.agent
print("llama_index.core.agent content:")
print(dir(llama_index.core.agent))

from llama_index.core.agent import ReActAgent
print("\nReActAgent bases:")
print(ReActAgent.__bases__)
print("\nReActAgent init signature:")
import inspect
print(inspect.signature(ReActAgent.__init__))
