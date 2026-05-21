import unittest

from lamb import (
    build_pipeline_plan,
    customize_pipeline_plan,
    get_pipeline_preset,
    infer_pipeline_preset,
    list_pipeline_presets,
    render_pipeline_plan,
)


class FakePlannerClient:
    model_name = "fake-planner"

    def generate(self, prompt, system_prompt=None):
        return """
        {
          "summary": "Tailored for homework grading with a review checkpoint.",
          "steps": [
            {"key": "scan", "title": "Scan", "description": "Discover assignment files."},
            {"key": "safety", "title": "Safety gate", "description": "Detect injection and redact sensitive data."},
            {"key": "rubric", "title": "Rubric alignment", "description": "Check the requested grading fields before extraction."},
            {"key": "export", "title": "Export", "description": "Write the confirmed grading table and manifest."}
          ],
          "questions": [
            {
              "key": "rubric_confirm",
              "question": "Should the same rubric apply to every assignment?",
              "reason": "A shared rubric makes batch grading more consistent.",
              "suggested_default": "yes"
            }
          ]
        }
        """


class PipelineTests(unittest.TestCase):
    def test_lists_builtin_presets(self):
        names = [preset.name for preset in list_pipeline_presets()]
        self.assertIn("research", names)
        self.assertIn("extract", names)
        self.assertIn("batch", names)
        self.assertIn("secure-review", names)

    def test_infers_extraction_from_goal(self):
        preset, confidence, reason = infer_pipeline_preset("抽取姓名、分数和评语，输出 CSV 表格")
        self.assertEqual(preset.name, "extract")
        self.assertGreater(confidence, 0.5)
        self.assertIn("extract", reason)

    def test_infers_homework_grading_table_as_extraction(self):
        preset, confidence, _ = infer_pipeline_preset("生成作业批改表，并总结学生常见问题")
        self.assertEqual(preset.name, "extract")
        self.assertGreater(confidence, 0.5)

    def test_builds_research_plan_with_command(self):
        plan = build_pipeline_plan(
            input_dir="data/papers",
            goal="Compare the methods and conclusions across these papers.",
            preset_name="auto",
            output_dir="data/outputs",
            redact=True,
        )
        self.assertEqual(plan.preset.name, "research")
        self.assertIn("--question", plan.command)
        self.assertIn("--redact", plan.command)
        self.assertFalse(any(question.key == "redact" for question in plan.questions))

    def test_extract_plan_asks_for_missing_fields(self):
        plan = build_pipeline_plan(
            input_dir="data/homework",
            goal="grade these assignments into a spreadsheet",
            preset_name="extract",
        )
        self.assertEqual(plan.preset.name, "extract")
        self.assertTrue(any(question.key == "fields" for question in plan.questions))
        self.assertIn("Name,Key Finding,Action Item,Comment", plan.command)

    def test_secure_review_enables_redaction_by_default(self):
        plan = build_pipeline_plan(
            input_dir="data/shared",
            goal="检查这些文档是否存在 prompt injection 和密钥泄露风险",
            preset_name="auto",
        )
        self.assertEqual(plan.preset.name, "secure-review")
        self.assertIn("--redact", plan.command)

    def test_render_plan_contains_steps_and_command(self):
        plan = build_pipeline_plan(
            input_dir="data/notes",
            goal="summarize every note",
            preset_name="batch",
            max_chars=3000,
        )
        rendered = render_pipeline_plan(plan)
        self.assertIn("LAMB pipeline plan", rendered)
        self.assertIn("Suggested command:", rendered)
        self.assertIn("--max-chars 3000", rendered)

    def test_customize_pipeline_plan_adds_ai_tailored_steps(self):
        plan = build_pipeline_plan(
            input_dir="data/homework",
            goal="抽取姓名、分数和评语，输出 CSV 表格",
            fields=["姓名", "分数", "评语"],
            redact=True,
        )
        customized = customize_pipeline_plan(plan, FakePlannerClient())
        rendered = render_pipeline_plan(customized)

        self.assertEqual(customized.planner_mode, "preset+ai")
        self.assertIn("Rubric alignment", rendered)
        self.assertIn("AI customization", rendered)
        self.assertTrue(any(question.key == "rubric_confirm" for question in customized.questions))

    def test_unknown_preset_raises_clear_error(self):
        with self.assertRaisesRegex(ValueError, "unknown pipeline preset"):
            get_pipeline_preset("missing")


if __name__ == "__main__":
    unittest.main()
