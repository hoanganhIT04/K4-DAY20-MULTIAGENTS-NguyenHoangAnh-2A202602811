# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Hoàng Anh | 2A202602811 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline):
- H2 (skills-auto so với baseline):
- H3 (tác vụ học so với tác vụ đánh giá):

## 3. Làm quen Deep Agents (Phần 0.3)

1.
2.
3.

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | B | `the original files in tests/ must not be modified (new test files are allowed)` |
| `code-learn` | `parse_price_all_formats` | D | `wrong for: ['(12.00)']` |
| `code-learn` | `csv_quoting_follows_docstring` | A | `to_csv_row returned 'Desk, large "oak",10.00,2'` |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function (name not starting with '_') in the package has type annotations...` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed...` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased'...` |
| `data-learn` | `north_q1_revenue` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `north_q1_orders` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `top_region` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `missing_amount_orders` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `duplicate_rows_removed` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `rule_money_in_cents` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `rule_meta_block` | G | `FileNotFoundError: answer.json (GraphRecursionError limit 60 reached)` |
| `data-learn` | `rule_clean_csv` | G | `RULE: write workspace/clean.csv... (GraphRecursionError limit 60 reached)` |
| `logs-learn` | `entry_count` | D | `wrong number of entries (got 9)` |
| `logs-learn` | `timestamps_utc` | D | `3/25 timestamps match` |
| `logs-learn` | `exception_fields` | D | `22 wrong exception values` |
| `logs-learn` | `repeat_counts` | D | `22 wrong repeat_count values` |
| `logs-learn` | `counts_by_service` | D | `counts_by_service: wrong values` |
| `logs-learn` | `rule_service_names` | E | `RULE: service names in the output are lower-case with '-' replaced by '_'` |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Nhận xét:
- **Phân bố 22 failed checks theo nhóm (A-G):** A: 1, B: 1, C: 0, D: 6, E: 6, F: 0, G: 8.
- **Hạng mục cao nhất:** Nhóm D (Bỏ sót dữ liệu bẩn/định dạng) và Nhóm E (Vi phạm quy ước tổ chức Acme `rule_`) đồng hạng cao nhất với 6 failed checks mỗi nhóm trong các check thực thi hoàn thành.
- **Thống kê từ `scripts/check_breakdown.py`:**
  - Technical checks đạt **5/18** (27.8%) ở đường cơ sở (`code-learn`: 4, `logs-learn`: 1).
  - House-rule checks (`rule_`) đạt **0/9** (0.0%). Điều này cho thấy toàn bộ các check quy ước Acme (`rule_`) trong bộ học đều thất bại ở đường cơ sở, phù hợp với sự hiện diện của Nhóm E trong các failed-check evidence.
- **Lỗi thực thi/runtime (Nhóm G):** Tác vụ `data-learn` gặp `GraphRecursionError` (chương trình dừng khi đạt giới hạn `recursion_limit` 60 bước trước khi ghi file đầu ra `answer.json` và `clean.csv`), dẫn đến 8 check thất bại do không tìm thấy file output (`FileNotFoundError`).
- **Khả năng phòng ngừa của Skill:** Skill có thể giúp phòng ngừa Nhóm E bằng cách trích xuất các quy ước `RULE:` từ trường `detail` của phản hồi thất bại ở tác vụ học để bổ sung vào ngữ cảnh của tác tử.

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):**
  1. `explorer`: Khám phá, đọc README, docstring, dữ liệu bẩn và log; báo cáo hiện trạng; không sửa đổi tệp (Read-only).
  2. `implementer`: Thực hiện chỉnh sửa mã nguồn/dữ liệu, tạo file đầu ra và chạy test/script kiểm tra (Mutator & Tester).
  3. `reviewer`: Kiểm tra độc lập tệp kết quả so với đề bài và quy ước Acme trước khi kết thúc (Independent Auditor).
- **`subagent_calls` ở từng tác vụ và nhận xét:**
  - `code-learn`: `0` calls. Tác tử chính hoàn thành workflow bằng các công cụ tệp và shell trực tiếp mà không phát sinh lệnh giao việc.
  - `data-learn`: `0` calls. Tác tử chính lặp đệ quy đạt giới hạn 60 bước (`GraphRecursionError`) trước khi phát sinh lệnh giao việc.
  - `logs-learn`: `1` call. Tác tử chính đã gọi subagent `implementer` thông qua công cụ `task`.
- **Thông tin thiếu hoặc thừa khi giao việc (`logs-learn`):**
  - Lời giao việc chứa các yêu cầu tác vụ, đường dẫn `workspace/app.log` và mẫu cấu hình JSON trong tham số `description`.
  - Subagent `implementer` hoạt động trong ngữ cảnh cô lập (context isolation), phân tích tệp log, ghi file `workspace/errors.json` và trả về báo cáo kết quả cho tác tử chính.
- **Ảnh hưởng đến token và thời gian:**
  - `logs-learn`: Token tăng từ 19,502 (`baseline`) lên 88,460 (`subagents`), thời gian tăng từ 13.1s lên 189.5s do chi phí bổ sung system prompt (`SUBAGENTS_NOTE`, `PATHS_NOTE`), khởi tạo subagent và trao đổi báo cáo.
  - Token trung bình toàn bộ điều kiện: Tăng từ 139,635 tokens (`baseline`) lên 166,489 tokens (`subagents`) (tăng 19.2% overhead).

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| | | | |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
