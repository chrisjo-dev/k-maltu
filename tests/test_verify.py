import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import SCRIPTS

from verify import parse_char, verify

ORIGINAL = """# 제목

속도는 21Mbps에서 92Mbps로 올랐다. 지연은 40ms였다.
자세한 내용은 [애플 문서](https://developer.apple.com/forums/thread/97805)와 https://example.com/a?b=1 참고.

![화면](images/a.png)

```sh
sudo ifconfig awdl0 down
```

인라인 `ping -c 10` 도 있다.
"""


def status_of(rows, item):
    return next(s for s, i, _ in rows if i == item)


class VerifyTest(unittest.TestCase):
    def test_identical_passes(self):
        rows, ok = verify(ORIGINAL, ORIGINAL)
        self.assertTrue(ok)
        self.assertTrue(all(s == "PASS" for s, _, _ in rows))

    def test_style_change_only_passes(self):
        result = ORIGINAL.replace("올랐다", "뛰었음").replace("[애플 문서]", "[애플 포럼 글]")
        rows, ok = verify(ORIGINAL, result)
        self.assertTrue(ok, rows)

    def test_number_change_fails(self):
        rows, ok = verify(ORIGINAL, ORIGINAL.replace("92Mbps", "90Mbps"))
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "숫자"), "FAIL")

    def test_dropped_number_fails(self):
        rows, ok = verify(ORIGINAL, ORIGINAL.replace(" 지연은 40ms였다.", ""))
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "숫자"), "FAIL")

    def test_link_target_change_fails(self):
        result = ORIGINAL.replace("thread/97805)", "thread/97806)")
        rows, ok = verify(ORIGINAL, result)
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "링크 주소"), "FAIL")
        self.assertEqual(status_of(rows, "URL"), "FAIL")

    def test_bare_url_change_fails(self):
        rows, ok = verify(ORIGINAL, ORIGINAL.replace("example.com/a?b=1", "example.com/a"))
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "URL"), "FAIL")

    def test_image_path_change_fails(self):
        rows, ok = verify(ORIGINAL, ORIGINAL.replace("images/a.png", "images/b.png"))
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "이미지 경로"), "FAIL")

    def test_code_change_fails(self):
        for before, after in [("awdl0 down", "awdl0 up"), ("`ping -c 10`", "`ping -c 5`")]:
            rows, ok = verify(ORIGINAL, ORIGINAL.replace(before, after))
            self.assertFalse(ok)
            self.assertEqual(status_of(rows, "코드 블록"), "FAIL")

    def test_middle_dot_forbidden(self):
        dot = parse_char("U+00B7")
        self.assertEqual(dot, "\u00b7")
        rows, ok = verify(ORIGINAL, ORIGINAL.replace("와 https", "\u00b7 https"), forbid=[dot])
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "금지 문자 U+00B7"), "FAIL")
        rows, ok = verify(ORIGINAL, ORIGINAL, forbid=[dot])
        self.assertTrue(ok)

    def test_hidden_char_left_fails(self):
        rows, ok = verify(ORIGINAL, ORIGINAL.replace("속도는", "속도​는"))
        self.assertFalse(ok)
        self.assertEqual(status_of(rows, "숨은 문자"), "FAIL")

    def test_hidden_char_inside_number_in_original_is_ignored(self):
        rows, ok = verify(ORIGINAL.replace("92", "9​2"), ORIGINAL)
        self.assertTrue(ok, rows)

    def test_short_result_is_warning_not_failure(self):
        result = ORIGINAL + ""
        long_original = ORIGINAL + "\n" + "덧붙인 문장이 아주 길게 이어진다. " * 20
        rows, ok = verify(long_original, result)
        self.assertTrue(ok)
        self.assertEqual(status_of(rows, "분량"), "WARN")

    def test_image_file_existence(self):
        with tempfile.TemporaryDirectory() as d:
            rows, ok = verify(ORIGINAL, ORIGINAL, result_dir=Path(d))
            self.assertFalse(ok)
            self.assertEqual(status_of(rows, "이미지 파일"), "FAIL")
            (Path(d) / "images").mkdir()
            (Path(d) / "images" / "a.png").write_bytes(b"x")
            rows, ok = verify(ORIGINAL, ORIGINAL, result_dir=Path(d))
            self.assertTrue(ok)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.md", Path(d) / "b.md"
            text = ORIGINAL.replace("![화면](images/a.png)", "")
            a.write_text(text, encoding="utf-8")
            b.write_text(text.replace("는", "는\u00b7"), encoding="utf-8")
            run = lambda *x: subprocess.run([sys.executable, str(SCRIPTS / "verify.py"), *map(str, x)],  # noqa: E731
                                            capture_output=True, text=True)
            self.assertEqual(run(a, a).returncode, 0)
            r = run(a, b, "--forbid", "U+00B7")
            self.assertEqual(r.returncode, 1)
            self.assertIn("[FAIL] 금지 문자 U+00B7", r.stdout)


if __name__ == "__main__":
    unittest.main()
