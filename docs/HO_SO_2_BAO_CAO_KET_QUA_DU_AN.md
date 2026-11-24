# BÁO CÁO KẾT QUẢ THỰC HIỆN DỰ ÁN
*(Mẫu theo Phụ lục 3 - Ban hành kèm theo Công văn số 6068/SGDĐT-GDTrH&HSSV ngày 04/11/2026 của Sở GDĐT TP Đà Nẵng)*

---

**TÊN DỰ ÁN:**  
# NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC BẰNG THỊ GIÁC MÁY TÍNH VÀ SUY LUẬN KHÔNG - THỜI GIAN

- **Lĩnh vực nghiên cứu:** Hệ thống nhúng và Phần mềm hệ thống
- **Cấp học thực hiện:** Học sinh Trung học cơ sở (THCS)
- **Phạm vi sản phẩm hiện tại:** Phiên bản thử nghiệm lõi (Demo MVP) tập trung vào phần Trí tuệ nhân tạo (AI)
- **Mã số dự án:** (Do Ban Tổ chức Cuộc thi cấp)
- **Năm học thực hiện:** 2026 - 2027

*(Báo cáo thực hiện ẩn danh theo đúng Quy chế Cuộc thi: Tuyệt đối không ghi tên trường, đơn vị dự thi, tên học sinh, người hướng dẫn hoặc chèn biểu trưng, logo).*

---

## PHẦN 1: ĐẶT VẤN ĐỀ VÀ MỤC TIÊU NGHIÊN CỨU

### 1.1. Lý do chọn đề tài và tính cấp thiết
Giữ gìn vệ sinh môi trường học đường là nền tảng để xây dựng ngôi trường xanh - sạch - đẹp và văn minh. Tuy nhiên, tại các khu vực sinh hoạt chung như hành lang, cầu thang hay sân trường, vẫn còn tình trạng học sinh vứt vỏ chai nhựa, hộp sữa bừa bãi hoặc bỏ rác vào sai ngăn của thùng rác phân loại (như bỏ chai nhựa vào ngăn rác không tái chế).

Các hệ thống camera quan sát trong trường hiện nay chỉ ghi hình thụ động. Khi xảy ra mất vệ sinh, thầy cô giám thị phải tua lại hàng giờ video rất vất vả. Từ thực tế đó, chúng em nghiên cứu xây dựng hệ thống Trí tuệ nhân tạo (AI) biến camera thường thành trợ lý giám sát thông minh. Hiện tại, dự án tập trung hoàn thiện phiên bản **Demo MVP (Sản phẩm thử nghiệm lõi)** cho phần AI cốt lõi với **2 nhiệm vụ gắn kết chặt chẽ**:
1. **Nhiệm vụ 1 (Đã hoàn thiện và kiểm chứng thực nghiệm):** Phát hiện hành vi xả rác không đúng nơi quy định, kết hợp suy luận chuỗi bằng chứng 3 mức và xuất Thẻ sự kiện 3 khung hình.
2. **Nhiệm vụ 2 (Đã thiết kế kiến trúc chi tiết để tích hợp):** Phân loại rác tái chế và không tái chế, đối chiếu với từng ngăn thùng rác để cải thiện tính tự giác bỏ rác đúng thùng phân loại của học sinh.

### 1.2. Mục tiêu và giả thuyết khoa học
- **Mục tiêu:** Xây dựng giải pháp thị giác máy tính gọn nhẹ, chạy mượt trên máy tính phổ thông của trường học; nhận biết trung thực hành vi xả rác mà không quy kết oan cho học sinh; đồng thời thiết kế phương án phân loại rác tái chế / không tái chế phù hợp thùng rác đôi học đường.
- **Giả thuyết khoa học:** Thay vì dùng các mô hình nhận diện hành động 3D nặng nề, việc kết hợp nhận diện vật thể, theo dấu định danh (ByteTrack) và bộ suy luận chuỗi bằng chứng theo không gian - thời gian sẽ giúp hệ thống đạt tốc độ thời gian thực, dễ kiểm chứng và dễ mở rộng sang bài toán phân loại rác.

---

## PHẦN 2: THIẾT KẾ HỆ THỐNG CHO HAI NHIỆM VỤ CỐT LÕI

### 2.1. Nhiệm vụ 1: Phát hiện hành vi xả rác không đúng nơi quy định (Đã triển khai)

#### A. Sáng kiến "Bộ nhận diện kép" và Theo dấu định danh
- **Mắt AI thứ nhất (`weights/best.pt` - YOLO11m):** Chuyên phát hiện Học sinh và các vật thể rác nhỏ cầm trên tay.
- **Mắt AI thứ hai (`yolov8s-worldv2.pt` - YOLO-World):** Phát hiện các loại thùng rác trong sân trường (cấp mã định danh #501, #502...).
- **Thuật toán theo dấu ByteTrack:** Ghi nhớ mã số định danh (ID) và quỹ đạo di chuyển của từng bạn học sinh và vật thể qua từng khung hình.

#### B. Bộ suy luận chuỗi bằng chứng 3 mức và Cơ chế tua ngược
Thay vì chỉ kiểm tra cứng nhắc rồi lập tức kết luận vi phạm, hệ thống đánh giá đầy đủ chuỗi 3 giai đoạn (*Mang rác* $\to$ *Tách rời* $\to$ *Rác nằm yên trên sàn*), lọc bỏ rác cũ đã nằm sẵn từ trước, và phân loại kết quả thành **3 mức độ khách quan**:

| Mức độ kết luận | Điều kiện chuỗi bằng chứng và ý nghĩa giáo dục |
| :--- | :--- |
| **1. Đủ bằng chứng thị giác** (`CONFIRMED_LITTERING`) | Camera quan sát trực tiếp cả 3 mốc: bạn mang rác, buông tay rời khỏi người và rác nằm yên ngoài thùng rác trên 0.6 giây. |
| **2. Cần kiểm tra thêm** (`SUSPICIOUS_NEED_REVIEW`) | Có dấu hiệu bỏ lại rác nhưng thời khắc mang hoặc buông tay bị che khuất (hệ thống phải dùng cơ chế "tua ngược" 2.5 giây để liên kết người vừa đi qua). Thầy cô xem lại Thẻ sự kiện để xác nhận, tuyệt đối không quy kết vội vàng. |
| **3. Không đủ căn cứ** (`INSUFFICIENT_EVIDENCE`) | Rác mới xuất hiện nhưng không có lịch sử người mang, bị mất dấu hoặc là rác có sẵn từ trước. |

#### C. Thẻ sự kiện 3 khung hình (Event Card) và Làm mờ khuôn mặt
Phần mềm tự động lưu ảnh đệm tại 3 mốc (*Trước sự kiện* $\to$ *Tách rời* $\to$ *Sau sự kiện*) và ghép thành một **Thẻ sự kiện 3 khung hình** có ghi rõ thời gian, quan sát trực tiếp hay bị che khuất. Toàn bộ vùng khuôn mặt học sinh trên cả 3 ảnh đều được tự động làm mờ (bộ lọc Gauss) để bảo vệ quyền riêng tư theo đúng quy chế.

### 2.2. Nhiệm vụ 2: Phân loại rác tái chế và không tái chế (Thiết kế tích hợp)
Nhằm rèn luyện thói quen bỏ rác đúng ngăn phân loại trong trường học (thùng rác đôi gồm ngăn màu xanh lá cho *Rác tái chế* và ngăn màu vàng cho *Rác không tái chế*), dự án xây dựng thiết kế kỹ thuật gồm 4 điểm chính:
1. **Phân loại 2 nhóm rác bằng YOLO-World (`yolov8s-worldv2.pt`):**
   - *Rác tái chế (`recyclable`):* chai nhựa, lon kim loại, giấy, hộp giấy, hộp sữa.
   - *Rác không tái chế (`non_recyclable`):* túi nilon, vỏ bánh kẹo, hộp xốp, khăn giấy, ly và ống hút dùng một lần, rác thực phẩm.
   - Dùng cơ chế *bỏ phiếu ổn định theo thời gian* (Temporal Majority Voting) qua nhiều khung hình theo ID để tránh nhảy nhãn.
2. **Khai báo trực tiếp vùng ngăn thùng rác (Manual Bin Zone Input):** Tắt nhận diện thùng rác tự động để tiết kiệm tài nguyên và tránh nhầm lẫn 2 ngăn sát nhau; người dùng khai báo tọa độ 2 ngăn qua file cấu hình hoặc công cụ vẽ vùng.
3. **Cơ chế xử lý thùng rác kín (Disappearance-in-Zone):** Do thùng rác trường học là thùng kín có lỗ bỏ rác, khi học sinh bỏ rác vào thùng, rác biến mất ngay tại vùng miệng ngăn thùng. Nhánh này phát hiện sự kiện rác biến mất liên tục tại miệng thùng để đối chiếu loại rác với loại ngăn (kèm nhánh phục hồi nếu học sinh đặt tạm rồi cầm lại).
4. **Phân định 4 kết quả đánh giá tự giác:** `CORRECT_SORTING` (Bỏ đúng ngăn), `WRONG_BIN_DISPOSAL` (Bỏ sai ngăn), `POSSIBLE_LITTERING` (Vứt ngoài thùng), và `DISPOSAL_UNVERIFIED` (Đã bỏ vào thùng nhưng độ tin cậy phân loại chưa đủ).

---

## PHẦN 3: KẾT QUẢ THỰC NGHIỆM VÀ BẰNG CHỨNG (NHIỆM VỤ 1 - DEMO MVP)

### 3.1. Kết quả kiểm thử tự động và chạy thực tế trên 6 video trường học
- **Kiểm thử tự động (`pytest`):** Đạt **17/17 bài kiểm thử PASS** (bao gồm bộ kiểm thử mới cho suy luận chuỗi bằng chứng 3 mức và tạo Thẻ sự kiện 3 khung hình).
- **Thực nghiệm trên 6 video quay tại trường học:**

| STT | Tập tin Video | Địa điểm | Frame | Tốc độ | Sự kiện | Kết quả phân loại thực tế |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| 1 | `sample_01_corridor` | Hành lang trường | 502 | 16.6 FPS | 1 lần | Bắt đúng vứt chai cạnh thùng lúc 13.37s (`Cần kiểm tra thêm` do tay che khuất lúc đầu) |
| 2 | `sample_02_classroom` | Trong lớp học | 203 | 20.3 FPS | 0 lần | Đúng logic: Rác giấu trong hộc bàn gỗ, không báo bừa |
| 3 | `sample_03_corridor_drop` | Hành lang dọc | 284 | 18.1 FPS | 1 lần | Bắt đúng cú thả chai lúc 00.93s (`Cần kiểm tra thêm` kèm Thẻ sự kiện 3 ảnh) |
| 4 | `sample_04_schoolyard` | Sân trường cây | 466 | 19.9 FPS | 0 lần | Chính xác: Bóng lá cây lay động không gây báo giả |
| 5 | `sample_05_balcony` | Ban công lầu 2 | 395 | 20.3 FPS | 0 lần | Chính xác: Học sinh đi lại tay không, an toàn |
| 6 | `sample_06_distant` | Sân trường xa | 419 | 19.9 FPS | 0 lần | Chính xác: Góc nhìn rộng ổn định, không nhiễu |

### 3.2. Bằng chứng trực quan: Thẻ sự kiện 3 khung hình và Key Frames
- **Video 1 & Video 3:** Xuất tự động **Thẻ sự kiện 3 khung hình** (`sample_01_corridor_littering_EVT_0001_card.jpg`, `sample_03_corridor_drop_near_bin_EVT_0001_card.jpg`), ghi rõ các mốc thời gian, trạng thái bị che khuất/truy vết ngược và gắn mức **Cần kiểm tra thêm** kèm làm mờ khuôn mặt học sinh.
- **Video 2, 4, 5, 6:** Minh chứng các trường hợp rác bị che khuất trong hộc bàn, bóng cây lay động, học sinh đi tay không và góc nhìn từ xa — hệ thống không phát sinh báo động giả.

---

## PHẦN 4: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN (FUTURE WORK)

### 4.1. Kết luận khoa học và phạm vi sản phẩm hiện tại
1. Dự án hiện dừng ở mức độ **Demo MVP (Sản phẩm khả dụng tối thiểu)**, tập trung chứng minh các tính năng lõi quan trọng nhất là **phần Trí tuệ nhân tạo (AI)** và suy luận hành vi.
2. Đã hoàn thiện và kiểm chứng **Nhiệm vụ 1** (phát hiện xả rác theo chuỗi bằng chứng 3 mức + Thẻ sự kiện 3 khung hình làm mờ mặt) với tốc độ 16.6 - 20.3 FPS và 17/17 bài test đạt chuẩn.
3. Đã xây dựng hoàn chỉnh thiết kế kỹ thuật cho **Nhiệm vụ 2** (phân loại rác tái chế / không tái chế và đánh giá bỏ đúng ngăn thùng kín).

### 4.2. Hướng phát triển tương lai (Future Work)
Hướng đi mà dự án nhắm tới là **đưa hệ thống AI này vào môi trường giáo dục thực tế**:
1. **Hoàn thiện tích hợp Nhiệm vụ 2:** Triển khai mã nguồn phân loại rác tái chế / không tái chế và thử nghiệm tại các cụm thùng rác phân loại của trường học.
2. **Hợp tác từ phía nhà trường để truy cập hệ thống Camera:** Phối hợp cùng Ban Giám hiệu xin cấp quyền kết nối an toàn tới hệ thống camera sẵn có ở hành lang, sân trường và khu vực đặt thùng rác.
3. **Hợp tác với các ứng dụng quản lý học sinh như eNetViet:** Tích hợp gửi thông báo tự động, kịp thời và kín đáo cho giáo viên cũng như học sinh về các vi phạm xả rác hoặc bỏ nhầm ngăn phân loại, hướng tới mục tiêu nâng cao ý thức tự giác bảo vệ môi trường học đường.

---

## TÀI LIỆU THAM KHẢO

1. Bộ Giáo dục và Đào tạo (2026), *Thông tư số 84/2026/TT-BGDĐT ban hành Quy chế Cuộc thi NCKH kỹ thuật quốc gia dành cho học sinh THCS và THPT*, Hà Nội.
2. Sở Giáo dục và Đào tạo TP Đà Nẵng (2026), *Công văn số 6068/SGDĐT-GDTrH&HSSV về hướng dẫn nộp hồ sơ Cuộc thi NCKH cấp thành phố năm học 2026-2027*, Đà Nẵng.
3. Bochkovskiy, A., Wang, C. Y., & Liao, H. Y. M. (2020), *YOLOv4: Tối ưu hóa tốc độ và độ chính xác trong nhận diện vật thể*, Kỷ yếu nghiên cứu thị giác máy tính.
4. Cheng, L., và các tác giả (2024), *YOLO-World: Mô hình nhận diện đối tượng mở theo thời gian thực*, Hội nghị IEEE/CVF CVPR.
5. Zhang, Y., Sun, P., và các tác giả (2022), *ByteTrack: Thuật toán theo dõi đa đối tượng bằng cách liên kết toàn bộ hộp nhận diện*, Hội nghị ECCV, Nhà xuất bản Springer.
6. Jocher, G., & Chaurasia, A. (2024), *Ultralytics YOLO11: Các mô hình thị giác máy tính tiên tiến thời gian thực*, Tài liệu nghiên cứu mã nguồn mở Ultralytics.
