# 两分钟演示脚本

## 0:00 - 0:20 项目定位

“这是一个从前端规则 Demo 演进来的 Agent 服务。输入 Git diff 后，模型 Provider 会通过三个受控工具完成代码读取、规范检索和修复计划生成。”

## 0:20 - 0:40 API 与 Provider

打开 `/docs`：“服务使用 FastAPI，提供健康检查、普通审查、SSE 审查和 Trace 查询。Provider 支持 Mock 与 DeepSeek，默认 Mock 保证测试稳定。”

## 0:40 - 1:15 实时运行

打开首页，载入样例并点击“运行 Agent”：“右侧依次展示规划阶段和三个工具的运行状态。这里展示的是公开执行阶段，不是模型私有推理。”

## 1:15 - 1:40 结果与可观测性

滚动到 findings、patch plan 和来源：“最终结果经过 Pydantic 校验，每个 finding 有严重级别、文件、行号和建议；traceId 可以关联一次运行的全部事件。”

## 1:40 - 2:00 工程可靠性

打开测试结果：“项目覆盖参数校验、工具超时、重试、降级、稳定错误码和五条端到端用例。真实密钥只从服务端环境变量读取，不进入前端和仓库。”

自动录制页面流程：

```bash
pip install -r requirements-demo.txt
playwright install chromium
python scripts/record_demo.py
```

