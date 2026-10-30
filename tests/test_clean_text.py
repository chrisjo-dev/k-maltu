import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import FIXTURES, SCRIPTS

from clean_text import clean_markdown

ZW = "​"
FLAG = "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F"
FAMILY = "\U0001F468‍\U0001F469‍\U0001F467"


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / "clean_text.py"), *map(str, args)],
                          capture_output=True, text=True)


class CleanMarkdownTest(unittest.TestCase):
    def test_fixture_matches_expected_exactly(self):
        src = (FIXTURES / "hidden_sample.md").read_text(encoding="utf-8")
        expected = (FIXTURES / "hidden_sample.expected.md").read_text(encoding="utf-8")
        out, stats = clean_markdown(src)
        self.assertEqual(out, expected)
        self.assertEqual(stats["removed_count"], 7)

    def test_removes_hidden_chars_in_prose(self):
        out, _ = clean_markdown(f"가{ZW}나﻿다⁠라­마\U000E0041바‮사")
        self.assertEqual(out, "가나다라마바사")

    def test_preserves_fenced_and_inline_code(self):
        src = f"앞{ZW}글\n\n```\nx{ZW}y\n```\n\n~~~\nq{ZW}r\n~~~\n\n중간 `a{ZW}b` 와 ``c`{ZW}d`` 끝{ZW}\n"
        out, stats = clean_markdown(src)
        self.assertIn(f"x{ZW}y", out)
        self.assertIn(f"q{ZW}r", out)
        self.assertIn(f"`a{ZW}b`", out)
        self.assertIn(f"``c`{ZW}d``", out)
        self.assertNotIn(f"앞{ZW}", out)
        self.assertNotIn(f"끝{ZW}", out)
        self.assertEqual(stats["removed_count"], 2)
        self.assertEqual(stats["code_hidden"], {"U+200B ZERO WIDTH SPACE (Cf)": 4})

    def test_unclosed_fence_protects_until_end(self):
        src = f"글{ZW}\n```\n코드{ZW}\n"
        out, _ = clean_markdown(src)
        self.assertEqual(out, f"글\n```\n코드{ZW}\n")

    def test_unmatched_backtick_is_prose(self):
        out, _ = clean_markdown(f"짝 없는 ` 백틱 뒤{ZW}글")
        self.assertEqual(out, "짝 없는 ` 백틱 뒤글")

    def test_no_markdown_mode_cleans_code_too(self):
        out, _ = clean_markdown(f"`a{ZW}b`", markdown=False)
        self.assertEqual(out, "`ab`")

    def test_keeps_emoji_flag_and_hangul_filler_after_jamo(self):
        heart = "❤️"
        src = f"{FAMILY} {heart} {FLAG} ㄱㅤ ᄀᅠ"
        out, stats = clean_markdown(src)
        self.assertEqual(out, src)
        self.assertEqual(stats["removed_count"], 0)

    def test_removes_isolated_hangul_filler(self):
        out, _ = clean_markdown("이름: ㅤㅤ 끝")
        self.assertEqual(out, "이름:  끝")

    def test_space_homoglyphs_reported_not_replaced_by_default(self):
        src = "가 나　다"
        out, stats = clean_markdown(src)
        self.assertEqual(out, src)
        self.assertEqual(sum(stats["spaces_left"].values()), 2)
        self.assertEqual(stats["replaced_count"], 0)

    def test_space_homoglyphs_replaced_when_asked(self):
        out, stats = clean_markdown("가 나　다", normalize_spaces=True)
        self.assertEqual(out, "가 나 다")
        self.assertEqual(stats["replaced_count"], 2)

    def test_no_nfkc_or_confusable_rewrite(self):
        src = "전각 Ａ, 원문자 ①, 키릴 а, 합자 ﬁ"
        out, _ = clean_markdown(src)
        self.assertEqual(out, src)


class CleanTextCliTest(unittest.TestCase):
    def test_writes_new_file_and_keeps_input(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.md"
            src.write_text(f"가{ZW}나\r\n다\r\n", encoding="utf-8", newline="")
            before = src.read_bytes()
            r = run_cli(src)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(src.read_bytes(), before)
            out = Path(d) / "a.cleaned.md"
            self.assertEqual(out.read_bytes(), "가나\r\n다\r\n".encode())

    def test_refuses_to_overwrite_input(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.md"
            src.write_text(f"가{ZW}나", encoding="utf-8")
            r = run_cli(src, "-o", src)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(src.read_text(encoding="utf-8"), f"가{ZW}나")

    def test_refuses_existing_output_without_force(self):
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "a.md", Path(d) / "b.md"
            src.write_text(f"가{ZW}나", encoding="utf-8")
            out.write_text("keep", encoding="utf-8")
            self.assertEqual(run_cli(src, "-o", out).returncode, 2)
            self.assertEqual(out.read_text(encoding="utf-8"), "keep")
            self.assertEqual(run_cli(src, "-o", out, "--force").returncode, 0)
            self.assertEqual(out.read_text(encoding="utf-8"), "가나")

    def test_check_mode_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as d:
            dirty, clean = Path(d) / "dirty.md", Path(d) / "clean.md"
            dirty.write_text(f"가{ZW}나", encoding="utf-8")
            clean.write_text("가 나 `x​y`", encoding="utf-8")
            self.assertEqual(run_cli(dirty, "--check").returncode, 1)
            # 공백 동형 문자와 코드 안 문자는 기본 정리 대상이 아니므로 통과
            self.assertEqual(run_cli(clean, "--check").returncode, 0)
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ["clean.md", "dirty.md"])


if __name__ == "__main__":
    unittest.main()
