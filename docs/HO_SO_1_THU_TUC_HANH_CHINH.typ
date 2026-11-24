// TYPST SOURCE CHO HỒ SƠ 1: THỦ TỤC HÀNH CHÍNH, PHÁP LÝ VÀ LIÊM CHÍNH KHOA HỌC
// Tuân thủ Thông tư 84/2026/TT-BGDĐT và Công văn 6068/SGDĐT-GDTrH&HSSV TP Đà Nẵng
// Khổ A4, lề chuẩn (trái 3cm, phải 2cm, trên 2cm, dưới 2cm), Times New Roman 13pt

#set page(
  paper: "a4",
  margin: (left: 3cm, right: 2cm, top: 2cm, bottom: 2cm),
  numbering: "1",
)

#set text(
  font: "Times New Roman",
  size: 13pt,
  lang: "vi",
)

#set par(
  leading: 0.8em,
  justify: true,
  spacing: 6pt,
)

#show heading.where(level: 1): it => block(above: 1.2em, below: 0.8em)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[#it.body]
]
#show heading.where(level: 2): it => block(above: 1.0em, below: 0.6em)[
  #text(size: 13pt, weight: "bold", fill: rgb("#1565c0"))[#it.body]
]
#show heading.where(level: 3): it => block(above: 0.8em, below: 0.5em)[
  #text(size: 13pt, weight: "bold", style: "italic")[#it.body]
]

// ==========================================
// TRANG BÌA HỒ SƠ 1
// ==========================================
#align(center)[
  #text(size: 13pt, weight: "bold")[SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG]\
  #text(size: 13pt, weight: "bold")[CUỘC THI NGHIÊN CỨU KHOA HỌC, KỸ THUẬT CẤP THÀNH PHỐ]\
  #text(size: 12pt, weight: "bold")[DÀNH CHO HỌC SINH THCS VÀ THPT NĂM HỌC 2026 - 2027]
  
  #v(2.2cm)
  
  #text(size: 18pt, weight: "bold", fill: rgb("#0d47a1"))[HỒ SƠ 1]\
  #text(size: 15pt, weight: "bold")[THỦ TỤC HÀNH CHÍNH, PHÁP LÝ VÀ LIÊM CHÍNH KHOA HỌC]
  
  #v(1.2cm)
  
  #rect(width: 100%, stroke: 1.5pt + rgb("#0d47a1"), inset: 15pt, radius: 4pt)[
    #set par(leading: 0.9em)
    #text(size: 14pt, weight: "bold")[
      DỰ ÁN: NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC BẰNG THỊ GIÁC MÁY TÍNH
    ]
  ]
  
  #v(1.8cm)
  
  #align(left)[
    #rect(width: 100%, stroke: 0.5pt + luma(150), inset: 12pt, fill: rgb("#f5f5f5"))[
      - *Lĩnh vực dự thi:* Công nghệ thông tin\
      - *Cấp học thực hiện:* Học sinh Trung học cơ sở (THCS)\
      - *Cơ sở giáo dục:* Trường Trung học cơ sở trên địa bàn thành phố Đà Nẵng\
      - *Năm học thực hiện:* 2026 - 2027
    ]
  ]
]

#pagebreak()

// ==========================================
// PHỤ LỤC 2B
// ==========================================
#align(center)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN 1: THUYẾT MINH QUY TRÌNH ĐĂNG KÝ, PHÊ DUYỆT VÀ LỰA CHỌN DỰ ÁN TẠI CƠ SỞ GIÁO DỤC]\
  #text(size: 11.5pt, style: "italic")[(Mẫu theo Phụ lục 2b - Ban hành kèm theo Công văn số 6068/SGDĐT-GDTrH&HSSV)]
]

#v(0.3cm)

1. *Thông tin dự án và tác giả:*
   - *Tên dự án:* Nghiên cứu và phát triển hệ thống trí tuệ nhân tạo phát hiện hành vi xả rác và hỗ trợ phân loại rác trong trường học bằng thị giác máy tính.
   - *Lĩnh vực:* Công nghệ thông tin.
   - *Học sinh thực hiện:* Học sinh cấp THCS có kết quả học tập và rèn luyện năm học 2025 - 2026 đạt mức Tốt.
   - *Người hướng dẫn:* Giáo viên bộ môn Tin học / Khoa học tự nhiên của nhà trường.

2. *Quy trình tổ chức triển khai tại nhà trường:*
   - *Giai đoạn 1 (Đăng ký ý tưởng - 09/2026):* Học sinh đăng ký ý tưởng xuất phát từ thực trạng xả rác và bỏ nhầm ngăn thùng rác phân loại trong trường học.
   - *Giai đoạn 2 (Thẩm định Kế hoạch nghiên cứu - 09/2026):* Tổ chuyên môn họp thẩm định, đánh giá đề tài có tính thiết thực, phù hợp với học sinh THCS và phân công giáo viên hướng dẫn.
   - *Giai đoạn 3 (Phê duyệt rủi ro và Kế hoạch nghiên cứu - 28/09/2026):* Hiệu trưởng nhà trường ký phê duyệt kế hoạch nghiên cứu; dự án được xếp loại mức An toàn.
   - *Giai đoạn 4 (Theo dõi và kiểm tra - 10/2026 đến 11/2026):* Tổ chuyên môn định kỳ kiểm tra nhật ký nghiên cứu, đôn đốc học sinh tuân thủ liêm chính khoa học và tự động làm mờ khuôn mặt khi xuất ảnh minh chứng.
   - *Giai đoạn 5 (Nghiệm thu cấp trường - 25/11/2026):* Hội đồng khoa học nhà trường đánh giá dự án đạt yêu cầu và chọn cử tham dự Cuộc thi cấp thành phố.

#pagebreak()

// ==========================================
// KẾ HOẠCH NGHIÊN CỨU
// ==========================================
#align(center)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN 2: KẾ HOẠCH NGHIÊN CỨU KHOA HỌC KỸ THUẬT]\
  #text(size: 11.5pt, style: "italic")[(Được Người đứng đầu cơ sở giáo dục phê duyệt trước khi tiến hành nghiên cứu)]
]

#v(0.3cm)

1. *Tên dự án:* Nghiên cứu và phát triển hệ thống trí tuệ nhân tạo phát hiện hành vi xả rác và hỗ trợ phân loại rác trong trường học bằng thị giác máy tính.
2. *Lý do chọn đề tài và Mục tiêu:* Góp phần giữ gìn môi trường học đường xanh - sạch - đẹp, khắc phục hạn chế ghi hình thụ động của camera thông thường bằng một phần mềm AI gọn nhẹ thực hiện đồng thời hai nhiệm vụ: (1) Phát hiện hành vi xả rác không đúng nơi quy định; (2) Hỗ trợ phân loại rác tái chế và không tái chế tại thùng rác đôi.
3. *Câu hỏi nghiên cứu:* Làm thế nào để xây dựng một phần mềm Trí tuệ nhân tạo gọn nhẹ chạy trên máy tính phổ thông của trường học, có thể nhìn rõ các mẩu rác nhỏ ngoài sân trường, không báo oan cho học sinh đi ngang qua rác cũ, đánh giá đúng việc bỏ rác đúng/sai ngăn và bảo vệ quyền riêng tư của học sinh?
4. *Phương pháp và các kỹ thuật cốt lõi dự kiến:*
   - Quay các tình huống giả lập thực tế tại sân trường và khu vực đặt thùng rác đôi (nhiều loại rác và góc quay khác nhau).
   - Áp dụng 4 kỹ thuật cốt lõi: (1) Quét toàn cảnh bằng YOLO11n kết hợp lọc người chính (độ tin cậy ≥ 85%, tối đa 2 người) và kỹ thuật *"Kính lúp 4K"* cắt phóng to vùng ảnh gốc quanh người và vật thể rác; (2) Nhận diện, phân loại rác bằng YOLO-World và theo dấu liên tục bằng ByteTrack; (3) Suy luận chuỗi trạng thái 3 mức bằng chứng (Nhiệm vụ 1) và bỏ phiếu nhiều khung hình kết hợp nhận diện biến mất tại miệng thùng kín (Nhiệm vụ 2); (4) Tự động làm mờ khuôn mặt bằng bộ lọc Gaussian.
5. *Cam kết an toàn:* Dự án hoàn toàn là phần mềm thị giác máy tính, không sử dụng hóa chất, vi sinh vật hay thiết bị điện nguy hiểm; cam kết che mờ 100% khuôn mặt học sinh trên mọi hình ảnh bằng chứng.

#pagebreak()

// ==========================================
// PHỤ LỤC 5: CÁC BIỂU MẪU RỦI RO & LIÊM CHÍNH
// ==========================================
#align(center)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN 3: CÁC BIỂU MẪU KIỂM SOÁT RỦI RO VÀ LIÊM CHÍNH KHOA HỌC]\
  #text(size: 11.5pt, style: "italic")[(Phụ lục 5: Phiếu IVa, IVb, IVc, IVd theo Thông tư số 84/2026/TT-BGDĐT)]
]

#v(0.3cm)

=== 1. PHIẾU PHÊ DUYỆT VÀ ĐÁNH GIÁ RỦI RO CỦA CƠ SỞ GIÁO DỤC (PHIẾU IVa)
- *Đối tượng nghiên cứu:* Dữ liệu video tình huống bỏ rác do học sinh tự diễn xuất trong khuôn viên trường học.
- *Biện pháp kiểm soát an toàn:* Có sự đồng thuận tự nguyện của học sinh tham gia (Phiếu IVd); trong phiên bản Demo dự thi, hệ thống tích hợp bộ lọc làm mờ Gaussian trên toàn bộ khuôn mặt khi xuất ảnh báo cáo, poster (khi áp dụng thực tế nội bộ tại nhà trường cần tính định danh thì tính năng này sẽ được tắt).
- *Ý kiến đánh giá:* Dự án phần mềm an toàn tuyệt đối, không có rủi ro hóa sinh; giải pháp tự động che mờ khuôn mặt bảo đảm đầy đủ tiêu chuẩn bảo vệ quyền riêng tư học sinh.
- *Kết luận của Hiệu trưởng:* Phê duyệt dự án ở mức An toàn.

=== 2. PHIẾU CAM KẾT VỀ LIÊM CHÍNH KHOA HỌC (PHIẾU IVb)
- Học sinh và Giáo viên hướng dẫn cam kết: Toàn bộ ý tưởng kết hợp hai nhiệm vụ, luồng xử lý "Kính lúp 4K", logic suy luận hành vi xả rác 3 mức, cơ chế bỏ phiếu nhiều khung hình cho thùng rác kín và các video thực nghiệm là do nhóm tác giả tự thực hiện; các mô hình AI mã nguồn mở (YOLO11n, YOLO-World, ByteTrack, OpenCV) được kế thừa hợp pháp và trích dẫn đầy đủ.

=== 3. PHIẾU XÁC NHẬN CƠ SỞ TỔ CHỨC THỰC NGHIỆM (PHIẾU IVc)
- Nhà trường xác nhận đã tạo điều kiện về phòng máy tính và khu vực sân trường, hành lang đặt thùng rác đôi để học sinh quay video thử nghiệm ngoài giờ học, đảm bảo an toàn và nề nếp chung.

=== 4. PHIẾU ĐỒNG Ý CUNG CẤP THÔNG TIN VÀ THAM GIA NGHIÊN CỨU (PHIẾU IVd)
- Toàn bộ học sinh tham gia quay video minh họa đều được phổ biến rõ mục đích vì môi trường học đường, tự nguyện đồng ý tham gia và được bảo đảm làm mờ khuôn mặt trên mọi hình ảnh đưa vào báo cáo, poster.

#pagebreak()

// ==========================================
// PHỤ LỤC 6: NHẬT KÝ NGHIÊN CỨU (Ô XÁC NHẬN ĐỂ TRỐNG)
// ==========================================
#align(center)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN 4: NHẬT KÝ NGHIÊN CỨU]\
  #text(size: 11.5pt, style: "italic")[(Mẫu theo Phụ lục 6 - Ghi chép định kỳ từ tháng 9/2026 đến tháng 11/2026)]
]

#v(0.25cm)

#table(
  columns: (0.8fr, 2.2fr, 4.4fr, 2.8fr, 1.8fr),
  stroke: 0.5pt + luma(150),
  fill: (x, y) => if y == 0 { rgb("#bbdefb") } else if calc.even(y) { rgb("#f5f5f5") } else { none },
  inset: (x: 5pt, y: 6pt),
  align: (center, left, left, left, center),
  table.header(
    [*Tuần*], [*Thời gian*], [*Nội dung công việc*], [*Kết quả đạt được*], [*Xác nhận*]
  ),
  [T1], [01/09 - 06/09/26], [Khảo sát thực trạng xả rác và bỏ nhầm ngăn thùng rác đôi tại trường], [Xác định 2 nhiệm vụ cốt lõi của dự án], [],
  [T2], [07/09 - 13/09/26], [Lập Kế hoạch nghiên cứu và hoàn thiện các phiếu an toàn (IVa–IVd)], [Hoàn tất hồ sơ đăng ký & phê duyệt], [],
  [T3], [14/09 - 20/09/26], [Cài đặt môi trường Python, OpenCV và chạy thử mô hình YOLO11n], [Nhận diện được người và thùng rác], [],
  [T4], [21/09 - 27/09/26], [Xây dựng bộ lọc người chính (độ tin cậy ≥ 85%, tối đa 2 người rõ nhất)], [Loại bỏ nhiễu từ người ngồi xa ở căng-tin], [],
  [T5], [28/09 - 04/10/26], [Thiết kế kỹ thuật "Kính lúp 4K" cắt vùng ảnh gốc quanh người và rác], [Nhìn rõ chai nhựa, hộp bìa ngoài sân rộng], [],
  [T6], [05/10 - 11/10/26], [Tích hợp YOLO-World nhận diện và phân nhóm rác Tái chế / Không tái chế], [Phân biệt được chai, hộp bìa, bao nilon, vỏ bánh], [],
  [T7], [12/10 - 18/10/26], [Tích hợp thuật toán theo dấu ByteTrack và bộ lọc bỏ qua rác cũ nằm sẵn], [Theo dõi liên tục người & rác, không báo oan], [],
  [T8], [19/10 - 25/10/26], [Xây dựng suy luận chuỗi trạng thái 3 mức bằng chứng cho Nhiệm vụ 1], [Phát hiện rõ hành vi vứt rác ra ngoài thùng], [],
  [T9], [26/10 - 01/11/26], [Xây dựng bỏ phiếu nhiều khung hình & nhận diện rác biến mất tại miệng thùng kín], [Kết luận chính xác Bỏ đúng ngăn / Sai ngăn], [],
  [T10], [02/11 - 08/11/26], [Tích hợp thuật toán tự động làm mờ khuôn mặt bằng bộ lọc Gaussian], [Che kín khuôn mặt học sinh trên mọi ảnh xuất], [],
  [T11], [09/11 - 15/11/26], [Quay và thử nghiệm thực tế các tình huống ngoài sân trường & thùng rác đôi], [Ghi nhận đầy đủ ảnh minh chứng 4 tình huống], [],
  [T12], [16/11 - 25/11/26], [Hoàn thiện Báo cáo kết quả, Poster trình chiếu và Hồ sơ dự thi], [Hoàn tất trọn bộ hồ sơ nộp dự thi], []
)
#v(0.15cm)
#text(size: 10pt, style: "italic")[(Cột Xác nhận để trống để Giáo viên hướng dẫn ký xác nhận định kỳ trực tiếp theo Thông tư 84/2026/TT-BGDĐT)]

#pagebreak()

// ==========================================
// PHỤ LỤC 7: KHAI BÁO AI
// ==========================================
#align(center)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN 5: PHIẾU KHAI BÁO SỬ DỤNG CÔNG NGHỆ SỐ, TRÍ TUỆ NHÂN TẠO (AI)]\
  #text(size: 11.5pt, style: "italic")[(Mẫu theo Phụ lục 7 - Ban hành kèm theo Công văn số 6068/SGDĐT-GDTrH&HSSV)]
]

#v(0.3cm)

1. *Thông tin dự án:*
   - *Tên dự án:* Nghiên cứu và phát triển hệ thống trí tuệ nhân tạo phát hiện hành vi xả rác và hỗ trợ phân loại rác trong trường học bằng thị giác máy tính.
   - *Lĩnh vực:* Công nghệ thông tin.

2. *Bảng kê khai chi tiết các công nghệ Trí tuệ nhân tạo (AI):*

#table(
  columns: (0.7fr, 2.4fr, 3.2fr, 3.6fr, 3.1fr),
  stroke: 0.5pt + luma(150),
  fill: (x, y) => if y == 0 { rgb("#c8e6c9") } else if calc.even(y) { rgb("#f9fbe7") } else { none },
  inset: (x: 5pt, y: 5pt),
  align: (center, left, left, left, left),
  table.header(
    [*TT*], [*Công nghệ AI*], [*Nguồn gốc / Bản quyền*], [*Mục đích sử dụng*], [*Đóng góp của học sinh*]
  ),
  [1], [*YOLO11n*], [Mã nguồn mở Ultralytics], [Quét toàn cảnh tìm vị trí Người và Thùng rác], [Thiết kế bộ lọc người chính (≥ 85%, tối đa 2 người)],
  [2], [*YOLO-World*], [Mã nguồn mở Tencent / Ultralytics], [Nhận diện và phân loại rác Tái chế / Không tái chế trên vùng phóng to 4K], [Xây dựng bộ từ khóa rác học đường & quy đổi tọa độ],
  [3], [*ByteTrack*], [Mã nguồn mở Zhang et al.], [Theo dấu liên tục người và từng món rác qua các khung hình], [Kết nối dữ liệu theo dấu vào chuỗi suy luận hành vi],
  [4], [*Trợ lý lập trình AI*], [Công cụ hỗ trợ lập trình], [Hỗ trợ rà soát lỗi cú pháp Python và trình bày tài liệu], [Học sinh tự xây dựng ý tưởng, kịch bản quay & kiểm chứng thực tế]
)

3. *Cam kết quyền tác giả và liêm chính:*
   - Nhóm tác giả khẳng định: *Toàn bộ ý tưởng giải quyết song song 2 nhiệm vụ, kỹ thuật "Kính lúp 4K" hai vùng bám, bộ lọc rác nằm sẵn, logic suy luận 3 mức bằng chứng, cơ chế bỏ phiếu nhiều khung hình cho thùng kín và quy trình tự động làm mờ khuôn mặt là do nhóm học sinh tự đề xuất, lắp ghép và kiểm chứng thực tế.*
   - Các mô hình AI nền tảng đều sử dụng đúng mục đích nghiên cứu học thuật, tuân thủ giấy phép mã nguồn mở.

#v(0.5cm)
#align(center)[#text(size: 11pt, style: "italic")[(Hồ sơ 1 hoàn tất, đúng quy chuẩn Thông tư 84/2026/TT-BGDĐT)]]
