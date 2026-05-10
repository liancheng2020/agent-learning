import { validateLearningPlan } from "./schema.js";

export function createLearningPlan({
  date = "2026-05-05",
  availableHours = 2,
  goal = "学习结构化输出，并做一个可校验的学习计划 Agent",
} = {}) {
  const plan = {
    date,
    theme: "结构化输出与任务拆解 Agent",
    goal,
    schedule: buildSchedule(availableHours),
    checklist: [
      "阅读 schema 约束和结构化输出的核心概念",
      "实现一个能输出固定 JSON 结构的 Planner Agent",
      "实现 validateLearningPlan 校验函数",
      "跑通 demo 和测试用例",
      "写下今天遇到的问题和明天的唯一目标",
    ],
    acceptanceCriteria: [
      "npm run demo 能输出完整学习计划",
      "npm test 能验证计划结构合法",
      "输出结果包含 schedule、checklist、acceptanceCriteria",
      "计划不是纯文本，而是可被程序继续消费的对象",
    ],
    nextStep: "明天把计划执行过程写入 JSONL 日志，形成最小 tracing/eval 基础。",
  };

  const errors = validateLearningPlan(plan);
  return {
    ok: errors.length === 0,
    plan,
    errors,
  };
}

export function renderPlanMarkdown(plan) {
  const schedule = plan.schedule
    .map((item) => `- ${item.time}: ${item.task}\n  产出：${item.output}`)
    .join("\n");
  const checklist = plan.checklist.map((item) => `- [ ] ${item}`).join("\n");
  const acceptanceCriteria = plan.acceptanceCriteria.map((item) => `- ${item}`).join("\n");

  return `# ${plan.date} 学习计划

## 主题
${plan.theme}

## 今日目标
${plan.goal}

## 时间安排
${schedule}

## 打卡清单
${checklist}

## 验收标准
${acceptanceCriteria}

## 明日衔接
${plan.nextStep}
`;
}

function buildSchedule(availableHours) {
  if (availableHours <= 1.5) {
    return [
      {
        time: "20 分钟",
        task: "理解结构化输出为什么比自由文本更适合 Agent 工程",
        output: "写出 3 条结构化输出的使用场景",
      },
      {
        time: "50 分钟",
        task: "实现 Planner Agent 和 schema 校验",
        output: "能生成并校验学习计划对象",
      },
      {
        time: "20 分钟",
        task: "跑 demo、补 README、提交今日记录",
        output: "项目可运行，日志完整",
      },
    ];
  }

  return [
    {
      time: "20 分钟",
      task: "复盘昨天 Tool Calling 项目，找出返回值不稳定的风险",
      output: "列出至少 2 个需要结构化输出解决的问题",
    },
    {
      time: "35 分钟",
      task: "设计 LearningPlan schema",
      output: "确定 date、theme、goal、schedule、checklist、acceptanceCriteria 等字段",
    },
    {
      time: "70 分钟",
      task: "实现 Planner Agent、校验函数和 demo/test 入口",
      output: "npm run demo 与 npm test 都能通过",
    },
    {
      time: "25 分钟",
      task: "整理 README 和今日打卡记录",
      output: "能向别人说明这个项目解决了 Agent 的什么工程问题",
    },
  ];
}
