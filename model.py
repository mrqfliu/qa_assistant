from langchain.llms.base import LLM
from langchain_community.llms.utils import enforce_stop_tokens
from transformers import AutoTokenizer, AutoModel
from typing import List, Optional, Any


# Custom GLM class
class ChatGLM2(LLM):
    max_token: int = 4096
    temperature: float = 0.8
    top_p = 0.9
    tokenizer: object = None
    model: object = None
    history = []

    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "custom_chatglm2"

    # Method to load the model
    def load_model(self, model_path=None):
        # Load the tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True,revision = 'main')
        # Load the model
        self.model = AutoModel.from_pretrained(model_path, trust_remote_code=True,revision = 'main').float()

    # Define the _call method for model inference
    def _call(self,prompt: str, stop: Optional[List[str]] = None) -> str:
        response, _ = self.model.chat(self.tokenizer,
                                        prompt,
                                        history=self.history,
                                        temperature=self.temperature,
                                        top_p=self.top_p)

        if stop is not None:
            response = enforce_stop_tokens(response, stop)

        self.history = self.history + [[None, response]]
        return response

if __name__ == '__main__':
    llm = ChatGLM2()
    llm.load_model(model_path='./chatglm-6b')
    print(f'llm--->{llm}')
    print(llm.invoke("1+1等于几？"))


