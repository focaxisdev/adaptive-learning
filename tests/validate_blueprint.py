"""Synthetic fixture checks. No model, question classifier, or teaching runtime."""
import json
from pathlib import Path
import re
import unittest

from validate_docs import modules, SPEC


def fixture():
    document = Path(__file__).with_name('blueprint_cases.md').read_text(encoding='utf-8')
    return json.loads(re.search(r'^\x60{3}json\n(.*?)\n\x60{3}$', document, re.M | re.S)[1])


def audit_index(case):
    sources = case['source_skills']
    if set(case['blueprint']['by_skill']) != set().union(*sources.values()):
        raise ValueError('source union')
    move = case['relocated_source']
    if move['version'] == case['blueprint']['version'] or move['from'] == move['to']:
        raise ValueError('revision')
    if set(move['ids']) != set(sources[move['from']]):
        raise ValueError('unstable IDs')
    gap = case['unread_case']
    if set(gap['unknown']) != set(gap['required']) - set(gap['read']):
        raise ValueError('source gap')


def completed(case, tail):
    """Reconcile manually labelled evidence by cycle/question, preserving old scores."""
    rows = {(case['cycle'], n): ('prior', skill, score) for n, skill, score in case['prior']}
    withdrawn = set()
    for number, version, skill, status, score in tail:
        ref = (case['cycle'], number)
        if status in ('pending', 'withdrawn'):
            if score is not None:
                raise ValueError('unanswered score')
            if status == 'withdrawn':
                withdrawn.add((ref, version))
            continue
        if status != 'valid' or (ref, version) in withdrawn or score not in (0, 1):
            raise ValueError('invalid score record')
        record = (version, skill, score)
        if ref in rows and rows[ref] != record:
            raise ValueError('conflicting replay')
        rows[ref] = record
    return rows


def coverage(skills, rows):
    mapped = {skill: [] for skill in skills}
    missing = []
    for ref, (_, skill, _) in rows.items():
        if skill is None:
            missing.append(ref)
        else:
            mapped[skill].append(ref)
    status = {}
    for skill, refs in mapped.items():
        if refs:
            status[skill] = 'tested'
        else:
            status[skill] = 'unknown' if missing else 'untested'
    return mapped, status


class BlueprintCases(unittest.TestCase):
    def setUp(self):
        self.case = fixture()

    def test_sources_union_revision_and_unread(self):
        audit_index(self.case)
        sources = self.case['source_skills']
        self.assertNotIn('BEAT-R', sources['S1'])
        self.assertIn('BEAT-R', sources['R1 §2'])
        self.assertNotIn('TIME-C', sources['R1 §1'] + sources['R1 §2'])

    def test_reject_corrupt_blueprint_and_hidden_source_gap(self):
        for field, corrupt, message in [
            ('blueprint', lambda value: value['by_skill'].pop('BEAT-R'), 'source union'),
            ('relocated_source', lambda value: value['ids'].append('MAP-NEW'), 'unstable IDs'),
            ('unread_case', lambda value: value['unknown'].clear(), 'source gap'),
        ]:
            with self.subTest(field=field):
                case = fixture()
                corrupt(case[field])
                with self.assertRaisesRegex(ValueError, message):
                    audit_index(case)

    def test_retest_requires_different_decision_in_annotated_examples(self):
        old, skin, retest = self.case['dedup']
        self.assertEqual([item['role'] for item in [old, skin, retest]], ['old', 'reskin', 'retest'])
        self.assertEqual({item['skill'] for item in [old, skin, retest]}, {'MAP-S'})
        self.assertNotEqual(old['material'], skin['material'])
        self.assertEqual(old['decision'], skin['decision'])
        self.assertNotEqual(old['decision'], retest['decision'])

    def test_resume_replace_and_tenth_effective_answer(self):
        tail = self.case['tail']
        pending, replacement = (self.case[key] for key in ('pending', 'replacement'))
        for prompt, event in ((pending, tail[0]), (replacement, tail[2])):
            self.assertEqual((prompt['number'], prompt['version']), tuple(event[:2]))
            self.assertEqual(set(prompt), {'number', 'version', 'text'})
        self.assertEqual(pending['number'], replacement['number'])
        self.assertNotEqual(pending['text'], replacement['text'])
        # Each prefix represents a possible interruption or pasted handoff.
        for end in range(len(tail) + 1):
            rows = completed(self.case, tail[:end])
            finished = end >= 5
            self.assertEqual(len(rows), 10 if finished else 9)
            self.assertEqual(sum(row[2] for row in rows.values()), 9 if finished else 8)
            mapped, state = coverage(self.case['blueprint']['by_skill'], rows)
            self.assertEqual(('C', 10) in mapped['MAP-N'], finished)
            self.assertNotIn(('C', 10), mapped['MAP-S'])
            self.assertEqual(state['BEAT-R'], 'untested')

    def test_damaged_legacy_mapping_preserves_score_and_uncertainty(self):
        self.case['prior'][0][1] = None
        rows = completed(self.case, [])
        _, state = coverage(self.case['blueprint']['by_skill'], rows)
        self.assertEqual((len(rows), sum(row[2] for row in rows.values())), (9, 8))
        self.assertEqual(state['BEAT-R'], 'unknown')
        self.assertEqual(state['MAP-N'], 'tested')
        self.assertNotIn('mastered', state.values())

    def test_reject_withdrawn_answer_pending_score_and_conflicting_replay(self):
        tail = self.case['tail']
        for extra, message in [
            ([10, 'a', 'MAP-S', 'valid', 1], 'invalid score record'),
            ([11, 'a', 'TIME-C', 'pending', 0], 'unanswered score'),
            ([10, 'b', 'MAP-N', 'valid', 0], 'conflicting replay'),
        ]:
            with self.subTest(extra=extra), self.assertRaisesRegex(ValueError, message):
                completed(self.case, tail + [extra])

    def test_portable_quiz_rules_in_common_block(self):
        # All configured modes carry the common block into a fresh chat.
        common = modules(SPEC.read_text(encoding='utf-8'))['共同核心']
        for requirement in ('短測配置或中途交接', '教材原句', '版本／位置', '先請補貼', '已答與待答狀態'):
            self.assertIn(requirement, common)

    def test_configuration_distinguishes_start_here_from_export(self):
        setup = SPEC.read_text(encoding='utf-8').split('## 共同核心', 1)[0]
        for requirement in ('目前 Chat 直接開始', '一道短診斷', '索取可攜配置', '已確認配置', '已啟用模式'):
            self.assertIn(requirement, setup)

    def test_pasteable_mode_blocks_expose_entry_points(self):
        # Static projection only. Conversational acceptance is in blueprint_cases.md.
        blocks = modules(SPEC.read_text(encoding='utf-8'))
        exam = blocks['共同核心'] + blocks['純 Chat 模考']
        for word in ('藍圖', '版本', '確認', '開考', '待答', '短測'):
            self.assertIn(word, exam)
        for mode in ('一般教學', '針對性補強'):
            self.assertNotIn('校準負荷', blocks[mode])
            self.assertNotIn('全池', blocks[mode])


if __name__ == '__main__':
    unittest.main(verbosity=2)
