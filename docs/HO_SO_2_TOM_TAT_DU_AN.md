# BÁO CÁO TÓM TẮT KẾT QUẢ THỰC HIỆN DỰ ÁN
*(Mẫu theo Phụ lục 4 - Công văn số 6068/SGDĐT-GDTrH&HSSV TP Đà Nẵng)*

---

**TÊN DỰ ÁN:**  
**NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC BẰNG THỊ GIÁC MÁY TÍNH VÀ SUY LUẬN KHÔNG - THỜI GIAN**

**LĨNH VỰC DỰ THI:** Hệ thống nhúng và Phần mềm hệ thống

---

### TÓM TẮT NỘI DUNG DỰ ÁN

Tình trạng vứt rác bừa bãi và bỏ sai ngăn phân loại tại trường học gây ảnh hưởng xấu đến môi trường, trong khi camera hiện nay chỉ ghi hình thụ động khiến thầy cô rà soát thủ công rất vất vả. Dự án xây dựng hệ thống Trí tuệ nhân tạo (AI) gồm hai nhiệm vụ: (1) Phát hiện hành vi xả rác không đúng nơi quy định; (2) Phân loại rác tái chế và không tái chế nhằm nâng cao tính tự giác bỏ rác đúng ngăn.

Ở mức Demo MVP tập trung vào phần lõi AI, hệ thống kết hợp thị giác máy tính và suy luận không - thời gian: nhận diện Người, Rác nhỏ (YOLO11m) và Thùng rác hoặc loại rác (YOLO-World); theo dấu bằng ByteTrack; lọc rác cũ; và suy luận theo chuỗi bằng chứng 3 mức (Đủ bằng chứng thị giác, Cần kiểm tra thêm, Không đủ căn cứ) nhằm tránh quy kết vội vàng. Khi có sự kiện, phần mềm tự động xuất Thẻ sự kiện 3 khung hình có làm mờ khuôn mặt học sinh. Với nhiệm vụ phân loại rác, dự án đã thiết kế kiến trúc khai báo vùng ngăn thùng, bỏ phiếu ổn định theo thời gian và nhận diện rác biến mất tại miệng thùng kín để đánh giá bỏ đúng hay sai ngăn.

Thực nghiệm nhiệm vụ 1 trên 6 video trường học đạt tốc độ 16.6 đến 20.3 khung hình/giây, phát hiện đúng các ca vứt rác, không báo oan rác cũ và vượt qua 17/17 bài kiểm thử tự động. Trong tương lai, dự án hướng tới hợp tác với nhà trường truy cập camera và liên kết ứng dụng quản lý như eNetViet để nhắc nhở giáo viên, học sinh kịp thời.
