# Tự đánh giá kỹ thuật theo RUBRIC.md

Mai Xuân Khang — 2A202603722 — K5-L3B.

| Tiêu chí | Tối đa | Bằng chứng | Trạng thái | Dự kiến | Tin cậy | Lý do và rủi ro bị trừ |
|---|---:|---|---|---:|---|---|
| Agent loop | 30 | agent.py; 53 main tests; traces 22 case | PASS | 29 | Cao | Assistant message, IDs, nhiều calls, điều kiện dừng đúng; chưa thử mọi backend/protocol biến thể |
| Robustness & trace | 15 | main/validation tests; B3/B4; trace lỗi | PASS | 14 | Cao | JSON/schema, exceptions, length, max_steps, bounded retry; chưa stress test API live dài hạn |
| Eval & phân tích | 20 | before/after, manifest, NOTES, final_review.json | PASS | 19 | Trung bình | 22/22 mỗi bộ, cùng model/dataset/budget, lỗi H5 thật; đã chạy lại after/bonus sau cập nhật upstream |
| Cải tiến & trình bày | 20 | source gate, prompt, tests, DEFENSE.md | PARTIAL | 16 | Trung bình/thấp | Cải tiến có evidence; chưa kiểm tra buổi demo và khả năng tự giải thích của học viên |
| Tổng chính | 85 | Các dòng trên | PARTIAL | 78 | Trung bình | Không đồng nhất điểm judge với điểm lab |
| Bonus | 15 | eval_bonus.json, B2/B3/B4/B10, bonus tests | PASS kỹ thuật | 14.91 | Trung bình | 10/10 scored; xem NOTES về claim thiếu bằng chứng trong các case chưa tối đa; live chưa kiểm chứng |
| Tổng dự kiến | 100 | Tự đánh giá, không chính thức | PARTIAL | 92.91 | Trung bình | Giảng viên có thể điều chỉnh theo code, trace, demo và quy định nộp |

Ba thang điểm cần phân biệt:

- Main eval do judge/code sinh: 95.18 → 99.91 trên 100.
- Bonus eval: 99.4/100, quy đổi 14.91/15 tham khảo.
- Điểm lab: 85 chính + 15 bonus do giảng viên quyết định; bảng tự đánh giá không
  tự động biến hai điểm eval thành điểm lab. Không cam kết 100/100.

Chưa chấm các yếu tố deadline, LMS, giải thích miệng hoặc đánh giá độc lập khác.
Phạm vi sử dụng AI hỗ trợ được ghi trong NOTES; phần giải thích miệng chưa được xác nhận.
