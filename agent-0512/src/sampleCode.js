export const sampleCode = `export function LoginButton({ api }) {
  const handleClick = async () => {
    const result = await api.login();
    localStorage.setItem("token", result.token);
  };

  return (
    <button onClick={handleClick}>
      <img src="/login.svg" />
    </button>
  );
}
`;

export const sampleFindings = [
  {
    severity: "high",
    category: "error-handling",
    file: "src/LoginButton.jsx",
    line: 3,
    message: "新增 async 调用缺少错误处理。",
    suggestion: "为 async 调用增加 try/catch，并向用户展示失败状态。"
  },
  {
    severity: "medium",
    category: "accessibility",
    file: "src/LoginButton.jsx",
    line: 9,
    message: "图片缺少 alt 属性。",
    suggestion: "为 img 添加有意义的 alt。"
  }
];
