// ==============================================================================
// TYPST SOURCE CHO POSTER ĐIỆN TỬ TRÌNH CHIẾU (PHỤ LỤC 8)
// Cuộc thi NCKH-KT cấp thành phố dành cho học sinh THCS & THPT năm học 2026 - 2027
// Khổ A4 Dọc (Portrait), ĐÚNG 04 TRANG — Chữ TO (14pt), ĐẦY TRANG, Ưu tiên Visualization
// ==============================================================================

#set page(
  paper: "a4",
  margin: (x: 1.0cm, top: 0.9cm, bottom: 0.95cm),
  footer: align(center)[
    #text(size: 10.5pt, weight: "bold", fill: rgb("#455a64"))[
      Dự án KHKT cấp THCS  •  Hệ thống AI phát hiện hành vi xả rác & hỗ trợ phân loại rác học đường  •  Trang #context counter(page).display() / 4
    ]
  ]
)

#set text(
  font: "Times New Roman",
  size: 13pt,
  lang: "vi",
)

#set par(
  leading: 0.72em,
  justify: true,
  spacing: 5.5pt,
)

// ==============================================================================
// TRANG 1: TỔNG QUAN DỰ ÁN, HAI NHIỆM VỤ & 4 KỸ THUẬT CỐT LÕI
// ==============================================================================
#rect(width: 100%, fill: rgb("#0d47a1"), radius: 10pt, inset: 15pt)[
  #align(center)[
    #text(size: 19pt, weight: "bold", fill: white)[
      HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC\
      VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC\
      BẰNG THỊ GIÁC MÁY TÍNH
    ]\
    #v(0.2cm)
    #rect(fill: rgb("#1b5e20"), radius: 12pt, inset: (x: 14pt, y: 5pt))[
      #text(size: 13pt, weight: "bold", fill: white)[
        Lĩnh vực: Công nghệ thông tin   |   Cấp THCS   |   Năm học 2026 - 2027
      ]
    ]
  ]
]

#v(0.25cm)

#rect(width: 100%, stroke: 1.8pt + rgb("#1565c0"), inset: 14pt, radius: 8pt, fill: rgb("#f3f8ff"))[
  #text(size: 16pt, weight: "bold", fill: rgb("#0d47a1"))[1. ĐẶT VẤN ĐỀ & MỤC TIÊU NGHIÊN CỨU]
  #v(0.2cm)
  - *Thực trạng học đường:* Vẫn còn tình trạng vứt vỏ chai, hộp giấy ra sân trường và bỏ nhầm ngăn thùng rác đôi (ngăn xanh lá: *Rác tái chế* / ngăn vàng: *Rác không tái chế*).
  - *Hạn chế của camera hiện nay:* Chỉ ghi hình thụ động; mỗi khi sân trường có rác, thầy cô giám thị phải ngồi tua lại hàng giờ video rất vất vả.
  - *Mục tiêu dự án:* Xây dựng *phiên bản thử nghiệm lõi AI* gọn nhẹ chạy trên máy tính phổ thông của trường học, quan sát trung thực, không báo oan và *tự động làm mờ khuôn mặt* học sinh để bảo vệ quyền riêng tư.
]

#v(0.25cm)

#rect(width: 100%, stroke: 1.8pt + rgb("#2e7d32"), inset: 14pt, radius: 8pt, fill: rgb("#f1f8e9"))[
  #text(size: 16pt, weight: "bold", fill: rgb("#1b5e20"))[2. HAI NHIỆM VỤ CỐT LÕI GẮN KẾT]
  #v(0.2cm)
  #grid(
    columns: (1fr, 1fr),
    gutter: 12pt,
    rect(width: 100%, fill: white, stroke: 1pt + rgb("#66bb6a"), radius: 6pt, inset: 11pt)[
      #text(size: 14.5pt, weight: "bold", fill: rgb("#0d47a1"))[Nhiệm vụ 1: Phát hiện xả rác]\
      #v(0.1cm)
      Quan sát chuỗi *Cầm rác → Tách khỏi tay → Nằm ngoài thùng*; bỏ qua rác cũ nằm sẵn để không báo oan; phân 3 mức bằng chứng rõ ràng.
    ],
    rect(width: 100%, fill: white, stroke: 1pt + rgb("#66bb6a"), radius: 6pt, inset: 11pt)[
      #text(size: 14.5pt, weight: "bold", fill: rgb("#1b5e20"))[Nhiệm vụ 2: Phân loại rác]\
      #v(0.1cm)
      Nhận diện *Rác tái chế* (chai nhựa, hộp bìa, lon) và *Không tái chế* (bao nilon, vỏ gói bánh) rồi đối chiếu ngăn thùng để báo *Đúng / Sai ngăn*.
    ]
  )
]

#v(0.25cm)

#rect(width: 100%, fill: rgb("#fff8e1"), stroke: 1.8pt + rgb("#ef6c00"), radius: 8pt, inset: 14pt)[
  #align(center)[#text(size: 15.5pt, weight: "bold", fill: rgb("#e65100"))[3. BỐN KỸ THUẬT CỐT LÕI GIÚP HỆ THỐNG GỌN NHẸ & CHÍNH XÁC]]
  #v(0.25cm)
  #grid(
    columns: (1fr, 1fr),
    gutter: 10pt,
    rect(width: 100%, fill: white, stroke: 1pt + rgb("#ffa726"), radius: 6pt, inset: 11pt)[
      #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[1. "Kính lúp 4K" hai vùng bám]\
      #v(0.08cm)
      Cắt phóng to vùng ảnh gốc quanh người và vật thể rác đang bay để nhìn rõ mẩu rác nhỏ ngoài sân rộng.
    ],
    rect(width: 100%, fill: white, stroke: 1pt + rgb("#ffa726"), radius: 6pt, inset: 11pt)[
      #text(size: 14pt, weight: "bold", fill: rgb("#1b5e20"))[2. Lọc người chính & Theo dấu]\
      #v(0.08cm)
      Chỉ giữ tối đa 2 người rõ nhất (độ tin cậy ≥ 85%) và theo dấu liên tục bằng ByteTrack, tránh nhiễu người ở xa.
    ],
    rect(width: 100%, fill: white, stroke: 1pt + rgb("#ffa726"), radius: 6pt, inset: 11pt)[
      #text(size: 14pt, weight: "bold", fill: rgb("#6a1b9a"))[3. Bỏ phiếu & Miệng thùng kín]\
      #v(0.08cm)
      Cộng dồn nhiều khung hình để chốt loại rác ổn định và nhận diện rác biến mất tại miệng ngăn thùng kín.
    ],
    rect(width: 100%, fill: white, stroke: 1pt + rgb("#ffa726"), radius: 6pt, inset: 11pt)[
      #text(size: 14pt, weight: "bold", fill: rgb("#c62828"))[4. Làm mờ mặt (Bản Demo thi)]\
      #v(0.08cm)
      Che mờ mặt khi trình bày dự thi để ẩn danh; khi triển khai thực tế tại trường cần định danh sẽ tắt tính năng này.
    ]
  )
]

#pagebreak()

// ==============================================================================
// TRANG 2: LUỒNG THỰC THI THUẬT TOÁN & CÁCH XỬ LÝ HAI NHIỆM VỤ
// ==============================================================================
#rect(width: 100%, fill: rgb("#1565c0"), radius: 8pt, inset: 12pt)[
  #align(center)[
    #text(size: 18pt, weight: "bold", fill: white)[LUỒNG THỰC THI THUẬT TOÁN & CÁC CÔNG NGHỆ CỐT LÕI]
  ]
]

#v(0.28cm)

#align(center)[
  #grid(
    columns: (1fr, auto, 1fr, auto, 1fr),
    align: horizon + center,
    gutter: 6pt,
    rect(width: 100%, height: 3.8cm, fill: rgb("#e3f2fd"), stroke: 1.5pt + rgb("#1565c0"), radius: 6pt, inset: 8pt)[
      #text(size: 13.5pt, weight: "bold", fill: rgb("#0d47a1"))[Bước 1\ Quét toàn cảnh]\
      #v(0.1cm)
      #text(size: 12.5pt)[YOLO11n tìm Người (≥ 85%, tối đa 2) & Thùng rác]
    ],
    text(size: 18pt, weight: "bold", fill: rgb("#1565c0"))[→],
    rect(width: 100%, height: 3.8cm, fill: rgb("#e8f5e9"), stroke: 1.5pt + rgb("#2e7d32"), radius: 6pt, inset: 8pt)[
      #text(size: 13.5pt, weight: "bold", fill: rgb("#1b5e20"))[Bước 2\ Kính lúp 4K]\
      #v(0.1cm)
      #text(size: 12.5pt)[Cắt ảnh gốc 4K quanh Người & Rác đang bay]
    ],
    text(size: 18pt, weight: "bold", fill: rgb("#1565c0"))[→],
    rect(width: 100%, height: 3.8cm, fill: rgb("#fff3e0"), stroke: 1.5pt + rgb("#ef6c00"), radius: 6pt, inset: 8pt)[
      #text(size: 13.5pt, weight: "bold", fill: rgb("#e65100"))[Bước 3\ Nhận diện rác]\
      #v(0.1cm)
      #text(size: 12.5pt)[YOLO-World phân loại Tái chế / Không tái chế]
    ],
  )
  #v(0.15cm)
  #text(size: 18pt, weight: "bold", fill: rgb("#1565c0"))[↓]
  #v(0.15cm)
  #grid(
    columns: (1fr, auto, 1fr),
    align: horizon + center,
    gutter: 10pt,
    rect(width: 100%, height: 3.3cm, fill: rgb("#f3e5f5"), stroke: 1.5pt + rgb("#6a1b9a"), radius: 6pt, inset: 9pt)[
      #text(size: 13.5pt, weight: "bold", fill: rgb("#4a148c"))[Bước 4: Theo dấu & Phân tích hành vi]\
      #v(0.1cm)
      #text(size: 12.5pt)[ByteTrack giữ mã vật thể; lọc rác cũ; phân tích chuỗi trạng thái & bỏ phiếu nhiều khung hình]
    ],
    text(size: 18pt, weight: "bold", fill: rgb("#1565c0"))[→],
    rect(width: 100%, height: 3.3cm, fill: rgb("#ffebee"), stroke: 1.5pt + rgb("#c62828"), radius: 6pt, inset: 9pt)[
      #text(size: 13.5pt, weight: "bold", fill: rgb("#b71c1c"))[Bước 5: Kết luận & Bảo vệ riêng tư]\
      #v(0.1cm)
      #text(size: 12.5pt)[Bật cảnh báo đúng/sai ngăn hoặc xả rác; tự động làm mờ khuôn mặt trên mọi ảnh bằng chứng]
    ],
  )
]

#v(0.5cm)

#rect(width: 100%, stroke: 1.6pt + rgb("#0277bd"), inset: 14pt, radius: 8pt, fill: rgb("#f4fbfe"))[
  #text(size: 15.5pt, weight: "bold", fill: rgb("#01579b"))[A. CÁCH XỬ LÝ NHIỆM VỤ 1 (PHÁT HIỆN HÀNH VI XẢ RÁC)]
  #v(0.2cm)
  - *Lọc rác nằm sẵn:* Những mẩu rác đứng yên ngay từ đầu video (không đi kèm người) được đánh dấu là "rác nền" và bỏ qua hoàn toàn để *không báo oan*.
  - *Đo khoảng cách chuẩn hóa:* Chia khoảng cách rác–người cho chiều cao người để đo công bằng dù học sinh đứng gần hay xa camera.
  - *Phân 3 mức bằng chứng nhân văn:*
    1. *Đủ bằng chứng rõ ràng:* Camera nhìn thấy trực tiếp cả 3 bước *Cầm → Buông → Nằm ngoài thùng*.
    2. *Cần thầy cô kiểm tra thêm:* Khoảnh khắc buông tay bị che khuất → dò ngược vài giây trước để tìm người đi ngang qua gần nhất.
    3. *Không đủ căn cứ:* Rác không rõ nguồn gốc → không đưa ra cảnh báo.
]

#v(0.28cm)

#rect(width: 100%, stroke: 1.6pt + rgb("#e65100"), inset: 14pt, radius: 8pt, fill: rgb("#fff8f5"))[
  #text(size: 15.5pt, weight: "bold", fill: rgb("#bf360c"))[B. CÁCH XỬ LÝ NHIỆM VỤ 2 (PHÂN LOẠI RÁC TÁI CHẾ / KHÔNG TÁI CHẾ)]
  #v(0.2cm)
  - *Khoanh sẵn 2 ngăn thùng cố định:* Định vị chính xác ngăn *Rác tái chế* (xanh lá) và ngăn *Rác không tái chế* (vàng), tránh nhầm ranh giới giữa hai ngăn đặt sát nhau.
  - *Bỏ phiếu nhiều khung hình:* Cộng dồn điểm tin cậy qua nhiều khung hình liên tiếp để chốt loại rác ổn định dù rác bị xoay nhiều góc trên tay.
  - *Nhận diện biến mất tại miệng thùng kín:* Khi rác đi vào vùng ngăn thùng rồi biến mất vào bên trong, chương trình đối chiếu loại rác với loại ngăn để bật ngay thanh *Xanh lá (Bỏ đúng ngăn)* hoặc *Cam (Bỏ sai ngăn)*.
]

#pagebreak()

// ==============================================================================
// TRANG 3: MINH CHỨNG THỰC NGHIỆM TRỰC QUAN (VISUALIZATION 8 ẢNH THẬT)
// ==============================================================================
#rect(width: 100%, fill: rgb("#2e7d32"), radius: 8pt, inset: 12pt)[
  #align(center)[
    #text(size: 18pt, weight: "bold", fill: white)[HÌNH ẢNH MINH CHỨNG THỰC NGHIỆM TẠI TRƯỜNG HỌC]
  ]
]

#v(0.25cm)
#text(size: 14.5pt, weight: "bold", fill: rgb("#0d47a1"))[1. Nhiệm vụ 1 — Phát hiện 2 hành vi ném vật thể (hộp bìa & chai nhựa) ngoài sân trường:]
#v(0.15cm)

#grid(
  columns: (1fr, 1fr),
  gutter: 8pt,
  [
    #align(center)[#image("../outputs/report_selected/IMG_6830_task1_0067.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Bước 1: Học sinh cầm 2 món rác tiến lại gần thùng rác màu cam.]]
  ],
  [
    #align(center)[#image("../outputs/report_selected/IMG_6830_task1_0121.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Bước 2: Bám sát người chính, thấy rõ chai nhựa & mờ mặt gọn.]]
  ],
  [
    #align(center)[#image("../outputs/report_selected/IMG_6830_task1_0163.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Bước 3: Khoảnh khắc bạn học sinh ném hộp bìa carton cạnh thùng.]]
  ],
  [
    #align(center)[#image("../outputs/report_selected/IMG_6830_task1_0178.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Bước 4: Cả hộp bìa và chai nhựa rơi ngoài thùng; AI nối vết & chốt bằng chứng.]]
  ]
)

#v(0.3cm)
#text(size: 14.5pt, weight: "bold", fill: rgb("#1b5e20"))[2. Nhiệm vụ 2 — Phân loại rác Tái chế / Không tái chế ở góc chính diện & góc sau thùng:]
#v(0.15cm)

#grid(
  columns: (1fr, 1fr),
  gutter: 8pt,
  [
    #align(center)[#image("../outputs/report_selected/IMG_6821_task2_0260.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Bao nilon trắng bỏ đúng ngăn Không tái chế → Thanh xanh Đúng ngăn.]]
  ],
  [
    #align(center)[#image("../outputs/report_selected/IMG_6822_task2_0120.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Chai nhựa bỏ nhầm ngăn Không tái chế → Thanh cam Sai ngăn.]]
  ],
  [
    #align(center)[#image("../outputs/report_selected/IMG_6822_task2_0386.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Chai nhựa khác bỏ đúng ngăn Rác tái chế → Thanh xanh Đúng ngăn.]]
  ],
  [
    #align(center)[#image("../outputs/report_selected/IMG_6823_task2_0736.jpg", height: 4.65cm)]
    #align(center)[#text(size: 10.5pt, style: "italic")[Góc quay từ sau thùng (mờ mặt tự động): Hộp bìa bỏ đúng ngăn Tái chế.]]
  ]
)

#pagebreak()

// ==============================================================================
// TRANG 4: TỔNG HỢP KẾT QUẢ, KẾT LUẬN & HƯỚNG PHÁT TRIỂN TƯƠNG LAI
// ==============================================================================
#rect(width: 100%, fill: rgb("#0d47a1"), radius: 8pt, inset: 12pt)[
  #align(center)[
    #text(size: 18pt, weight: "bold", fill: white)[TỔNG HỢP KẾT QUẢ, KẾT LUẬN & HƯỚNG PHÁT TRIỂN]
  ]
]

#v(0.25cm)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 10pt,
  rect(width: 100%, fill: rgb("#e3f2fd"), stroke: 1.5pt + rgb("#1565c0"), radius: 8pt, inset: 10pt)[
    #align(center)[#text(size: 15pt, weight: "bold", fill: rgb("#0d47a1"))[2 NHIỆM VỤ]\ #v(0.05cm) #text(size: 12pt)[Phát hiện xả rác &\ Phân loại rác tại thùng đôi]]
  ],
  rect(width: 100%, fill: rgb("#e8f5e9"), stroke: 1.5pt + rgb("#2e7d32"), radius: 8pt, inset: 10pt)[
    #align(center)[#text(size: 15pt, weight: "bold", fill: rgb("#1b5e20"))[100% MỜ MẶT]\ #v(0.05cm) #text(size: 12pt)[Bảo vệ tuyệt đối\ quyền riêng tư học sinh]]
  ],
  rect(width: 100%, fill: rgb("#fff3e0"), stroke: 1.5pt + rgb("#ef6c00"), radius: 8pt, inset: 10pt)[
    #align(center)[#text(size: 15pt, weight: "bold", fill: rgb("#e65100"))[CHẠY GỌN NHẸ]\ #v(0.05cm) #text(size: 12pt)[Kính lúp 4K + YOLO11n\ + YOLO-World + ByteTrack]]
  ],
)

#v(0.28cm)

#text(size: 15.5pt, weight: "bold", fill: rgb("#1b5e20"))[1. BẢNG TỔNG HỢP 4 THỬ NGHIỆM PHÂN LOẠI RÁC TẠI TRƯỜNG HỌC]
#v(0.15cm)
#table(
  columns: (23%, 14%, 14%, 49%),
  inset: 7pt,
  align: (left, center, center, left),
  fill: (_, row) => if row == 0 { rgb("#c8e6c9") } else if calc.odd(row) { rgb("#f9fbe7") } else { white },
  stroke: 0.7pt + luma(140),
  [*Tình huống*], [*Đúng*], [*Sai*], [*Diễn biến hệ thống ghi nhận được*],
  [Thử nghiệm 1], [3], [0], [Lon nước, hộp bìa, chai nhựa bỏ đúng ngăn Tái chế],
  [Thử nghiệm 2], [2], [0], [Bao nilon trắng bỏ đúng ngăn Không tái chế],
  [Thử nghiệm 3], [1], [3], [Chai nhựa bỏ nhầm ngăn Không tái chế; 1 lượt bỏ đúng ngăn],
  [Thử nghiệm 4], [3], [3], [Góc sau thùng: vỏ gói bánh sai ngăn; chai & bìa đúng từng lượt]
)

#v(0.28cm)

#rect(width: 100%, stroke: 1.6pt + rgb("#2e7d32"), inset: 13pt, radius: 8pt, fill: rgb("#f6fbf6"))[
  #text(size: 15.5pt, weight: "bold", fill: rgb("#1b5e20"))[2. KẾT LUẬN]
  #v(0.15cm)
  - Hoàn thiện thành công *phiên bản thử nghiệm lõi*, chứng minh học sinh THCS hoàn toàn có thể ứng dụng Trí tuệ nhân tạo giải quyết đồng thời hai bài toán: *phát hiện xả rác* và *hỗ trợ phân loại rác*.
  - Nhận diện rõ vật thể nhỏ ngoài sân trường, phân biệt nhạy bén hành vi bỏ đúng/sai ngăn ở nhiều góc quay khác nhau và giữ gìn trọn vẹn quyền riêng tư của bạn bè.
]

#v(0.25cm)

#rect(width: 100%, stroke: 1.6pt + rgb("#0277bd"), inset: 13pt, radius: 8pt, fill: rgb("#f4fbfe"))[
  #text(size: 15.5pt, weight: "bold", fill: rgb("#01579b"))[3. HƯỚNG PHÁT TRIỂN TƯƠNG LAI]
  #v(0.15cm)
  - *Hợp tác từ phía nhà trường:* Xin sự đồng thuận của Ban Giám hiệu để kết nối an toàn với hệ thống camera sẵn có tại hành lang, sân trường và khu vực đặt thùng rác phân loại.
  - *Liên kết ứng dụng quản lý học sinh (như eNetViet):* Gửi thông báo nhắc nhở tự động, kín đáo đến giáo viên và học sinh khi có vi phạm, góp phần xây dựng ngôi trường xanh - sạch - đẹp một cách tự giác.
]

#v(0.25cm)

#rect(width: 100%, fill: rgb("#e8f5e9"), stroke: 1.2pt + rgb("#4caf50"), inset: 10pt, radius: 8pt)[
  #align(center)[
    #text(size: 13.5pt, weight: "bold", fill: rgb("#2e7d32"))[CAM KẾT LIÊM CHÍNH KHOA HỌC & BẢO VỆ QUYỀN RIÊNG TƯ HỌC SINH]\
    #v(0.08cm)
    #text(size: 12pt)[Ảnh minh chứng trong bản Demo dự thi đã tự động làm mờ mặt theo Thông tư 84/2026/TT-BGDĐT; khi áp dụng thực tế nội bộ tại trường cần tính định danh, tính năng làm mờ này sẽ được tắt.]
  ]
]
