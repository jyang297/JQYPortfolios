---
title: "DEMO: Building a Toy RAG in a Weekend"
description: "Placeholder write-up for a tiny RAG experiment with cached embeddings and a scripted evaluator."
pubDate: 2025-01-05
isDraft: false
author: "Demo Author"
tags:
  - RAG
  - LangChain
  - Vector DB
image: "@/assets/blog/placeholder.jpg"
---

> DEMO CONTENT — delete or replace this file when adding real blog posts.

Weekend experiment recap (placeholder):

1) **Goal:** wire up a minimal RAG that answers FAQs for a fake product.  
2) **Data prep:** chunked 25 markdown docs, built embeddings, stored in a local vector DB.  
3) **Retriever:** top-k = 4, rerank with cosine similarity; naive but fine for demo.  
4) **LLM prompts:** system message enforced tone + sources; added guardrail to refuse hallucinations.  
5) **Eval:** scripted 20 Q&A pairs, measured hit rate and latency. Average latency 1.3s on laptop.  
6) **Next:** add metadata filters, swap reranker, push to a serverless endpoint.
