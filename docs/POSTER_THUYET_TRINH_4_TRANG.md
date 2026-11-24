# POSTER TRÌNH CHIẾU DỰ ÁN NGHIÊN CỨU KHOA HỌC KỸ THUẬT
*(Mẫu theo Phụ lục 8 - Ban hành kèm theo Công văn số 6068/SGDĐT-GDTrH&HSSV TP Đà Nẵng)*
*(Quy cách: Đúng 04 trang trình chiếu - Không ghi tên tác giả, giáo viên, cơ sở giáo dục, đơn vị dự thi)*

---

<!-- TRANG 1 -->
# TRANG 1: TỔNG QUAN, HAI NHIỆM VỤ CỐT LÕI VÀ PHẠM VI DEMO MVP

### 1. TÊN ĐỀ TÀI DỰ ÁN
**NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC BẰNG THỊ GIÁC MÁY TÍNH VÀ SUY LUẬN KHÔNG - THỜI GIAN**
- **Lĩnh vực dự thi:** Hệ thống nhúng và Phần mềm hệ thống --- Năm học 2026 - 2027

### 2. BỐI CẢNH & PHẠM VI DEMO MVP
- **Thực trạng:** Vẫn còn tình trạng vứt vỏ chai, hộp sữa bừa bãi ở hành lang, sân trường và bỏ nhầm ngăn thùng rác phân loại. Camera hiện nay chỉ ghi hình thụ động, thầy cô tua lại video thủ công rất vất vả.
- **Phạm vi hiện tại (Demo MVP):** Tập trung hoàn thiện **phần lõi Trí tuệ nhân tạo (AI)** gọn nhẹ, dễ kiểm chứng, tự động làm mờ mặt học sinh để bảo vệ quyền riêng tư.

### 3. HỆ THỐNG GỒM HAI NHIỆM VỤ GẮN KẾT
- **Nhiệm vụ 1 (Đã triển khai & kiểm chứng):** Phát hiện hành vi xả rác không đúng nơi quy định bằng suy luận chuỗi bằng chứng 3 mức và tự động xuất Thẻ sự kiện 3 khung hình.
- **Nhiệm vụ 2 (Đã thiết kế kiến trúc chi tiết):** Phân loại **rác tái chế** và **không tái chế**, đối chiếu vùng ngăn thùng rác để cải thiện tính tự giác bỏ rác đúng thùng phân loại.

---

<!-- TRANG 2 -->
# TRANG 2: KIẾN TRÚC AI & SUY LUẬN KHÔNG - THỜI GIAN CHO HAI NHIỆM VỤ

### A. NHIỆM VỤ 1: SUY LUẬN CHUỖI BẰNG CHỨNG 3 MỨC
- **Bộ nhận diện kép + ByteTrack:** YOLO11m bắt Người và Rác nhỏ; YOLO-World tìm Thùng rác; ByteTrack duy trì ID ổn định.
- **Phân cấp 3 mức kết luận (tránh quy kết vội vàng):**
  1. **Đủ bằng chứng thị giác:** Quan sát trực tiếp cả 3 bước (Mang rác $\to$ Tách rời $\to$ Nằm yên ngoài thùng).
  2. **Cần kiểm tra thêm:** Có che khuất ở lúc mang/buông (dùng truy vết ngược 2.5 giây) — thầy cô xem lại Thẻ sự kiện.
  3. **Không đủ căn cứ:** Rác có sẵn từ trước hoặc thiếu lịch sử người mang.
- **Thẻ sự kiện 3 khung hình:** Ghép 3 mốc ảnh liên tiếp + tự động làm mờ mặt học sinh.

### B. NHIỆM VỤ 2: PHÂN LOẠI RÁC TÁI CHẾ / KHÔNG TÁI CHẾ
- **Nhận diện & Phân loại bằng YOLO-World:** Phân biệt *Rác tái chế* (chai nhựa, lon, giấy, hộp sữa) và *Không tái chế* (túi nilon, vỏ bánh, hộp xốp, khăn giấy), dùng *bỏ phiếu theo thời gian* để giữ nhãn ổn định.
- **Khai báo vùng ngăn thùng (Manual Bin Zone):** Định vị chính xác ngăn Xanh (Tái chế) và ngăn Vàng (Không tái chế), không nhầm ngăn.
- **Xử lý thùng rác kín (Disappearance-in-Zone):** Nhận diện rác biến mất ngay tại miệng ngăn thùng để đánh giá 4 trạng thái: *Bỏ đúng ngăn*, *Bỏ sai ngăn*, *Xả ngoài thùng*, *Chưa đủ căn cứ phân loại*.

---

<!-- TRANG 3 -->
# TRANG 3: KẾT QUẢ THỰC NGHIỆM TRÊN 6 VIDEO & THẺ SỰ KIỆN 3 KHUNG HÌNH

| STT | Tập tin Video | Địa điểm | Frame | Tốc độ | Sự kiện | Kết quả thực tế (17/17 bài test PASS) |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `sample_01_corridor` | Hành lang trường | 502 | 16.6 FPS | 1 lần | Bắt đúng vứt chai cạnh thùng lúc 13.37s (`Cần kiểm tra thêm`) |
| 2 | `sample_02_classroom` | Trong phòng học | 203 | 20.3 FPS | 0 lần | Đúng logic: Rác giấu trong hộc bàn gỗ, không báo bừa |
| 3 | `sample_03_corridor_drop` | Hành lang dọc | 284 | 18.1 FPS | 1 lần | Bắt đúng cú thả chai lúc 00.93s (`Cần kiểm tra thêm`) |
| 4 | `sample_04_schoolyard` | Sân trường cây | 466 | 19.9 FPS | 0 lần | Chính xác: Bóng lá cây lay động không gây báo giả |
| 5 | `sample_05_balcony` | Ban công lầu 2 | 395 | 20.3 FPS | 0 lần | Chính xác: Học sinh đi tay không, trạng thái an toàn |
| 6 | `sample_06_distant` | Sân trường xa | 419 | 19.9 FPS | 0 lần | Chính xác: Góc quay rộng ổn định, không nhiễu giả |

- **Bằng chứng trực quan:** Hiển thị Thẻ sự kiện 3 ảnh tại Video 1 và Video 3 (đã tự động làm mờ mặt học sinh) cùng Key Frame minh chứng chống báo giả tại Video 2.

---

<!-- TRANG 4 -->
# TRANG 4: KẾT LUẬN, PHẠM VI DEMO MVP VÀ HƯỚNG PHÁT TRIỂN (FUTURE WORK)

### 1. KẾT QUẢ & PHẠM VI DEMO MVP HIỆN TẠI
- **Tập trung vào phần lõi AI:** Dự án hiện dừng ở mức độ **Demo MVP** nhằm chứng minh trọn vẹn tính khả thi của các thuật toán AI cốt lõi.
- **Suy luận trung thực, nhân văn:** Phân cấp 3 mức bằng chứng và xuất **Thẻ sự kiện 3 khung hình** giúp giáo viên kiểm chứng trực quan, tránh kết luận vội vàng khi có che khuất.
- **Hiệu năng thực tế:** Chạy mượt 16.6 - 20.3 FPS trên máy tính phổ thông, 17/17 bài kiểm thử tự động đạt 100% PASS.

### 2. HƯỚNG PHÁT TRIỂN TƯƠNG LAI (FUTURE WORK)
- **Mục tiêu lớn:** Đưa hệ thống AI này vào ứng dụng thực tế trong **môi trường giáo dục** để xây dựng thói quen giữ vệ sinh và phân loại rác tự giác.
- **Hoàn thiện tích hợp Nhiệm vụ 2:** Triển khai mã nguồn phân loại rác tái chế / không tái chế trên cụm thùng rác đôi tại trường học.
- **Hợp tác từ phía nhà trường:** Cần sự phối hợp của Ban Giám hiệu cho phép kết nối an toàn với hệ thống Camera sẵn có của trường.
- **Liên kết ứng dụng quản lý (như eNetViet):** Gửi thông báo nhắc nhở kín đáo, kịp thời tới giáo viên và học sinh khi có vi phạm.
