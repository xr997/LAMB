# Examples

LAMB 的示例场景刻意保持日常化，方便评委和用户快速理解。

## 批量批改作业

```bash
lamb extract data/homework --fields "姓名,分数,评语,主要问题" --redact
```

输出 CSV 可以直接用 Excel 打开。每一行对应一份作业。

## 批量读论文

```bash
lamb research data/papers --question "这些论文的研究问题、方法和结论分别是什么？"
```

输出 Markdown 报告，包含结论、关键依据、来源引用和不确定性。

## 会议纪要整理

```bash
lamb extract data/meetings --fields "会议主题,待办事项,负责人,截止时间"
```

适合把多个会议纪要整理成一张待办表。

## 简历筛选

```bash
lamb extract data/resumes --fields "姓名,教育背景,技能,项目经验,匹配岗位"
```

建议搭配 `--redact`，减少手机号、邮箱等敏感信息进入 LLM 请求。

## 调研报告总结

```bash
lamb research data/reports --question "这些报告共同反映了哪些趋势？有哪些明显分歧？"
```

适合处理多个调研报告、访谈纪要、市场材料。

## 安全预览

```bash
lamb research data/inputs --question "这些文档说了什么？" --dry-run --strict-security
```

`--dry-run` 不调用 LLM，适合先看文件清单、跳过原因、输出路径和安全提示。
