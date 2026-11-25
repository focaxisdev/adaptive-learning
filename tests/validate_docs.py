"""Maintainer-only structural checks; not a teaching runtime or psychometric test."""
from pathlib import Path
import re
import subprocess
import unittest
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
READMES = ['README.md', 'README.en.md', 'README.ja.md']
DOCS = [*sorted(ROOT.glob('README*.md')), ROOT / 'NOTICE.md',
        *sorted((ROOT / 'docs').rglob('*.md'))]
SPEC = ROOT / 'docs/PROJECT_INSTRUCTIONS.md'
NAMES = ['共同核心', '一般教學', '針對性補強', '純 Chat 模考', '正式考試難度校準']


def modules(text):
    result = {}
    for section in re.split(r'^## ', text, flags=re.M)[1:]:
        title = section.splitlines()[0]
        blocks = re.findall(r'```text\n(.*?)\n```', section, re.S)
        if blocks:
            if title in result or len(blocks) != 1:
                raise ValueError('Duplicate module/block: ' + title)
            result[title] = blocks[0]
    return result


def anchors(text):
    return {re.sub(r'[^\w\-\u4e00-\u9fff ]', '', h.lower()).replace(' ', '-')
            for h in re.findall(r'^#+ (.+)$', text, re.M)}


class DocumentChecks(unittest.TestCase):
    def test_links_and_fences(self):
        for path in DOCS:
            text = path.read_text()
            self.assertEqual(sum(line.startswith('```') for line in text.splitlines()) % 2, 0, path)
            for target in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in target:
                    continue
                parts = target.split('#', 1)
                dest = (path.parent / parts[0]).resolve()
                self.assertTrue(dest.is_file(), (path, target))
                if len(parts) == 2:
                    self.assertIn(parts[1], anchors(dest.read_text()), (path, target))

    def test_locale_navigation_and_entry_point(self):
        for name in READMES:
            with self.subTest(locale=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                for other in READMES:
                    if other != name:
                        self.assertIn(f']({other})', text)
                self.assertIn('](docs/PROJECT_INSTRUCTIONS.md)', text)

    def test_mode_projection(self):
        # Ensures the extractable general-learning bundle does not silently
        # require unselected exam configuration. Semantic fidelity needs review.
        blocks = modules(SPEC.read_text())
        self.assertEqual(set(blocks), set(NAMES))
        general = blocks['共同核心'] + '\n' + blocks['一般教學']
        self.assertNotIn('iPAS', general)
        self.assertNotIn('50 題', general)
        self.assertNotIn('〔', general)
        self.assertLess(len(general), 2300)
        self.assertIn('未配置模式', blocks['共同核心'])
        self.assertIn('開放題', blocks['共同核心'])
        self.assertIn('成功條件', blocks['一般教學'])
        self.assertIn('最多兩輪', blocks['一般教學'])
        self.assertIn('最多兩輪', blocks['針對性補強'])

    def test_privacy_patterns(self):
        # Targeted scan only: absence of these patterns is not proof of no PII.
        patterns = [r'chatgpt\.com/(?:c|share)/', r'libfile_',
                    r'\b(?:ghp|github_pat|xox[baprs])[-_][A-Za-z0-9_]+',
                    r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}']
        for path in DOCS:
            for pattern in patterns:
                self.assertIsNone(re.search(pattern, path.read_text()), (path, pattern))

    def test_synthetic_answers(self):
        self.assertEqual(Fraction(12, 12 + 3), Fraction(4, 5))
        self.assertEqual(Fraction(18, 18 + 2), Fraction(9, 10))
        items = ['x']
        alias = items
        alias.append('y')
        self.assertEqual(items, ['x', 'y'])
        self.assertEqual(Fraction(60 + 100, 100 + 100), Fraction(4, 5))
        self.assertLess(Fraction(60 + 99, 100 + 99), Fraction(4, 5))
        self.assertEqual(sum([1, 0, 1]), 2)

    def test_diff_whitespace(self):
        subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
