from langchain.llms import OpenAI
from langchain.chains import LLMChain,SimpleSequentialChain
from langchain.prompts import PromptTemplate
from langchain.memory import SimpleMemory
import os

##os.environ["OPENAI_API_KEY"]=""
def seq_chain(topic):
    llm=OpenAI(temperature=0.7)
    template="""You are a content creator! Given a topic it is your job is to create a subject
    Title:{topic}
    Creator: This is the title for the above topic"""

    prompt_template=PromptTemplate(template=template,input_variables=['topic'])
    title_chain=LLMChain(llm=llm,prompt=prompt_template,output_key="subject")

    template="""You are a content creator! Given a subject it is your job is to create body for an email
    Subject:{subject}
    Creator: This is the content for the above subject"""

    prompt_template=PromptTemplate(template=template,input_variables=['subject'])
    content_chain=LLMChain(llm=llm,prompt=prompt_template,output_key="body")
    overall_chain=SimpleSequentialChain(chains=[title_chain,content_chain],verbose=True)
    return overall_chain.run(topic)

if __name__ == '__main__':
    seq_chain()