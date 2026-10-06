"""GUIDE Phần 3 - Người tuyển chọn skill (skill curator): tự viết skill từ các lần chạy thất bại.   >>> SINH VIÊN CÀI ĐẶT curate_skills <<<

Pseudo-code: guides/pseudocode/04_curator.md
Kiểm tra:    pytest tests/test_04_curator.py
Chạy thật:   python -m lab.curator
"""
import json
import re
from pathlib import Path

from .tasks import eval_markers   # có sẵn: định danh của tác vụ đánh giá, tính lúc chạy

# ---- CÓ SẴN, KHÔNG SỬA: kiểm tra và tách khối skill (phần dễ sai và liên quan bảo mật) ----------------
SAFE_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_skill(text: str, expected_name: str | None = None) -> list[str]:
    """Kiểm tra nội dung một SKILL.md. Trả về danh sách vấn đề (rỗng = hợp lệ).

    Quy tắc: có khối YAML frontmatter; `name` chữ thường/số/gạch ngang (tối đa 64 ký tự) và bằng `expected_name`
    nếu được truyền; có `description` (tối đa 1024 ký tự); phần thân tối đa 80 dòng; không chứa chuỗi nào của
    `eval_markers()`. Quy tắc về `name` cũng là biện pháp bảo mật: tên khối do LLM sinh ra được dùng để tạo
    đường dẫn, nên `../evil` không được lọt qua.
    """
    problems = []
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text.strip() + "\n", re.S)
    if not m:
        return ["missing YAML frontmatter"]
    front, body = m.groups()
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    n = name.group(1).strip() if name else ""
    if not SAFE_NAME.fullmatch(n) or len(n) > 64:
        problems.append("invalid name")
    elif expected_name is not None and n != expected_name:
        problems.append("name differs from the block name")
    if not desc or len(desc.group(1).strip()) > 1024:
        problems.append("missing or too long description")
    if len(body.strip().splitlines()) > 80:
        problems.append("body longer than 80 lines")
    low = text.lower()
    for marker in eval_markers():
        if marker in low:
            problems.append(f"mentions evaluation material: {marker}")
    return problems


def parse_skill_blocks(reply: str) -> list[tuple[str, str]]:
    """Tách câu trả lời của LLM thành danh sách (name, nội dung SKILL.md).

    Khuôn dạng: `=== SKILL: <name> ===` ... `=== END ===`. Một khối kết thúc ở điểm nào đến trước trong ba điểm:
    `=== END ===`, tiêu đề `=== SKILL:` kế tiếp, hoặc cuối văn bản (LLM đôi khi quên dòng END).
    """
    pattern = re.compile(r"^=== SKILL: (\S+) ===[ \t]*\n(.*?)(?=^=== END ===|^=== SKILL: |\Z)", re.S | re.M)
    return [(name, text.strip()) for name, text in pattern.findall(str(reply))]
# --------------------------------------------------------------------------------------------------


def curate_skills(results_dir="results", source_condition="baseline", out_dir=None, model=None, max_skills: int = 3) -> list[Path]:
    """Đọc các lần chạy của TÁC VỤ HỌC (role == "learn") trong `source_condition`, nhờ LLM viết skill, ghi file.

    Các bước: nạp run.json + trace.md -> (nếu không có check nào thất bại: in cảnh báo và trả về [] mà KHÔNG gọi LLM)
    -> dựng prompt -> model.invoke(prompt) -> parse_skill_blocks -> validate_skill(text, expected_name=name)
    -> ghi `<out_dir>/<name>/SKILL.md`. Mặc định `out_dir` = <gốc lab>/skills/auto (dùng `ROOT` từ lab.tasks).
    Giữ tối đa `max_skills` skill hợp lệ; skill không hợp lệ bị bỏ qua.
    Prompt chứa, với mỗi check thất bại, TÊN và trường `detail` (lời nhận xét của bot đánh giá: phát biểu quy tắc bị vi phạm)
    cùng phần cuối của vết (trace). Với tác vụ học, `detail` chỉ phát biểu quy tắc, không chứa đáp án.
    Tuyệt đối KHÔNG đưa dữ liệu của tác vụ đánh giá (role == "eval") vào prompt.
    model mặc định: make_model() (lab.model).
    Trả về: danh sách đường dẫn SKILL.md đã ghi.
    """
    if out_dir is None:
        from .tasks import ROOT
        out_dir = ROOT / "skills" / "auto"
    else:
        out_dir = Path(out_dir)

    results_dir = Path(results_dir)
    runs = []

    for run_file in sorted(results_dir.glob(f"{source_condition}/*/run.json")):
        try:
            r = json.loads(run_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        if r.get("role") != "learn":
            continue

        trace_file = run_file.parent / "trace.md"
        trace_text = ""
        if trace_file.exists():
            trace_text = trace_file.read_text(encoding="utf-8")[-6000:]

        failed = [
            (c.get("name"), c.get("detail", ""))
            for c in r.get("checks", [])
            if not c.get("passed")
        ]

        if failed:
            runs.append({
                "task": r.get("task", run_file.parent.name),
                "failed": failed,
                "trace": trace_text,
            })

    if not runs or not any(run["failed"] for run in runs):
        print("Cảnh báo: không có check thất bại ở tác vụ học")
        return []

    if model is None:
        from .model import make_model
        model = make_model()

    prompt_lines = [
        "You are writing skills for a software engineering agent.",
        "Below are failed checks (check name and reviewer feedback) and execution traces from learning runs.",
        f"Find common process/procedural issues (not task-specific answers) and write up to {max_skills} concise skills",
        "to prevent these errors on NEW tasks of the same kind.",
        "",
        "Rules:",
        "- Skills must be general: do not mention task IDs, specific filenames of a task, answers, or exact numbers.",
        "- Each skill has YAML frontmatter with `name` (lowercase, hyphens) and `description` (one sentence: USE WHEN...),",
        "  followed by at most 40 lines of imperative checklist/instructions.",
        "- Output format, exact match:",
        "=== SKILL: <name> ===",
        "---",
        "name: <name>",
        "description: <use when...>",
        "---",
        "<body content>",
        "=== END ===",
        "",
        "LEARNING RUN FAILURES AND TRACES:",
    ]

    for run in runs:
        prompt_lines.append(f"\nTask: {run['task']}")
        prompt_lines.append("Failed checks:")
        for check_name, detail in run["failed"]:
            prompt_lines.append(f"- {check_name}: {detail}")
        if run["trace"]:
            prompt_lines.append(f"Trace excerpt:\n{run['trace']}")

    prompt = "\n".join(prompt_lines)
    reply = model.invoke(prompt).content

    written_paths = []
    for name, text in parse_skill_blocks(reply):
        if len(written_paths) >= max_skills:
            break
        problems = validate_skill(text, expected_name=name)
        if problems:
            continue

        skill_dir = out_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(text, encoding="utf-8")
        written_paths.append(skill_file)

    return written_paths


if __name__ == "__main__":
    for p in curate_skills():
        print("wrote", p)
