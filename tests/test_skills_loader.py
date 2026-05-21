"""Tests that all SKILL.md files load correctly via AgentSkills."""

import pathlib

import pytest

SKILLS_DIR = pathlib.Path(__file__).parent.parent / "skills"

EXPECTED_SKILL_DIRS = {
    "reflect-framework",
    "prompt-evaluation",
    "prompt-improvement",
    "prompt-styles",
    "prompt-chaining",
}


class TestSkillDirectories:
    def test_all_expected_skill_dirs_exist(self) -> None:
        actual = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
        assert EXPECTED_SKILL_DIRS.issubset(actual), (
            f"Missing skill dirs: {EXPECTED_SKILL_DIRS - actual}"
        )

    @pytest.mark.parametrize("skill_name", sorted(EXPECTED_SKILL_DIRS))
    def test_skill_dir_contains_skill_md(self, skill_name: str) -> None:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        assert skill_file.exists(), f"{skill_file} not found"

    @pytest.mark.parametrize("skill_name", sorted(EXPECTED_SKILL_DIRS))
    def test_skill_md_is_non_empty(self, skill_name: str) -> None:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8").strip()
        assert len(content) > 0, f"{skill_file} is empty"


class TestAgentSkillsLoading:
    def test_agent_skills_plugin_loads_all_dirs(self) -> None:
        """AgentSkills should parse all SKILL.md files without raising."""
        from strands import AgentSkills

        plugin = AgentSkills(skills=[str(SKILLS_DIR)])
        assert plugin is not None

    def test_agent_init_loads_skills_without_error(self) -> None:
        """The module-level agent in agent/__init__.py loads without raising."""
        from agent import agent

        assert agent is not None
        assert agent.name == "ReFlectPromptingAgent"
