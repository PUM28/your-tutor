import json
import tempfile
import unittest
import zipfile
import shutil
import subprocess
import sys
from pathlib import Path

from video_learning import choose_track, export_pack, overlapping, parse_captions, sample_times, seconds, stamp


class EvidenceTests(unittest.TestCase):
    def test_repeated_speech_at_distinct_times_is_preserved(self):
        cues = parse_captions('WEBVTT\n\n00:00:01.125 --> 00:00:02.250\nx\n\n'
                              '00:00:10.000 --> 00:00:11.000\nx\n')
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0]['start_s'], 1.125)
        self.assertEqual(cues[0]['end_s'], 2.25)

    def test_exact_duplicates_removed_but_rolling_evidence_retained(self):
        cue = '00:00:01.000 --> 00:00:02.000\nlog\n\n'
        rows = parse_captions('WEBVTT\n\n' + cue + cue +
                              '00:00:01.500 --> 00:00:03.000\nlog likelihood\n')
        self.assertEqual([r['text'] for r in rows], ['log', 'log likelihood'])

    def test_srt_and_html_entities(self):
        rows = parse_captions('1\r\n01:02:03,456 --> 01:02:04,789\r\n<b>x</b> &lt; y\r\n')
        self.assertEqual(rows[0], {'start_s': 3723.456, 'end_s': 3724.789, 'text': 'x < y'})

    def test_note_blocks_not_speech(self):
        self.assertEqual(parse_captions('WEBVTT\n\nNOTE\n00:00:01.000 --> 00:00:02.000\nignore'), [])

    def test_reverse_caption_rejected(self):
        with self.assertRaises(ValueError):
            parse_captions('00:00:02.000 --> 00:00:01.000\ntext')

    def test_window_includes_crossing_cue_not_neighbor(self):
        rows = [{'start_s': 0, 'end_s': 10}, {'start_s': 10, 'end_s': 20},
                {'start_s': 20, 'end_s': 30}]
        self.assertEqual(overlapping(rows, 10, 20), [rows[1]])
        self.assertEqual(overlapping(rows, 9, 11), rows[:2])

    def test_end_clamp_matches_upstream_seek(self):
        self.assertEqual(sample_times(0, 20, 10, 20), [0, 10, 19.5])
        self.assertEqual(sample_times(10, 15, 10, 20), [10, 15])

    def test_nonfinite_bad_ranges_and_budget_rejected(self):
        for args in [(0, 20, 0, 20), (10, 5, 1, 20), (0, float('inf'), 1, 20),
                     (0, 21, 10, 20), (19.8, 20, 1, 20), (0, 1000, 1, 1000)]:
            with self.assertRaises(ValueError):
                sample_times(*args)

    def test_requested_language_precedes_other_manual_track(self):
        self.assertEqual(choose_track({'zh': []}, {'en-orig': []}, 'en'), ('en-orig', True))
        self.assertEqual(choose_track({'en-xyz': []}, {'en': []}, 'en'), ('en-xyz', False))
        self.assertIsNone(choose_track({'zh': []}, {}, 'vi'))

    def test_time_roundtrip(self):
        for t in (0, 0.123, 3599.999, 3600, 3733.629):
            self.assertAlmostEqual(seconds(stamp(t)), t, places=3)

    def test_export_escapes_source_and_never_claims_formula_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'frame.jpg').write_bytes(b'test image')
            manifest = {'source': 'https://example.org/video', 'title': '<script>bad()</script>',
                        'start_s': 0, 'end_s': 10, 'formula_status': 'unverified'}
            export_pack(out, manifest, [{'start_s': 1, 'end_s': 2, 'text': '<script>x</script>'}],
                        [{'timestamp_s': 1, 'path': 'frame.jpg'}])
            page = (out / 'study-pack.html').read_text()
            self.assertNotIn('<script>', page)
            self.assertIn('&lt;script&gt;', page)
            self.assertEqual(json.loads((out / 'manifest.json').read_text())['formula_status'], 'unverified')
            with zipfile.ZipFile(out / 'study-pack.zip') as z:
                self.assertIsNone(z.testzip())
                self.assertIn('frame.jpg', z.namelist())
                self.assertNotIn('study-pack.zip', z.namelist())


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'needs ffmpeg')
class LocalIntegrationTests(unittest.TestCase):
    def test_two_repo_adapter_aligns_red_then_blue_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            video, captions, out = folder / 'colors.mp4', folder / 'colors.vtt', folder / 'pack'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                            'color=c=red:s=160x90:r=10:d=2', '-f', 'lavfi', '-i',
                            'color=c=blue:s=160x90:r=10:d=2', '-filter_complex',
                            '[0:v][1:v]concat=n=2:v=1:a=0[v]', '-map', '[v]',
                            '-c:v', 'libx264', str(video)], check=True, capture_output=True)
            captions.write_text('WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nred\n\n'
                                '00:00:02.000 --> 00:00:04.000\nblue\n')
            script = Path(__file__).with_name('video_learning.py')
            command = [sys.executable, str(script), str(video), '--captions', str(captions),
                       '--interval', '1', '--cache', str(folder / 'cache'), '--out', str(out)]
            run = subprocess.run(command, text=True, capture_output=True, timeout=90)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            self.assertEqual(result['status'], 'evidence_ready')
            frames = json.loads((out / 'frames.json').read_text())
            for time, dominant in [(1.0, 0), (3.0, 2)]:
                frame = next(f for f in frames if f['timestamp_s'] == time)
                rgb = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(out / frame['path']),
                                      '-vf', 'scale=1:1', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-'],
                                     check=True, capture_output=True).stdout[:3]
                self.assertGreater(rgb[dominant], 200)
                self.assertLess(rgb[2 if dominant == 0 else 0], 30)
            # Re-running into the same folder must not destroy a learner's notes.
            (out / 'my-notes.md').write_text('keep')
            second = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual((out / 'my-notes.md').read_text(), 'keep')


if __name__ == '__main__':
    unittest.main()
