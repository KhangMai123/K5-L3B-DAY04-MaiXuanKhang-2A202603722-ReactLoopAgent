# Giải thích code và tự kiểm tra trước khi trình bày

Mai Xuân Khang — 2A202603722 — K5-L3B.

Tài liệu tóm tắt thiết kế đang dùng và các tình huống cần giải thích khi demo.
Mỗi mục đi kèm cách đối chiếu với code hoặc trace. Các câu hỏi tự kiểm tra dùng
để chuẩn bị trình bày; chưa thay thế buổi phản biện trực tiếp.

## 1. ReAct loop trong bài này

`run_agent` tạo system/user messages, chọn schemas và prompt từ tools nếu có.
Mỗi lượt gọi `provider.complete` được ghi usage. Assistant message được append
nguyên vẹn. Nếu có calls, Python parse và kiểm tra arguments, chạy từng tool,
ghi trace rồi append JSON observation theo từng ID. Chỉ sau tất cả observations
mới gọi model tiếp. Nếu model dừng hợp lệ, source gate kiểm tra trước completed.
`length`, output rỗng, response sai cấu trúc và lỗi provider trả error; hết budget
trả max_steps với answer rỗng.

Câu hỏi tự kiểm tra: một response có ba tool calls, call thứ hai lỗi JSON thì
call thứ ba có chạy không? Có: lỗi thứ hai là observation, không dừng vòng for.

## 2. Vì sao giữ assistant message nguyên vẹn?

Nó chứa danh sách tool calls và ID mà observations phải tham chiếu. DeepSeek có
thể thêm trường riêng; giữ nguyên giúp conversation tiếp theo giữ đúng protocol.
Code không lấy nội dung suy luận nội bộ để ghi trace. Trace model chỉ ghi step,
finish và số calls; usage có thể có số reasoning tokens, không chứa nội dung suy luận.

Câu hỏi: nếu chỉ giữ `content` mà bỏ `tool_calls`, provider còn biết các tool
results là câu trả lời cho yêu cầu nào không? Không còn đủ dữ liệu protocol.

## 3. tool_call_id dùng làm gì?

Tool message dùng đúng `call['id']`, không dùng tên tool hay ID incident.
Hai calls cùng `get_status` vẫn có ID khác nhau. Tests kiểm tra thứ tự/ID của
hai results; test bổ sung kiểm tra call lỗi không làm mất result còn lại.

## 4. Vì sao max_steps đếm model calls?

Vòng `for step in range(1, max_steps+1)` bao quanh `complete`, còn vòng tool calls
nằm bên trong. Một model turn có năm tool calls vẫn là một step. Lượt sửa answer
thiếu nguồn cũng là model call và tiêu budget. Provider request lỗi vẫn thêm một
usage rỗng và trả error. Budget này không phải giới hạn số tool calls hoặc thời
gian chạy tuyệt đối. Main eval dùng 8; bonus 16; hàm mặc định 6.

## 5. Chống prompt injection như thế nào?

System prompt thực tế là prompt của bộ tools cộng `OPERATING_RULES`. Mọi trường
tool, kể cả notice tự xưng system/developer, là dữ liệu. Hướng dẫn yêu cầu không
đổi nhiệm vụ và không lặp payload/marker khi mô tả việc từ chối. Không có danh
sách hard-code marker hay ID eval trong agent. Trace vẫn giữ dữ liệu tool để
kiểm chứng; final tập trung vào status liên quan. Đây chủ yếu là phòng vệ bằng
prompt, không phải bảo đảm chống mọi injection trong tương lai.

## 6. Source validation hoạt động thế nào?

Sau `get_incident_details` thành công (`ok is True`), `valid_source` chỉ nhận URL
HTTP(S) có host và không chứa user/password. `sources` là tập URL thực sự được
trả về. `answer_urls` tách URL khỏi final để tránh nhận nhầm URL chỉ cùng tiền tố.
Nếu thiếu URL của bất kỳ incident đã đọc, ghi `validation_missing_source` và
append yêu cầu sửa. Model phải sửa trong budget; Python không tự tạo URL hoặc
ghép URL vào answer. Lookup thất bại không tạo yêu cầu nguồn. Gate không đối
chiếu từng claim với nguồn và không chứng minh URL thật sự đáng tin.

Câu hỏi: vì sao chỉ kiểm tra `'https://nguon/abc' in answer` chưa đủ? Vì URL giả
`https://nguon/abc-fabricated` vẫn vượt qua phép kiểm tra tiền tố đó.

## 7. Lỗi được chọn và cách sửa

H5 trong baseline có status đúng nhưng được 20 vì lặp marker injection trong
đoạn “Lưu ý an toàn”. Agent đã từ chối chỉ dẫn giả; lỗi cụ thể là trích lại payload,
không phải bằng chứng nó thực thi payload. Prompt được bổ sung quy tắc mô tả
chung thay vì chép chuỗi độc hại. E2 còn thiếu URL incident dù judge cho 100,
nên bổ sung gate có tests riêng. `evidence/improvement_plan.md` ghi giả thuyết
trước khi sửa, `NOTES.md` ghi so sánh kết quả cuối.

## 8. Đọc kết quả trước/sau

Xem `NOTES.md` mục 4 và `evidence/comparison.json`: điểm tổng, điểm H5, số model
calls, tool calls, token agent/judge và chi phí ước tính. Đọc riêng các regression;
không suy từ điểm tổng tăng thành mọi case tốt hơn. Cấu hình before/after phải
giống, snapshot/dataset có hash, baseline có SHA256 để kiểm tra không sửa tay.
Điểm eval 0–100 khác điểm lab 85+15; self-assessment không phải điểm giảng viên.

## 9. Bonus retry và pagination

`tools.schemas`/`tools.system_prompt` cung cấp năm status tools và details phân
trang. `ToolExecutor` chỉ ghi nhớ rate limits trong một conversation. Lỗi 429
được trả cho model; model quyết định có gọi lại. Python nhớ số lỗi liên tiếp theo
tool/provider, chặn thực thi sau ba lỗi và đặt `retry_allowed=false`. Nó đọc
`Retry-After` dạng số giây hoặc HTTP date, dùng backoff 2/4/8 giây khi thiếu header;
tổng budget chờ là 20 giây. Nếu header yêu cầu chờ lâu hơn budget thì dừng, không
rút ngắn thời gian máy chủ yêu cầu. Fixture bonus có delay=0 nên không chờ thật.

Arguments pagination được kiểm tra integer (loại cả bool), offset không âm,
limit 1–3. Model dùng `next_offset` nếu câu hỏi còn thiếu bằng chứng; không cần
đọc mọi trang nếu đã có thông tin cần, nhưng phải thừa nhận giới hạn. Một provider
lỗi không ngăn tool của provider khác chạy. B2/B3/B4/B10 là các trace cần mở
khi demo pagination, retry và partial failure.

Câu hỏi tự kiểm tra: nếu provider LLM trả 429 thì guard này có xử lý không?
Không: đây là guard cho status tools. Lỗi LLM provider trả status=error, không
được biến thành nhận định dịch vụ outage; hạ tầng eval cần được khắc phục riêng.
