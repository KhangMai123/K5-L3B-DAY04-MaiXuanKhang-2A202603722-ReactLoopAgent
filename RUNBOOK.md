# Chạy và kiểm chứng bài Day 04

Mai Xuân Khang — 2A202603722 — K5-L3B.

Bài dùng Python standard library, không cần cài thêm package hoặc framework agent.

Repo đã tích hợp commit `147982b` từ VinUni, bổ sung provider `opencode-go`.
README, `.env.example`, các lựa chọn CLI và tests liên quan dùng bản upstream mới.
OpenCode Go được kiểm tra offline qua tests của đề; cấu hình chạy eval của bài
vẫn là DeepSeek trực tiếp. Các helper có sẵn giữ nguyên, không bổ sung helper mới.

## Cấu hình đang dùng

Sau lỗi HTTP 429 của Gemini, cấu hình được chuyển sang **DeepSeek trực tiếp**.
Endpoint: `https://api.deepseek.com/chat/completions`; model: `deepseek-flash`.
`PROVIDER=openai` chỉ chọn định dạng Chat Completions tương thích trong adapter,
không có nghĩa request gửi tới OpenAI. `OPENAI_BASE_URL` quyết định endpoint.
Gemini vẫn dùng nguyên endpoint riêng; không bị biến cấu hình này chuyển hướng.

Theo [tài liệu DeepSeek](https://api-docs.deepseek.com/), model ID `deepseek-flash`
hiện được phục vụ bởi DeepSeek V4.1 Flash. Không dùng ID riêng của OpenCode Go.

Copy `.env.example` thành `.env`, điền `DEEPSEEK_API_KEY` tại máy local.
File chỉ dùng `KEY=VALUE`, không thêm `export`. `with_env.py` nạp cấu hình bằng
standard library, chuyển key qua môi trường subprocess và không in giá trị key.
Trên máy đang làm lab, cấu hình nằm tại `.local/deepseek.env`; dùng
`--env .local/deepseek.env` sau `with_env.py` cho các lệnh cần API.

```powershell
python --version
python -m unittest discover -s tests -v
python -m unittest discover -s bonus -p "test_*.py" -v
python with_env.py run.py "Kiểm tra GitHub Actions theo snapshot và dẫn nguồn."
python with_env.py run.py --bonus --max-steps 16 "Kiểm tra GitHub, Vercel và npm theo snapshot."
python with_env.py evals/run_evals.py --case E2 --output eval_results_recheck_e2.json
python with_env.py evals/run_evals.py --output eval_results_recheck_main.json
python with_env.py evals/run_evals.py --bonus --output eval_results_recheck_bonus.json
```

Không ghi đè các file `eval_before.json`, `eval_after.json`, `eval_bonus.json` đã
lưu làm bằng chứng. Chọn tên output mới khi kiểm tra lại. Agent/judge dùng cùng
model, main budget 8 và bonus budget 16. Eval runner luôn dùng snapshot; CLI
`run.py` cũng mặc định snapshot. Các request agent và judge đều có thể tính phí.

## Phạm vi dữ liệu

Main `get_status` tìm chuỗi trong 50 incident gần nhất và trả tối đa 5 incident khớp.
`matching_incidents_in_last_50` là số mục khớp trong phạm vi quét, không phải số
incident có mặt trong mảng `incidents` trả về. A5 thực tế trả 5 mục, đếm được 23
mục khớp; không được tuyên bố đã đọc hoặc nhận đủ 50 mục.
Không tìm thấy không chứng minh không tồn tại. Trường `components` của status
không đồng nhất với `components` của incident. `get_incident_details` giữ tối đa
hai update mới nhất và update đầu tiên, mỗi body tối đa 900 ký tự.

Bonus cung cấp 5 status tools và timeline theo trang, `offset >= 0`, `limit` từ
1 đến 3. `next_offset` cho biết còn trang; `truncated` cho biết body bị cắt.
Snapshot GitHub/Cloudflare được chụp ngày 09/11/2026; ba provider bonus ngày
10/11/2026. Các dữ liệu này không xác nhận trạng thái live tại thời điểm nộp.

## Bằng chứng và bảo mật

`evidence/agent_before.py` là code baseline trước cải tiến; manifest lưu hash
dataset/snapshot và cấu hình. Kết quả Gemini lỗi được giữ nguyên ở local
`evidence/gemini_incomplete.json`, loại khỏi danh sách commit để tránh nhầm với
baseline nộp. Hash lịch sử của nó vẫn có trong manifest; kết quả này không tham
gia so sánh DeepSeek before/after. Kết quả OpenCode Go lỗi xác thực cũng không
được dùng để chấm bài. `evidence/final_review.json` ghi kết quả tests, source hash,
protected-file/secret checks và danh sách commit được rà soát.

Sau cập nhật upstream, main after và bonus được chạy lại bằng model đã khóa;
baseline giữ nguyên. NOTES và manifest phản ánh kết quả của phiên bản đã tích hợp.
Không chỉnh tay eval. Điểm cao không bảo đảm mọi câu trong answer đều đúng;
cần đối chiếu các claim về số incident, scope và injection với trace của chính run.

`.env`, `*.env`, `.local/`, cache và kết quả chạy lại `eval_results*.json` được
ignore. Không đưa key vào câu lệnh, source, trace hoặc tài liệu. Chỉ commit các
file nộp đã rà soát và được duyệt. Việc nộp link lên LMS thực hiện bằng tài khoản cá nhân.
