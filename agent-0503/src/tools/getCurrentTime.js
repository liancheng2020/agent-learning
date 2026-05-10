export const getCurrentTimeTool = {
  name: "getCurrentTime",
  description: "Get the current local time.",
  parameters: {
    type: "object",
    properties: {
      locale: {
        type: "string",
        description: "BCP 47 locale used to format the time.",
      },
    },
    required: [],
    additionalProperties: false,
  },
  execute({ locale = "zh-CN" } = {}) {
    const now = new Date();

    return {
      iso: now.toISOString(),
      localTime: new Intl.DateTimeFormat(locale, {
        dateStyle: "full",
        timeStyle: "medium",
        timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      }).format(now),
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    };
  },
};
