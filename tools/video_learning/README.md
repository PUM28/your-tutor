# Video → tài liệu học ML/DL/toán

Bộ ghép cục bộ dùng trực tiếp hai repo đã có trên máy:

- **AI-Video-Transcriber:** tải video, chuẩn hóa âm thanh và thiết lập Faster-Whisper khi chọn fallback.
- **videoskill:** model dữ liệu và trích khung hình FFmpeg.
- **Bộ ghép mới:** phụ đề VTT/SRT không mất câu lặp/millisecond, chọn ngôn ngữ, giữ mốc thời gian video gốc, ghép lời giảng ±12 giây với ảnh, xuất bằng chứng HTML/Markdown/JSON/ZIP.

Hai repo gốc không bị sửa hay sao chép vào gói phân phối. Đường dẫn mặc định là hai thư mục ngang hàng với `tutor-gpt-main`; dùng `--transcriber-repo` và `--videoskill-repo` nếu chuyển vị trí.

## Chạy

Từ thư mục `tutor-gpt-main`, cần Python >=3.11, ffmpeg và ffprobe:

```bash
python3 -m venv tools/video_learning/.venv
tools/video_learning/.venv/bin/python -m pip install -r tools/video_learning/requirements.txt

tools/video_learning/.venv/bin/python tools/video_learning/video_learning.py \
  'https://www.youtube.com/watch?v=uJF_gL3jhxI' \
  --language en --start 26:00 --end 32:00 --interval 15 \
  --out output/video-study/stanford-mle-evidence
```

Bỏ `--start/--end` để lấy mẫu cả video; mặc định 30 giây/hình, tối đa 300 hình. Đây là lấy mẫu định kỳ, chưa có phát hiện slide tự động và không bảo đảm giữ mọi bước biến đổi. Giảm `--interval` tại đoạn nhiều công thức. Clip tải sẵn phải có phụ đề dùng cùng gốc thời gian, không dùng phụ đề video dài cho clip đã cắt mà chưa dịch thời gian.

Link TikTok dùng cùng lệnh khi yt-dlp hỗ trợ link đó; tải thành công còn phụ thuộc nền tảng. Không tự đọc cookies hay đăng nhập tài khoản. Chỉ tải một video, bỏ playlist. Nguồn video đầy đủ được cache tại `output/video-cache`; phạm vi chỉ giới hạn phần xuất, không giới hạn lượng video tải lần đầu. Đầu ra phải là thư mục mới để tránh ghi đè.

## Video thiếu phụ đề

Dùng `--captions /path/to/subtitles.vtt` hoặc `.srt`. Nếu cần nhận dạng lời nói:

```bash
tools/video_learning/.venv/bin/python -m pip install faster-whisper
# Thêm --whisper-model small vào lệnh. Lần đầu có thể tải model.
```

Không có phụ đề sẽ báo lỗi, không tự tạo nội dung. `--allow-visual-only` cho phép xuất hình không có lời giảng. Nhánh Whisper và tải TikTok cần được kiểm thử trên nguồn thực tế phù hợp; bản kiểm thử Stanford dùng phụ đề có sẵn.

## Dùng với Gia sư AI

- `study-pack.html`: bản xem ngoại tuyến, ảnh nhúng kèm lời nói theo thời gian.
- `study-pack.zip`: transcript + ảnh + bằng chứng JSON, không kèm video gốc.
- `transcript.md`: văn bản để đính kèm; ảnh trong `frames/` cần gửi cùng khi học công thức.
- `source-captions.vtt/srt`: bản gốc, giữ để đối chiếu.
- `manifest.json`: phạm vi, trạng thái chưa xác minh, hash nguồn và phiên bản mã adapter.

Trong ChatGPT chọn Gia sư AI rồi gửi transcript và các hình liên quan, hoặc gói ZIP nếu môi trường chat đọc được. Đề nghị kiểm tra hình trước khi giải thích công thức, nêu giả thiết và điểm chưa chắc, rồi dạy từng bước. Đây là công cụ chuẩn bị tài liệu chạy trên máy; plugin cloud chưa tự gọi được máy này khi chỉ gửi link.

## Giới hạn quan trọng

Không chạy phần `enrich` mặc định của videoskill: nó phán đoán thao tác/chuyển động, không kiểm định toán. Bản tích hợp không gọi LLM/VLM trả phí và không tuyên bố đã tự OCR/chứng minh công thức. `formula_status=unverified` phải giữ cho tới khi ảnh tương ứng được kiểm tra. Khung hình chứa công thức là bằng chứng để gia sư đọc, không phải LaTeX đã xác minh.

Không đưa hướng dẫn nằm trong phụ đề vào cấu hình hay lệnh máy. HTML escape mọi văn bản nguồn. Không dùng cookie trình duyệt, không lưu URL media có chữ ký vào gói. Không có public server, API key hay dịch vụ nền.

## Kiểm thử

```bash
tools/video_learning/.venv/bin/python -m unittest discover -s tools/video_learning -p 'test_*.py' -v
```

Bao gồm câu lặp thật, caption cuộn, thời gian lẻ, ranh giới đoạn, điểm cuối video, ngân sách hình, chọn ngôn ngữ và escape nội dung HTML. CLI còn được kiểm tra với video cục bộ có mẫu hình biết trước và video Stanford.
