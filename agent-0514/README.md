# Agent 0514: Embedding RAG

主题：更接近真实 RAG 的流程：chunk -> embedding -> vector search -> cite。

本项目使用本地 hash embedding 模拟向量，不依赖外部服务。

```bash
npm run demo
npm test
npm start
```

你要掌握：chunk 大小、向量相似度、topK、引用、检索评估。
