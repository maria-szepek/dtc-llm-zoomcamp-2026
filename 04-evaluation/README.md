# evaluation 

* user talking to assistant, which is an agent with different tools, a.o. the searching tool (agentic RAG)
* it is up to the agent how many times it will invoke that search tool and what questions to send
* USER <--> ASSISTANT <--> [SEARCH <--> KDB]

* **In the first part we evaluate how good is the search**

* **For the rag evaluation we will use the A → Q* → A' pattern.**

A - original answer in the faq
Q* - question generated from that answer by an llm (synthetic data)
A' - answer produced by the RAG system when given Q*

* There is online vs offline evaluation 

* We will cover: 

Search evaluation: does the search return the right documents? (Hit Rate and MRR (Mean Reciprocal Rank))

RAG evaluation: does the LLM generate good answers? (LLM-as-a-judge)

Agent evaluation: does the agent use tools efficiently? (final answer and the tool-call trajectory)


# 1. how to evaluate

* collect as many questions as possible, interact with system, and collect the data. (INTERACT -> LOGS ->{Q;})
 ( Q are are the questions we want to evaluate)

* a is system (rag) generated, for this query document 1 and document 5 is relevant that cna be done manually 

# 2. today: generate data 

* in the faq db we have questions and answers 
* FAQ - (Qi, Ai) = real data (FAQ)
* we are trying to go back from the answer, what question can be asked, e.g. 


* Ai -> Qi1*, ..., Qin* -> (Qi1*, Ai; ... Qin*, Ai)
* then we send these questions, send it through the entire rag system, obtain retrieved answer a* and we want to know if A element of (d1, d2, ...) returned by the system






# ABOUT PART 2: RAG and Agent Evaluation

* we have this fake data that we generated so we can use the entire rag and at the end there is an answer that we get. 
* so we can compare answer we get to the reference answer 
* so we'll go through the entire data set of ground truth data, and compare by showing an llm: 

here look, this is the question the user had, this is the reference answer and this is what the llm generated. 




# next steps .. 

* generated data is good if i don't have any data, good proxy but once i have real data i need to start adjusting the data generation process to mimic real data

* even if i just collect the real user question i can ask an llm to generate something similar 

* and later i can start labeling the data coming from production

* the earlier i can start doing that the better 

*  THERE ARE ALSO OTHER EVALUATING METHODS SUCH AS COSINE SIMILARITY SEE OLDER COHORTS 

* evaluation is the most important part. 

