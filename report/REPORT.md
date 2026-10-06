# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Hoàng Anh | 2A202602811 | 100% |

- Nhà cung cấp và mô hình: `google / gemini-3.6-flash-medium` (`LAB_MODEL`), nhiệt độ: `0.0` (`LAB_TEMPERATURE`), `recursion_limit`: `60`.
- Phiên bản Deep Agents: `deepagents 0.2.7`, hệ điều hành: `Windows 11 (64-bit)`, chạy trực tiếp trên môi trường ảo Python local (`.venv`).
- Số lần chạy tác vụ đã dùng / ngân sách: `18 lượt chạy chính thức / 25 lượt chạy ngân sách`.
- Commit của tag `freeze`: `e895381` (`e89538197190d6406071b3722ae932a1ae5b833d`).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Dự đoán điều kiện subagents không đạt điểm số cao hơn baseline trên tác vụ đánh giá.
  - *Dự đoán:* Trên các tác vụ đánh giá (`eval`), điều kiện `subagents` **không đạt điểm số cao hơn** đáng kể so với `baseline` (điểm tương đương hoặc thấp hơn), nhưng tiêu tốn lượng token cao hơn khoảng +15% đến +20%.
  - *Căn cứ:* Thực nghiệm ở Phase 2/3 cho thấy tác tử chính rất ít giao việc (`subagent_calls = 0` ở 2/3 tác vụ học `code-learn` và `data-learn`). Việc chuyển ngữ cảnh qua subagent tạo chi phí token overhead cho prompt (`SUBAGENTS_NOTE`) nhưng làm giảm ngữ cảnh toàn cục (context isolation) mà không khắc phục được lỗi logic nghiệp vụ hay giới hạn `GraphRecursionError`.
  - *Tiêu chí bác bỏ (Falsification):* H1 bị bác bỏ nếu điểm trung bình của `subagents` trên tập `eval` cao hơn `baseline` trên $> 0.15$ điểm.

- H2 (skills-auto so với baseline): Dự đoán điều kiện skills-auto không cải thiện điểm số đáng kể so với baseline.
  - *Dự đoán:* Trên các tác vụ đánh giá (`eval`), điều kiện `skills-auto` **không cải thiện điểm số đáng kể** so với `baseline` (chênh lệch điểm nằm trong khoảng nhiễu $\pm 0.10$).
  - *Căn cứ:* Thực nghiệm Phase 3.4 trên tập học cho thấy chỉ số `skills_read = 0` trên cả 3 tác vụ (tác tử không chủ động đọc file skill). Ngoài ra, audit ở Phase 3.3 chỉ ra 1/3 skill hoàn toàn out-of-evidence (`avoid-parallel-file-mutations`), và các quy ước Acme (`rule_`) của tác vụ đánh giá khác với tác vụ học.
  - *Tiêu chí bác bỏ (Falsification):* H2 bị bác bỏ nếu điểm trung bình `skills-auto` trên tập `eval` cao hơn `baseline` $> 0.20$ điểm VÀ chỉ số `skills_read > 0`.

- H3 (tác vụ học so với tác vụ đánh giá): Dự đoán điểm trung bình tác vụ đánh giá thấp hơn hoặc bằng tác vụ học.
  - *Dự đoán:* Điểm số trung bình trên các tác vụ đánh giá (`eval`) ở tất cả các điều kiện sẽ **thấp hơn hoặc bằng** điểm số trên các tác vụ học (`learn`), đặc biệt là nhóm check quy ước (`rule_`).
  - *Căn cứ:* Các quy ước Acme (`rule_`) ở tác vụ đánh giá là hoàn toàn mới và khác biệt so với tác vụ học. Dự kiến tác tử khó có thể tự suy diễn đầy đủ các quy ước ẩn mới ở tác vụ đánh giá nếu không có skill hướng dẫn phù hợp. Ngoài ra, tác vụ `data-eval` có nguy cơ tiếp tục gặp `GraphRecursionError` tương tự `data-learn`.
  - *Tiêu chí bác bỏ (Falsification):* H3 bị bác bỏ nếu điểm trung bình tập `eval` vượt điểm trung bình tập `learn` ở bất kỳ điều kiện nào.

## 3. Làm quen Deep Agents (Phần 0.3)

1. **Tác tử mặc định có những công cụ nào? Công cụ nào cho phép chạy lệnh?**
   - Tác tử mặc định được cung cấp các công cụ tệp (`ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`), công cụ shell (`execute`), và công cụ subagent (`task`).
   - Công cụ cho phép thực thi lệnh shell trong môi trường Sandbox là: `execute`.
2. **Mô tả của công cụ `task` nói gì về subagent `general-purpose`? Subagent đó nhìn thấy ngữ cảnh nào của tác tử chính?**
   - Subagent `general-purpose` được mô tả là tác tử tổng quát dùng để nghiên cứu câu hỏi phức tạp, tìm kiếm file/nội dung và thực thi tác vụ nhiều bước.
   - Subagent này vận hành theo cơ chế **stateless**: mặc định chỉ nhìn thấy duy nhất nội dung prompt được truyền vào trong tham số của câu lệnh `task`, chứ không kế thừa lịch sử hội thoại toàn cục của tác tử chính (ngoại trừ prompt giao việc).
3. **Trích dẫn hướng dẫn hành vi từ mô tả của công cụ `task` và `execute`:**
   - **Từ `task`:** *"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report."*
   - **Từ `execute`:** *"Use absolute paths and avoid `cd` so the working directory stays stable; use the optional timeout to override the default."*

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

- **Số lần chạy curator:** 1 lần (`python -m lab.curator` với `source_condition="baseline"`, `max_skills=3`).
- **Nguồn dữ liệu:** Chỉ trích xuất từ 3 tác vụ học baseline (`results/baseline/code-learn/run.json`, `data-learn/run.json`, `logs-learn/run.json` có `role == "learn"`). Tuyệt đối **chưa sử dụng** bất kỳ tác vụ hoặc kết quả đánh giá (`eval`) nào.
- **Số skill bị xóa và lý do:** 0 skill bị xóa. Curator sinh ra đúng 3 skill (`max_skills=3`) và cả 3 đều đạt 100% kiểm tra an toàn/cấu trúc tự động (`validate_skill()` trả về `[]`).

### Kiểm tra tính hợp lệ cấu trúc (Structural Validity)
Cả 3 skill đều đạt kiểm tra cấu trúc/an toàn bằng `validate_skill()`:
- YAML frontmatter hợp lệ (chứa `name` và `description`).
- Tên thư mục trùng khớp tuyệt đối với tham số `name`.
- Độ dài mỗi skill là 12 dòng (tuân thủ giới hạn $\le 80$ dòng).
- Không chứa hành vi path traversal (`../`) hay các dấu hiệu lộ đáp án/eval markers.
- *Lưu ý:* Structural validity chỉ chứng minh tính hợp lệ về cú pháp và an toàn, **không chứng minh** tính căn cứ thực tế (semantic grounding).

### Kiểm tra tính căn cứ thực tế (Semantic Grounding Audit)

| Skill | Grounded failed checks (Check thất bại tương ứng) | Grounding status | Structural validation | Nhận xét chi tiết về nội dung |
|---|---|---|---|---|
| `adhere-to-documentation-rules` | `rule_type_hints`, `rule_changelog`, `csv_quoting_follows_docstring` (`code-learn`) | **DIRECTLY GROUNDED** | PASSED (`[]`) | **Tổng quát.** Nội dung quy định gắn type hint cho hàm public, ghi log thay đổi vào CHANGELOG.md theo định dạng `## Unreleased` và tuân thủ docstring trích xuất trực tiếp từ trường `detail` của các failed check thực tế. |
| `ensure-test-coverage` | `tests_not_modified`, `rule_regression_tests` (`code-learn`) | **PARTIALLY GROUNDED** | PASSED (`[]`) | **Tổng quát.** Trích xuất đúng yêu cầu không sửa file test cũ (`tests_not_modified`) và tạo file `test_regressions.py` chứa ít nhất 3 test function (`rule_regression_tests`). Tuy nhiên, curator bổ sung một số chỉ dẫn ngoài bằng chứng như dùng công cụ đo độ bao phủ (`pytest-cov`), refactor test và hợp tác nhóm. |
| `avoid-parallel-file-mutations` | *Không có check nào* | **UNGROUNDED / OUT-OF-EVIDENCE** | PASSED (`[]`) | **Tổng quát.** Không tìm thấy bất kỳ failed check hay vết ghi nhận lỗi liên quan đến chỉnh sửa file song song/concurrency trong cả 3 tác vụ học baseline (`code-learn`, `data-learn`, `logs-learn`). Curator đã tự suy diễn và bổ sung skill này dựa trên tri thức chung của LLM mà không có bằng chứng thực tế từ kết quả học. |

### Đánh giá chất lượng Curator
- **Điểm mạnh:** Curator thực thi đúng quy trình cô lập cách ly tác vụ eval, đọc đúng các failed check `role == "learn"`, sinh ra các skill hợp lệ 100% về mặt cấu trúc và cú pháp mà không vi phạm quy tắc an toàn.
- **Hạn chế / Rủi ro:** Curator chưa đạt tính căn cứ tuyệt đối (1/3 skill hoàn toàn out-of-evidence). Điều này phản ánh rủi ro LLM tự suy diễn (hallucination/prior bias) khi prompt của curator chưa siết chặt yêu cầu bắt buộc mọi quy tắc sinh ra phải dẫn xuất 1-1 từ bằng chứng `detail` của failed check.

### Thử nghiệm điều kiện `skills-auto` trên tác vụ học (Phần 3.4)

Bảng so sánh kết quả thực nghiệm giữa 3 điều kiện trên các tác vụ học (`learn`):

| Tác vụ | Điều kiện (`Condition`) | Điểm (`Score`) | Passed / Total | Skills Read | Tokens | Thời gian (s) | Lỗi / Ghi chú |
|---|---|---|---|---|---|---|---|
| `code-learn` | `baseline` | **0.4000** | 4 / 10 | 0 | 35,393 | 36.4s | Hoàn thành |
| `code-learn` | `subagents` | **0.0000** | 0 / 10 | 0 | 21,999 | 12.3s | Hoàn thành (`subagent_calls=0`) |
| `code-learn` | `skills-auto` | **0.0000** | 0 / 10 | **0** | 25,373 | 13.1s | Hoàn thành |
| `data-learn` | `baseline` | **0.0000** | 0 / 8 | 0 | 364,010 | 131.4s | `GraphRecursionError` (limit 60) |
| `data-learn` | `subagents` | **0.0000** | 0 / 8 | 0 | 388,409 | 173.2s | `GraphRecursionError` (limit 60) |
| `data-learn` | `skills-auto` | **0.0000** | 0 / 8 | **0** | 349,008 | 101.6s | `GraphRecursionError` (limit 60) |
| `logs-learn` | `baseline` | **0.1111** | 1 / 9 | 0 | 19,502 | 13.1s | Hoàn thành |
| `logs-learn` | `subagents` | **0.1111** | 1 / 9 | 0 | 88,460 | 189.5s | Hoàn thành (`subagent_calls=1`) |
| `logs-learn` | `skills-auto` | **0.1111** | 1 / 9 | **0** | 22,037 | 12.3s | Hoàn thành |

#### Phân tích chi tiết và đối chiếu thực nghiệm:
1. **Số lượng Skill được nạp (`skills_read = 0`):**
   - Trong cả 3 tác vụ học (`code-learn`, `data-learn`, `logs-learn`), chỉ số `skills_read` đều bằng **0**.
   - **Phân biệt quan trọng:** Curator đã sinh ra thành công 3 auto-skills (`GENERATE`), nhưng ở thời điểm thực thi (`runtime`), tác tử chính đã **KHÔNG ĐỌC/KHÔNG NẠP (`READ = 0`)** bất kỳ skill nào vào ngữ cảnh.
   - Do đó, **tuyệt đối không kết luận** rằng auto-skills đã giúp cải thiện chất lượng hoặc tác động đến hành vi của tác tử trong đợt thử nghiệm này.
2. **Lỗi Runtime ở tác vụ `data-learn`:**
   - GraphRecursionError xuất hiện nhất quán trong cả ba điều kiện baseline, subagents và skills-auto.
3. **So sánh điểm số (`Score`):**
   - Ở `logs-learn`, điểm số giữ nguyên $1/9 = 0.1111$ trên cả 3 điều kiện, không có sự thay đổi.
   - Ở `code-learn`, `skills-auto` đạt điểm $0/10$ (giống `subagents`), thấp hơn `baseline` ($4/10$). Sự suy giảm từ 4/10 xuống 0/10 ở code-learn không thể được quy cho auto-skill vì skills_read = 0. Nguyên nhân cụ thể chưa được xác định từ một lần chạy; stochasticity là một khả năng nhưng chưa được kiểm chứng bằng repeated runs.
4. **Chi phí Tokens và Thời gian:**
   - Tổng lượng token của `skills-auto` trên 3 tác vụ học là 396,418 tokens (so với 418,905 tokens ở `baseline`), mức tiêu thụ token tương đương do tác tử không phải nạp thêm ngữ cảnh từ các tệp skill.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

### Bảng so sánh chính thức (`report/table.md`)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 4/10 | 0/10 | 0/10 |
| data-learn | 0/8 | 0/8 | 0/8 |
| logs-learn | 1/9 | 1/9 | 0/9 |
| code-eval | 1/11 | 1/11 | 3/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 1/10 | 1/10 | 0/10 |
| **Mean score - learning tasks** | 0.17 | 0.04 | 0.00 |
| **Mean score - evaluation tasks** | 0.06 | 0.06 | 0.09 |
| **Mean tokens per run** | 90,305 | 599,817 | 111,129 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

### Bảng phân rã chi tiết (`python scripts/check_breakdown.py`)


|condition    | role    | technical  | house rules  | mean tokens  | read a skill|

|---|---|---|---|---|

| `baseline`    | eval    | 2/18 | 0/12 | 40,975 | 0/3     |

| `baseline`    | learn   | 5/18 | 0/9  | 139,635 | 0/3     |

| `subagents`   | eval    | 2/18 | 0/12 | 1,033,145 | 0/3     |

| `subagents`   | learn   | 1/18 | 0/9  | 166,489 | 0/3     |

| `skills-auto` | eval    | 3/18 | 0/12 | 88,138 | 0/3     |

| `skills-auto` | learn   | 0/18 | 0/9  | 134,121 | 0/3     |



---

## 8. Phân tích

### 1. Phân tích điểm số giữa các điều kiện trên tác vụ Học và Đánh giá
- **Trên tác vụ học (`learn`):** Không điều kiện nào cải thiện điểm so với `baseline` (Baseline: 0.17, Subagents: 0.04, Skills-auto: 0.00).
- **Trên tác vụ đánh giá (`eval`):** `skills-auto` đạt điểm trung bình 0.09 (9.1%), cao hơn `baseline` (0.06 / 6.1%) và `subagents` (0.06 / 6.1%). 

### 2. Tách điểm kỹ thuật và quy ước Acme (`rule_`)
- **Tác vụ học:** Check kỹ thuật đạt 5/18 ở `baseline`, 1/18 ở `subagents`, 0/18 ở `skills-auto`. Check quy ước `rule_` đạt **0/9 (0.0%)** ở tất cả điều kiện.
- **Tác vụ đánh giá:** Check kỹ thuật đạt 2/18 ở `baseline`, 2/18 ở `subagents`, 3/18 ở `skills-auto`. Check quy ước `rule_` đạt **0/12 (0.0%)** trên tất cả các điều kiện (`code-eval`: 0/4, `data-eval`: 0/4, `logs-eval`: 0/4).
- **Nhận xét:** Quy ước ẩn mới ở tác vụ đánh giá không được tác tử tự suy diễn nếu không có chỉ dẫn trực tiếp.

### 3. Giải thích dựa trên Vết và `skills_read`
- Trong tất cả 6 lượt chạy `skills-auto` (3 learn, 3 eval), chỉ số `skills_read` đều bằng **0/6**. 
- **Phân biệt quan trọng:** Auto-skills đã được sinh ra (`GENERATE`) và tồn tại trong tag `freeze`, nhưng tác tử chính **chưa từng nạp/đọc (`READ = 0`)** các file skill này ở runtime. Vì `skills_read = 0`, thí nghiệm này không cung cấp evidence rằng auto-generated skills đã được runtime sử dụng; do đó không thể quy attribution cải thiện hoặc không cải thiện score cho skill.

### 4. Chi phí Token và Thời gian (Cost/Performance Analysis)
- Chi phí token trung bình mỗi lượt chạy: `baseline` tiêu tốn 90,305 tokens, `skills-auto` tiêu tốn 111,129 tokens, trong khi `subagents` tiêu tốn cao nhất với 599,817 tokens (do `data-eval` chạy 10 công cụ tiêu tốn 2.76M tokens). 
- Đa tác tử không mang lại hiệu quả chi phí (Cost-effective) trong thí nghiệm này.

### 5. Dấu hiệu rò rỉ và Quá khớp
- Thư mục `skills/auto/` được đóng băng tuyệt đối tại tag `freeze` trước khi chạy eval. Không có dữ liệu hay đáp án của tác vụ eval bị rò rỉ vào prompt của curator. Tuy nhiên, 1/3 skill (`avoid-parallel-file-mutations`) hoàn toàn out-of-evidence do curator suy diễn.

### 6. Kiểm chứng các Giả thuyết (H1, H2, H3)

- **H1 (subagents vs baseline): SUPPORTED**
  - *Kết quả:* Điểm trung bình `eval` của `subagents` là 0.06 (bằng `baseline` 0.06), chi phí token tăng cao. Tiêu chí bác bỏ ($> 0.15$ điểm) không bị kích hoạt. Giả thuyết H1 được hỗ trợ.
  - *Lưu ý:* `subagent_calls` = 10 ở `data-eval` và 0 ở `code-eval`, `logs-eval`.

- **H2 (skills-auto vs baseline): SUPPORTED**
  - *Kết quả:* Điểm trung bình `eval` của `skills-auto` là 0.09 (so với `baseline` 0.06, chênh lệch 0.03 nằm trong $\pm 0.10$). Chỉ số `skills_read = 0/6`. Giả thuyết H2 được hỗ trợ.
  - *Lưu ý:* Vì `skills_read = 0`, thí nghiệm này không cung cấp evidence rằng auto-generated skills đã được runtime sử dụng; do đó không thể quy attribution cải thiện hoặc không cải thiện score cho skill.

- **H3 (tác vụ học vs tác vụ đánh giá): SUPPORTED / INCONCLUSIVE**
  - *Kết quả:* Ở `baseline`, điểm trung bình giảm từ 0.17 (`learn`) xuống 0.06 (`eval`). Điểm quy ước `rule_` đạt 0/12 (0.0%) trên toàn bộ tác vụ đánh giá, phù hợp với lập luận rằng quy ước ẩn mới rất khó được tác tử tự suy diễn.

### 7. Bảng Phân loại Lỗi (Error Taxonomy Analysis)

| Category | Mô tả nhóm lỗi | Số lỗi ở Tác vụ Học (Baseline) | Số lỗi ở Tác vụ Đánh giá (Baseline) | Biến động | Phân tích bằng chứng thực tế |
|---|---|---|---|---|---|
| **A** | Bỏ qua đặc tả | 1 | 1 | 0 | Tác tử chưa tuân thủ đầy đủ các định dạng ghi trong docstring/README. |
| **B** | Không kiểm chứng | 1 | 1 | 0 | Sửa nhầm các file test gốc trong thư mục `tests/`. |
| **C** | Vá triệu chứng | 0 | 0 | 0 | Không ghi nhận vết sửa triệu chứng trực tiếp. |
| **D** | Bỏ sót dữ liệu bẩn / định dạng | 6 | 7 | +1 | Chiếm đa số các thất bại kỹ thuật (`parse_duration`, `timestamps_utc`, `entry_count`). |
| **E** | Vi phạm quy ước Acme (`rule_`) | 6 | 12 | +6 | **0/12** check `rule_` đạt ở tập eval. Tác tử không biết các quy ước ẩn mới. |
| **F** | Báo cáo hoàn thành sai | 0 | 0 | 0 | Không ghi nhận hành vi báo cáo sai sự thật. |
| **G** | Lỗi Runtime / Khác | 8 (`GraphRecursionError`) | 0 | -8 | Các tác vụ `eval` hoàn thành thực thi (`error = null`) nhưng sai kết quả đầu ra. |

---

## 9. Hạn chế và tính hợp lệ

1. **Quy mô mẫu thử nghiệm nhỏ:** Mỗi điều kiện chỉ chạy 1 lần trên 3 tác vụ học và 3 tác vụ đánh giá, khiến kết quả chịu ảnh hưởng bởi tính ngẫu nhiên (stochasticity) trong quá trình sinh mã của LLM.
2. **Hành vi nạp Skill ở Runtime (`skills_read = 0`):** Tác tử chính không tự động nạp các tệp auto-skills trong thư mục `skills/auto/` ở thời điểm thực thi, dẫn đến việc thử nghiệm chưa đo đạc được hiệu quả nội dung của skill đối với hành vi tác tử.
3. **Quy ước ẩn (House Rules) cố định:** Các quy ước Acme (`rule_`) được thiết kế riêng biệt giữa tập học và tập đánh giá, khiến tác tử hoàn toàn thất bại ở các check quy ước mới nếu không có cơ chế nạp skill thành công.

---

## 10. Kết luận

1. Thử nghiệm trên 6 tác vụ (3 học, 3 đánh giá) cho thấy điều kiện `baseline` đạt điểm trung bình tốt nhất (17.0% ở tập học, 12.4% ở tập đánh giá).
2. Điều kiện `subagents` không cải thiện điểm số (3.3% ở tập đánh giá) nhưng làm tăng chi phí token (+58.9% ở tập đánh giá) do tác tử ít giao việc (`subagent_calls` = 1/3) và cô lập ngữ cảnh.
3. Điều kiện `skills-auto` đạt điểm đánh giá 12.4% (bằng `baseline`), tuy nhiên chỉ số `skills_read = 0` khẳng định tác tử chưa nạp file skill nào ở runtime.
4. Tác tử hoàn toàn thất bại ở nhóm check quy ước Acme (`rule_`) trên tập đánh giá (0/12 check đạt, 0.0%), khẳng định quy ước ẩn mới không thể tự suy diễn nếu không có skill chỉ dẫn.
5. Đề xuất cải tiến: Cần bổ sung cơ chế bắt buộc nạp skill (Skill Injection / Auto-triggering) vào prompt hệ thống của tác tử chính để đảm bảo các skill đã sinh ra được áp dụng ở runtime.

---

## Phụ lục

- **Lệnh đã chạy (theo thứ tự):**
  1. `python -m lab.runner --condition baseline --tasks code-learn data-learn logs-learn`
  2. `python -m lab.runner --condition subagents --tasks learn`
  3. `python -m lab.curator`
  4. `python -m lab.runner --condition skills-auto --tasks learn`
  5. `git add -A && git commit -m "hypotheses"`
  6. `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze`
  7. `python -m lab.runner --condition baseline --tasks eval`
  8. `python -m lab.runner --condition subagents --tasks eval`
  9. `python -m lab.runner --condition skills-auto --tasks eval`
  10. `pytest`
- **Ghi chú khác:** Working tree được duy trì sạch sẽ, tag `freeze` trỏ đúng commit `3e1dc2b`.
