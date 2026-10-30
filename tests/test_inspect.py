import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import FIXTURES, SCRIPTS, load_inspect, png_chunk

ins = load_inspect()


class PiiTest(unittest.TestCase):
    def found(self, text):
        return {name: [m.group(0) for m in pat.finditer(text)] for name, pat in ins.PII_PATTERNS.items()}

    def test_detects_candidates(self):
        f = self.found("서버 10.0.0.255 접속, 메일 a.b+c@mail.example.co.kr, 폰 010-9876-5432, 01012345678, 번호 900101-1234567")
        self.assertEqual(f["IPv4"], ["10.0.0.255"])
        self.assertEqual(f["이메일"], ["a.b+c@mail.example.co.kr"])
        self.assertEqual(f["휴대폰 번호"], ["010-9876-5432", "01012345678"])
        self.assertEqual(f["주민등록번호 형식"], ["900101-1234567"])

    def test_ignores_non_candidates(self):
        f = self.found("버전 1.2.3.4.5, 값 256.1.1.1, 금액 1,000원, 날짜 2026. 10. 30., 시간 14:00, 전화 02-123-4567")
        self.assertEqual(sum(len(v) for v in f.values()), 0, f)

    def test_report_masks_values(self):
        text = "IP 192.168.10.20 메일 someone@example.com"
        out = ins.inspect_text(text)
        self.assertIn("개인정보 후보: 2곳", out)
        self.assertNotIn("192.168.10.20", out)
        self.assertNotIn("someone@example.com", out)


class HiddenReportTest(unittest.TestCase):
    def test_counts_lines_and_code_marker(self):
        out = ins.inspect_text((FIXTURES / "hidden_sample.md").read_text(encoding="utf-8"))
        self.assertIn("숨은 문자: 9개", out)
        self.assertIn("U+200B ZERO WIDTH SPACE (Cf) x3  위치: 3줄, 10줄(코드), 13줄(코드)", out)
        self.assertIn("공백 동형 문자: 2개", out)
        self.assertIn("U+3164 HANGUL FILLER (Lo) x1  위치: 7줄", out)


class ImageReportTest(unittest.TestCase):
    def test_lists_png_text_keyword(self):
        png = (b"\x89PNG\r\n\x1a\n" + png_chunk(b"IHDR", bytes(13)) + png_chunk(b"tEXt", b"Software\x00x")
               + png_chunk(b"IDAT", b"") + png_chunk(b"IEND", b""))
        out = ins.inspect_image(png)
        self.assertIn("지울 메타데이터: 1개", out)
        self.assertIn("키워드: Software", out)

    def test_cli_is_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "a.md"
            src.write_bytes((FIXTURES / "hidden_sample.md").read_bytes())
            before = src.read_bytes()
            r = subprocess.run([sys.executable, str(SCRIPTS / "inspect_report.py"), str(src)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("숨은 문자: 9개", r.stdout)
            self.assertEqual(src.read_bytes(), before)
            self.assertEqual([p.name for p in Path(d).iterdir()], ["a.md"])


if __name__ == "__main__":
    unittest.main()
