"""Verifica a estrutura e integração das skills pedagógicas adicionais."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    'knowledge-transfer': ('references/test-design.md',),
    'song-difficulty-analyzer': ('references/rubric.md',),
}


class SkillExtensionTests(unittest.TestCase):
    def test_skills_have_matching_frontmatter(self):
        for name in SKILLS:
            path = ROOT / '.agents' / 'skills' / name / 'SKILL.md'
            self.assertTrue(path.is_file(), path)
            text = path.read_text(encoding='utf-8')
            self.assertTrue(text.startswith('---\n'), name)
            self.assertRegex(text, rf'(?m)^name: {re.escape(name)}$')
            self.assertRegex(text, r'(?m)^description: .+')

    def test_skill_reference_files_exist(self):
        for name, references in SKILLS.items():
            for reference in references:
                path = ROOT / '.agents' / 'skills' / name / reference
                self.assertTrue(path.is_file(), path)

    def test_agents_routes_to_both_skills_without_new_hooks(self):
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        for name in SKILLS:
            self.assertIn(f'${name}', agents)
            self.assertIn(f'`{name}`', agents)
        self.assertIn('não exigem hooks novos', agents)

    def test_skill_paths_use_the_embedded_workspace(self):
        for name in SKILLS:
            text = (ROOT / '.agents' / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8')
            self.assertIn('workspaces/', text)

    def test_readme_documents_skill_discovery(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        guide = (ROOT / 'INSTALL-SKILLS.md').read_text(encoding='utf-8')
        self.assertIn('INSTALL-SKILLS.md', readme)
        self.assertIn('nova sessão', guide.lower())
        self.assertIn('workspaces/', guide)


if __name__ == '__main__':
    unittest.main()
