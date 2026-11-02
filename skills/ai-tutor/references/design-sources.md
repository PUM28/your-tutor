# Nguồn thiết kế và giới hạn

Khảo sát bản repo cục bộ do người dùng cung cấp ngày 2026-11-01. Các đường dẫn dưới đây là dấu vết nguồn để bảo trì, không phải phụ thuộc khi chạy skill. Không yêu cầu người học cài hai ứng dụng.

## Tutor-GPT

Repo khảo sát: `tutor-gpt-main`.

- `utils/ai/prompts.ts`: kết hợp lịch sử, ngữ cảnh người học và ngữ cảnh PDF trong phản hồi.
- `utils/prompts/thought.ts`: tách nhu cầu tìm hiểu người học và nhu cầu tra cứu tài liệu.
- `utils/prompts/response.ts`: đối thoại gia sư ngắn, cá nhân hóa theo ngữ cảnh.

Chuyển thể: phân biệt nguồn kiến thức với sở thích và bằng chứng học tập; chỉ lấy ngữ cảnh liên quan, điều chỉnh câu hỏi theo phản hồi. Không sao chép phần nhập vai, suy đoán tâm lý, chỉ dẫn xuất suy nghĩ nội bộ, mốc kiến thức/công cụ cố định hoặc nghĩa vụ luôn kết thúc bằng câu hỏi. Không tích hợp Honcho.

## DeepTutor

Repo khảo sát: `DeepTutor-main`.

- `deeptutor/learning/prompts/en.yaml`: mục tiêu quan sát được; loại memory/concept/procedure/design; giải thích, dạy lại, luyện tập, chẩn đoán lỗi.
- `deeptutor/learning/topic_materials.py`: phân biệt nguồn sẵn có với nguồn đọc được và đọc theo chương khi cần.
- `deeptutor/reading/quiz.py`: câu hỏi đọc hiểu có bằng chứng từ phần đang đọc, kiểm tra phương án.
- `deeptutor/learning/teaching.py`: sở thích cần phát biểu thực tế; ghi cách dạy và kết quả theo mục tiêu; phản hồi mới ưu tiên hơn ghi nhớ cũ.
- `deeptutor/capabilities/mastery/memory.py`: ký ức gia sư không tự chứng minh tiến độ; giữ điểm neo nguồn, lỗi và điều chưa chắc.
- `deeptutor/learning/review_strategy.py`: chiến lược ôn khác nhau theo mục tiêu và loại kiến thức.
- `tests/capabilities/test_mastery_teaching_delivery.py`: có kiểm thử phân biệt đã phát lời giảng với bằng chứng học được. Chỉ đọc kiểm thử, không chạy bộ test ứng dụng.

Chuyển thể: lộ trình theo mục tiêu, danh mục nguồn, kiểm tra câu hỏi, sổ lỗi, hồ sơ tiếp nối và ôn thích ứng. Không sao chép yêu cầu cứng về số câu/số mô-đun, không gán nội dung từ tên tệp chưa đọc, không dùng tham số lịch ôn làm cam kết khoa học. Không giả lập các công cụ, API, lưu trữ hoặc máy chấm của DeepTutor.

## Phần phát triển thêm trong skill

Kết nối hai ý tưởng thành vòng học thống nhất: đọc nguồn cần thiết → chọn mục tiêu → dạy phù hợp phản hồi → kiểm tra khả năng thực hiện → sửa lỗi → ôn và tiếp nối. Thêm phân biệt đáp án suy ra với bằng chứng nguyên văn, chấm đúng câu đang chờ, giữ tiến độ chưa kiểm chứng khi người học muốn đi tiếp và không coi sở thích là năng lực cố định.

Đây là chuyển thể quy trình bằng văn bản tự viết, không sao chép mã hay tích hợp runtime. Kiểm tra cấu trúc skill không chứng minh hiệu quả giáo dục; cần điều chỉnh qua những buổi học thực tế của người dùng.
