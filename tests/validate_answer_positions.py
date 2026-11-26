"""Check the order of independently verified, finalized single-choice answer keys."""
import argparse
from collections import Counter
import json
import sys
import unittest


def scan(sequence):
    """Input tokens preserve source order. '-' skips a version; '?' marks a gap."""
    counts = Counter()
    gaps = []
    hits = []
    excluded = 0
    tail = ''
    offsets = []
    tokens = ''.join(sequence.split())
    for index, key in enumerate(tokens, start=1):
        if key == '-':
            excluded += 1
            continue
        if key == '?':
            gaps.append(index)
            tail = ''
            offsets.clear()
            continue
        if not 'A' <= key <= 'Z':
            raise ValueError(f'invalid token {key!r} at position {index}')

        counts[key] += 1
        tail = tail[-17:] + key
        offsets = offsets[-17:] + [index]
        for period in range(1, 7):
            copies = 6 if period == 1 else 3
            length = period * copies
            block = tail[-period:]
            if len(tail) >= length and tail.endswith(block * copies):
                hits.append(dict(first_token=offsets[-length], last_token=index, block=block))
                break  # report the shortest qualifying period at this endpoint

    if hits:
        result = 'PERIOD'
    elif not counts or gaps:
        result = 'INCOMPLETE'
    else:
        result = 'NO_SHORT_PERIOD'
    return dict(result=result, verified_keys=sum(counts.values()), counts=dict(counts),
                excluded_versions=excluded, gap_tokens=gaps, hits=hits)


class AnswerPositionCases(unittest.TestCase):
    def test_report_every_endpoint_in_old_36_to_52_run(self):
        report = scan('CADB CADB CADB CADB C')
        self.assertEqual(report['result'], 'PERIOD')
        self.assertEqual(report['hits'][0], dict(first_token=1, last_token=12, block='CADB'))
        self.assertEqual([35 + hit['last_token'] for hit in report['hits']], list(range(47, 53)))

    def test_periods_one_to_six_at_the_exact_threshold(self):
        for block in ('A', 'BD', 'CAB', 'ADBC', 'DABAC', 'ABCADB'):
            with self.subTest(block=block):
                keys = block * (6 if len(block) == 1 else 3)
                self.assertFalse(scan(keys[:-1])['hits'])
                self.assertEqual(scan(keys)['hits'], [dict(first_token=1, last_token=len(keys), block=block)])

    def test_count_distribution_cannot_substitute_for_sequence(self):
        periodic = scan('ABCD' * 3)
        irregular = scan('AABDCBCDADBC')
        self.assertEqual(periodic['counts'], irregular['counts'])
        self.assertEqual(periodic['result'], 'PERIOD')
        self.assertEqual(irregular['result'], 'NO_SHORT_PERIOD')

    def test_check_intermediate_and_cross_tenth_item_boundaries(self):
        keys = 'DCCADB' + 'ABABAB' + 'CD'
        self.assertFalse(scan(keys[:10])['hits'])
        self.assertFalse(scan(keys[10:])['hits'])
        self.assertIn(dict(first_token=7, last_token=12, block='AB'), scan(keys)['hits'])

    def test_resume_longest_period_with_seventeen_known_positions(self):
        keys = 'BCA' + 'ABCADB' * 3
        recent = keys[:-1][-17:]
        self.assertEqual(scan(recent + keys[-1])['hits'][-1]['block'], 'ABCADB')
        self.assertFalse(scan(recent[-16:] + keys[-1])['hits'])

    def test_excluded_versions_do_not_break_the_effective_sequence(self):
        report = scan('AB-A--B-AB')
        self.assertEqual(report['counts'], {'A': 3, 'B': 3})
        self.assertEqual(report['excluded_versions'], 4)
        self.assertEqual(report['hits'], [dict(first_token=1, last_token=10, block='AB')])

    def test_unknown_gap_neither_bridges_a_pattern_nor_hides_a_known_one(self):
        incomplete = scan('ABA?BAB')
        self.assertEqual(incomplete['result'], 'INCOMPLETE')
        self.assertFalse(incomplete['hits'])
        found = scan('ABABAB?CD')
        self.assertEqual(found['result'], 'PERIOD')
        self.assertEqual(found['gap_tokens'], [7])
        self.assertTrue(found['hits'])

    def test_no_verified_key_does_not_pass(self):
        for keys in ('', '--?', '---'):
            self.assertEqual(scan(keys)['result'], 'INCOMPLETE')
        with self.assertRaises(ValueError):
            scan('AB0C')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan', metavar='KEYS', help="audit keys in order ('-' excluded, '?' unknown)")
    args = parser.parse_args()
    if args.scan is None:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(AnswerPositionCases)
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    try:
        result = scan(args.scan)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 3
    print(json.dumps(result, indent=2))
    return {'NO_SHORT_PERIOD': 0, 'PERIOD': 1, 'INCOMPLETE': 2}[result['result']]


if __name__ == '__main__':
    sys.exit(main())
