from openai import OpenAI
from src.logs import logger 

class ModelOpenAi:

    def __init__(self, name:str, temperature:float,url:str, key:str|None=None)-> None:

        self.name = name 
        self.temperature = temperature
        self.client = OpenAI(base_url=url, api_key=key if key is not None else "lm-studio") 



    def response(self, prompt:str, input:list) -> str:

        logger.info(f"Generating response from model {self.name}...")
        messages = [{"role": "system", "content": prompt}] + input

      

        response = self.client.chat.completions.create(
            messages=messages,
            temperature=self.temperature,
            model=self.name
        )

        response = response.choices[0].message.content

        logger.success("Response generated with sucess")

        return response

        



    
        
