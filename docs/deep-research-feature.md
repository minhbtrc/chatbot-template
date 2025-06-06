# Deep Research Feature

## What is Deep Research? 
- Deep Research is the ability of a model to search the Internet, analyse web pages and documents, and give the most accurate and thoughtful answer based on the information found. It helps to break internal knowledge limits or gaps on complex tasks. In other words, it automates knowledge mining via simple search queries. 

- On Feb 02 2025, OpenAI Deep Research is built on top of the O3 model, with the help of RL, they taught the model to use a browser(searching, clicking, scrolling, etc.), Python, and reason on a massive amount of data to find specific information.

- All of these were possible due to a new browsing dataset for research use cases.

## Open source Deep Research 
- Because we don't know how this feature of OpenAI is built, there are some attempts to build an open source version of it. For examples, [Hugginface](https://huggingface.co/blog/open-deep-research) and [Langchain](https://github.com/langchain-ai/open_deep_research/tree/main?tab=readme-ov-file), [WebThinker](https://github.com/RUC-NLPIR/WebThinker)

There are 2 directions to replicate the feature: By Workflows and by Multi Agents. But the idea behind is the same, including 3 main components: 
1. Planing: use a Large Reasoning Model (LRM) to plan the task. This can be supported by human by asking follow up questions to refine the plan (OpenAI), or Gemini allow user to accept and confirm the plan generated.
2. The reflection loop: for each section of the plan, use an LLM and a search tool (tavily). First, based on the plan, LLM will use tavily to search the web, then use the search results to reflect and refine the answer. This is a loop until the LLM is confident with the answer.
3. The output: after the reflection loop, the answer will be generated and reported.

## An overall picture of Deep Research
![Comparison between OpenAI's Deep Research and Open Source version](docs/img/opensource-deepresearch.jpeg)

- About architecture, we have 2 directions to build the deep research. About the UX, we can invovle the Human In The Loop (HITL) or not.
- About HITL, OpenAI's Deep Research is supported by a human to ask follow up questions to refine the plan. Gemini's Deep Research is supported by a human to accept and confirm the plan generated.