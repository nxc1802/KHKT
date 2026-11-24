// ==============================================================================
// HỒ SƠ 2: BÁO CÁO KẾT QUẢ VÀ TÓM TẮT DỰ ÁN (CHUẨN KHKT CẤP THCS)
// Khổ A4, lề trái 3cm, phải 2cm, trên 2cm, dưới 2cm; Times New Roman 13pt
// Văn phong tự nhiên, gần gũi, dễ hiểu cho học sinh và giáo viên cấp THCS
// ==============================================================================

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
  spacing: 7pt,
)

#show heading.where(level: 1): it => block(above: 1.2em, below: 0.7em)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[#it.body]
]
#show heading.where(level: 2): it => block(above: 0.95em, below: 0.5em)[
  #text(size: 13pt, weight: "bold", fill: rgb("#1565c0"))[#it.body]
]
#show heading.where(level: 3): it => block(above: 0.75em, below: 0.4em)[
  #text(size: 13pt, weight: "bold", style: "italic")[#it.body]
]

// ==============================================================================
// TRANG BÌA (HOÀN TOÀN ẨN DANH)
// ==============================================================================
#align(center)[
  #text(size: 13pt, weight: "bold")[SỞ GIÁO DỤC VÀ ĐÀO TẠO THÀNH PHỐ ĐÀ NẴNG]\
  #text(size: 13pt, weight: "bold")[CUỘC THI NGHIÊN CỨU KHOA HỌC, KỸ THUẬT CẤP THÀNH PHỐ]\
  #text(size: 12pt, weight: "bold")[DÀNH CHO HỌC SINH THCS VÀ THPT NĂM HỌC 2026 - 2027]
  
  #v(2.0cm)
  
  #text(size: 16pt, weight: "bold", fill: rgb("#0d47a1"))[BÁO CÁO KẾT QUẢ THỰC HIỆN DỰ ÁN]
  
  #v(1.0cm)
  
  #rect(width: 100%, stroke: 1.5pt + rgb("#0d47a1"), inset: 15pt, radius: 4pt)[
    #set par(leading: 0.9em)
    #text(size: 14pt, weight: "bold")[
      NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC BẰNG THỊ GIÁC MÁY TÍNH
    ]
  ]
  
  #v(1.8cm)
  
  #align(left)[
    #rect(width: 100%, stroke: 0.5pt + luma(150), inset: 12pt, fill: rgb("#f5f5f5"))[
      - *Lĩnh vực dự thi:* Công nghệ thông tin\
      - *Cấp học thực hiện:* Học sinh Trung học cơ sở (THCS)\
      - *Phạm vi sản phẩm hiện tại:* Phiên bản thử nghiệm tập trung vào phần lõi Trí tuệ nhân tạo (AI)\
      - *Mã số dự án:* (Do Ban Tổ chức Cuộc thi cấp)\
      - *Năm học thực hiện:* 2026 - 2027
    ]
  ]
  
  #v(1.8cm)
  #text(size: 11pt, style: "italic", fill: luma(100))[
    (Báo cáo thực hiện ẩn danh theo đúng Quy chế Cuộc thi: Tuyệt đối không ghi tên trường, đơn vị dự thi, tên học sinh, người hướng dẫn hoặc chèn biểu trưng, logo)
  ]
]

#pagebreak()

// ==============================================================================
// PHẦN A: BÁO CÁO TÓM TẮT DỰ ÁN (PHỤ LỤC 4 - DƯỚI 300 TỪ)
// ==============================================================================
#[
  #set par(leading: 1.0em, spacing: 11pt)

  #align(center)[
    #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN A: BÁO CÁO TÓM TẮT KẾT QUẢ THỰC HIỆN DỰ ÁN]\
    #text(size: 11pt, style: "italic")[(Mẫu theo Phụ lục 4 - Công văn số 6068/SGDĐT-GDTrH&HSSV - Dưới 300 từ)]
  ]

  #v(0.5cm)

  *TÊN DỰ ÁN:*  
  #text(weight: "bold")[NGHIÊN CỨU VÀ PHÁT TRIỂN HỆ THỐNG TRÍ TUỆ NHÂN TẠO PHÁT HIỆN HÀNH VI XẢ RÁC VÀ HỖ TRỢ PHÂN LOẠI RÁC TRONG TRƯỜNG HỌC BẰNG THỊ GIÁC MÁY TÍNH]

  *LĨNH VỰC DỰ THI:* Công nghệ thông tin

  #v(0.2cm)
  *NỘI DUNG TÓM TẮT:*

  Tình trạng vứt rác bừa bãi và bỏ nhầm ngăn thùng phân loại trong trường học ảnh hưởng xấu đến môi trường, trong khi camera hiện nay chỉ ghi hình thụ động khiến thầy cô phải xem lại rất vất vả. Dự án xây dựng hệ thống Trí tuệ nhân tạo (AI) thực hiện hai nhiệm vụ: (1) Phát hiện hành vi xả rác không đúng nơi quy định; (2) Phân loại rác tái chế và không tái chế giúp học sinh rèn thói quen bỏ rác đúng ngăn.

  Ở phiên bản thử nghiệm hiện tại, hệ thống tập trung vào các kỹ thuật AI cốt lõi: nhận diện Người, Rác và Thùng rác; cắt phóng to vùng ảnh gốc quanh bạn học sinh để nhìn rõ mẩu rác nhỏ ngoài sân trường; theo dấu liên tục từng người và vật thể; lọc bỏ rác nằm sẵn từ trước để không báo oan. Hệ thống đánh giá hành vi theo 3 mức bằng chứng (Đủ bằng chứng rõ ràng, Cần thầy cô kiểm tra thêm, Không đủ căn cứ) và tự động làm mờ khuôn mặt để bảo vệ quyền riêng tư. Với nhiệm vụ phân loại, hệ thống tổng hợp kết quả qua nhiều khung hình và kiểm tra rác biến mất tại miệng ngăn thùng kín để biết học sinh bỏ đúng hay sai ngăn.

  Thực nghiệm trên video quay thực tế tại sân trường và thùng rác đôi cho thấy hệ thống nhận diện rõ người, vật thể rác và đánh giá đúng các tình huống bỏ đúng hoặc sai ngăn. Trong tương lai, dự án hướng tới hợp tác với nhà trường kết nối camera và liên kết ứng dụng quản lý như eNetViet để nhắc nhở kịp thời.
]

#pagebreak()

// ==============================================================================
// PHẦN B: BÁO CÁO KẾT QUẢ DỰ ÁN (PHỤ LỤC 3 - TỐI ĐA 15 TRANG)
// ==============================================================================
#align(center)[
  #text(size: 14pt, weight: "bold", fill: rgb("#0d47a1"))[PHẦN B: BÁO CÁO KẾT QUẢ THỰC HIỆN DỰ ÁN]\
  #text(size: 11pt, style: "italic")[(Mẫu theo Phụ lục 3 - Công văn số 6068/SGDĐT-GDTrH&HSSV TP Đà Nẵng)]
]

#v(0.2cm)

= PHẦN 1: ĐẶT VẤN ĐỀ VÀ MỤC TIÊU NGHIÊN CỨU

== 1.1. Lý do chọn đề tài
Hằng ngày khi đến trường, chúng em thấy nhà trường luôn đặt rất nhiều thùng rác ở sân trường và hành lang, trong đó có cả những chiếc thùng rác đôi phân loại thành hai ngăn rõ rệt: ngăn màu xanh lá đựng *Rác tái chế* (giấy, chai nhựa, lon nước) và ngăn màu vàng đựng *Rác không tái chế* (khăn giấy, túi nilon, vỏ bánh kẹo). Tuy nhiên, vào giờ ra chơi, vẫn còn tình trạng một số bạn vứt vỏ chai, hộp giấy ra nền sân hoặc vội vàng bỏ nhầm chai nhựa vào ngăn rác không tái chế.

Hiện nay, hầu hết các trường học đều đã lắp camera quan sát, nhưng những chiếc camera này chỉ có nhiệm vụ ghi hình lại. Mỗi khi sân trường có rác, thầy cô giám thị phải ngồi tua lại hàng giờ video để kiểm tra, vừa tốn thời gian vừa dễ bỏ sót. Từ thực tế gần gũi đó, chúng em nảy ra ý tưởng ứng dụng Trí tuệ nhân tạo (AI) để giúp camera "hiểu" được hình ảnh và tự động hỗ trợ nhà trường hai việc quan trọng:
1. *Nhiệm vụ 1:* Phát hiện hành vi xả rác không đúng nơi quy định (nhận biết bạn học sinh đã bỏ rác vào thùng hay vứt ra ngoài đất).
2. *Nhiệm vụ 2:* Nhận diện rác tái chế và rác không tái chế, từ đó biết học sinh bỏ đúng ngăn hay sai ngăn để kịp thời nhắc nhở, giúp các bạn hình thành thói quen phân loại rác tự giác.

== 1.2. Mục tiêu và phạm vi nghiên cứu
Mục tiêu của chúng em là xây dựng một phần mềm gọn nhẹ, có thể chạy trực tiếp trên máy tính phổ thông của nhà trường. Phần mềm phải quan sát trung thực, tuyệt đối không quy kết oan cho những bạn học sinh vô tình đi ngang qua mẩu rác cũ đã nằm sẵn trên sân, đồng thời phải bảo vệ quyền riêng tư của bạn bè bằng cách tự động làm mờ khuôn mặt trên mọi hình ảnh bằng chứng.

Ở giai đoạn hiện tại, dự án tập trung hoàn thiện *phiên bản thử nghiệm lõi*, tức là xây dựng và kiểm chứng kỹ phần quan trọng nhất: bộ não Trí tuệ nhân tạo (AI) phân tích video thực tế do chính chúng em quay tại sân trường.

#pagebreak()
= PHẦN 2: Ý TƯỞNG GIẢI PHÁP CHO HAI NHIỆM VỤ CỐT LÕI

== 2.1. Nhiệm vụ 1: Phát hiện hành vi xả rác không đúng nơi quy định
Nếu chỉ nhìn vào một tấm ảnh chụp đứng yên thì rất khó biết ai là người vứt rác, vì có thể bạn học sinh chỉ đang đi bộ ngang qua một vỏ chai có sẵn trên sân. Vì vậy, chúng em thiết kế phần mềm quan sát diễn biến theo thời gian giống như mắt người, đi qua 3 bước rõ ràng: *Bạn học sinh đang cầm rác → Rác rời khỏi tay → Rác nằm lại trên mặt đất hay đã rơi vào thùng rác*.

Nếu một mẩu rác đã nằm yên trên sân ngay từ lúc bắt đầu quay mà bạn học sinh chỉ đi ngang qua gần đó, phần mềm sẽ nhận ra đó là rác cũ và bỏ qua để *không báo oan*. Ngoài ra, ngoài sân trường đôi khi có người đi qua che khuất góc nhìn của camera, nên thay vì kết luận vội vàng, hệ thống chia kết quả thành *3 mức độ rõ ràng*:
- *Mức 1 — Đủ bằng chứng rõ ràng:* Camera nhìn thấy trọn vẹn từ lúc bạn học sinh cầm rác, buông tay cho đến khi rác nằm lại bên ngoài thùng.
- *Mức 2 — Cần thầy cô kiểm tra thêm:* Có dấu hiệu rác mới xuất hiện trên sân nhưng khoảnh khắc buông tay bị khuất góc nhìn. Lúc này, phần mềm tự động xem ngược lại vài giây trước đó để tìm người vừa đi qua và xuất ra chuỗi ảnh cho thầy cô xem lại.
- *Mức 3 — Không đủ căn cứ:* Rác không rõ nguồn gốc hoặc bị mất dấu giữa chừng, hệ thống sẽ không đưa ra cảnh báo.

== 2.2. Nhiệm vụ 2: Phân loại rác tái chế và không tái chế
Với cụm thùng rác đôi đặt cố định trong trường học, hai ngăn xanh lá và vàng nằm sát ngay cạnh nhau nên AI rất dễ bị nhầm ranh giới nếu tự đoán vị trí thùng. Để giải quyết thật đơn giản và chắc chắn, người dùng chỉ cần khoanh sẵn vùng của ngăn *Rác tái chế* và ngăn *Rác không tái chế* một lần duy nhất trên màn hình camera.

Khi một bạn học sinh mang rác tới gần thùng, phần mềm sẽ tự động nhận diện xem món rác trên tay thuộc nhóm *Rác tái chế* (như chai nhựa, hộp bìa, lon nước) hay *Rác không tái chế* (như khăn giấy, túi nilon, vỏ gói bánh). Sau đó, phần mềm quan sát xem món rác đó đi vào ngăn nào để đưa ra kết luận ngay lập tức: *Bỏ đúng ngăn* (hiện thanh thông báo màu xanh lá) hoặc *Bỏ sai ngăn* (hiện thanh cảnh báo màu cam).

#pagebreak()
= PHẦN 3: CÁC KỸ THUẬT CỐT LÕI VÀ CÁCH THUẬT TOÁN THỰC THI

Để phần mềm chạy mượt và chính xác trên những video quay ngoài sân trường mà không cần đến máy chủ đắt tiền, chúng em thiết kế một quy trình xử lý gọn nhẹ gồm nhiều bước phối hợp chặt chẽ với nhau. Dưới đây là sơ đồ luồng thực thi và cách từng thuật toán hoạt động bên trong chương trình.

== 3.1. Luồng xử lý tổng thể của chương trình
Mỗi khung hình đọc từ video gốc độ phân giải cao (4K) sẽ đi tuần tự qua 5 bước xử lý chính:

#v(0.15cm)
#align(center)[
  #grid(
    columns: (1fr, auto, 1fr, auto, 1fr),
    align: horizon + center,
    gutter: 4pt,
    rect(width: 100%, fill: rgb("#e3f2fd"), stroke: 0.8pt + rgb("#1565c0"), radius: 4pt, inset: 6pt)[
      #text(size: 10pt, weight: "bold")[1. Quét toàn cảnh]\
      #text(size: 9pt)[YOLO11n tìm Người & Thùng rác (lọc ≥ 85%, tối đa 2 người)]
    ],
    text(size: 13pt, weight: "bold", fill: rgb("#1565c0"))[→],
    rect(width: 100%, fill: rgb("#e8f5e9"), stroke: 0.8pt + rgb("#2e7d32"), radius: 4pt, inset: 6pt)[
      #text(size: 10pt, weight: "bold")[2. Kính lúp 4K]\
      #text(size: 9pt)[Cắt vùng ảnh gốc quanh Người & Vật thể rác đang bay]
    ],
    text(size: 13pt, weight: "bold", fill: rgb("#1565c0"))[→],
    rect(width: 100%, fill: rgb("#fff3e0"), stroke: 0.8pt + rgb("#ef6c00"), radius: 4pt, inset: 6pt)[
      #text(size: 10pt, weight: "bold")[3. Nhận diện rác]\
      #text(size: 9pt)[YOLO-World nhận diện & phân loại Tái chế / Không tái chế]
    ],
  )
  #v(0.1cm)
  #text(size: 13pt, weight: "bold", fill: rgb("#1565c0"))[↓]
  #v(0.1cm)
  #grid(
    columns: (1fr, auto, 1fr),
    align: horizon + center,
    gutter: 8pt,
    rect(width: 100%, fill: rgb("#f3e5f5"), stroke: 0.8pt + rgb("#6a1b9a"), radius: 4pt, inset: 6pt)[
      #text(size: 10pt, weight: "bold")[4. Theo dấu & Phân tích hành vi]\
      #text(size: 9pt)[ByteTrack giữ mã vật thể; lọc rác cũ; phân tích chuỗi trạng thái & bỏ phiếu nhiều khung hình]
    ],
    text(size: 13pt, weight: "bold", fill: rgb("#1565c0"))[→],
    rect(width: 100%, fill: rgb("#ffebee"), stroke: 0.8pt + rgb("#c62828"), radius: 4pt, inset: 6pt)[
      #text(size: 10pt, weight: "bold")[5. Kết luận & Bảo mật]\
      #text(size: 9pt)[Chốt cảnh báo đúng/sai ngăn hoặc xả rác; tự động làm mờ khuôn mặt trên ảnh bằng chứng]
    ],
  )
]
#align(center)[#text(size: 9.5pt, style: "italic")[Hình 1: Sơ đồ luồng thực thi từ khung hình video gốc đến kết luận của hệ thống AI]]

== 3.2. Thuật toán "Kính lúp 4K" hai vùng bám và lọc người chính
Khi quay ngoài sân trường rộng, một chai nhựa hay mảnh giấy trên tay học sinh chỉ chiếm một vùng rất nhỏ. Nếu thu nhỏ cả bức ảnh 4K về kích thước chuẩn của AI rồi mới tìm rác, vật thể sẽ bị mờ nhòe và máy không thể nhận ra. Chương trình giải quyết vấn đề này bằng quy trình 2 bước:
- *Bước 1 — Quét toàn cảnh và lọc người chính:* Ở mỗi khung hình, chương trình chạy mô hình gọn nhẹ *YOLO11n* trên ảnh thu nhỏ để tìm nhanh vị trí người và thùng rác. Để tránh bị nhiễu bởi những người ngồi xa ở khu vực căng-tin, thuật toán chỉ giữ lại tối đa *2 người* có độ tin cậy từ *85%* trở lên và đứng rõ nhất trong khung hình.
- *Bước 2 — Cắt phóng to 2 vùng bám trên ảnh gốc 4K:* Thay vì chỉ nhìn quanh thân người, chương trình cắt trực tiếp từ ảnh gốc độ phân giải cao hai loại vùng ảnh sắc nét: (1) *Vùng bám theo người* (mở rộng thêm viền quanh tay và thân) để nhìn rõ rác đang cầm; (2) *Vùng bám theo quán tính của rác* để khi bạn học sinh ném vật thể bay tách ra khỏi người, AI vẫn giữ được khung hình phóng to bám theo vật thể cho tới khi rơi xuống đất. Các vùng cắt này được đưa vào mô hình *YOLO-World* để nhận diện rác, sau đó chương trình cộng lại tọa độ gốc để vẽ khung chính xác lên toàn cảnh.

== 3.3. Thuật toán theo dấu (ByteTrack) và suy luận hành vi theo thời gian
Sau khi nhận diện được từng khung hình, chương trình sử dụng thuật toán *ByteTrack* để nối các khung bao qua thời gian, giúp máy hiểu rằng "bạn học sinh" và "chai nhựa" ở giây thứ 2 và giây thứ 3 là cùng một đối tượng. Từ dữ liệu theo dấu liên tục này, thuật toán xử lý riêng cho từng nhiệm vụ:
- *Với Nhiệm vụ 1 (Phát hiện hành vi xả rác):*
  - *Lọc rác nằm sẵn từ trước:* Những vật thể rác xuất hiện đứng yên ngay từ những giây đầu video mà không đi cùng người sẽ được đưa vào danh sách "rác nền" và bỏ qua hoàn toàn để không báo oan.
  - *Đo khoảng cách chuẩn hóa và chuỗi trạng thái:* Ở mỗi khung hình, chương trình tính khoảng cách giữa tâm vật thể rác và người rồi chia cho chiều cao của người đó (giúp ngưỡng khoảng cách luôn công bằng dù bạn đứng gần hay xa camera). Một hành vi chỉ được ghi nhận khi vật thể đi qua đủ chuỗi chuyển trạng thái: *Gần tay người → Tách rời khỏi người → Nằm yên bên ngoài thùng rác* trong đủ số khung hình liên tiếp. Nếu khoảnh khắc buông tay bị che khuất, chương trình tự động dò ngược bộ nhớ đệm vài giây trước đó để tìm người vừa đi ngang qua gần nhất và gắn mức *Cần thầy cô kiểm tra thêm*.
- *Với Nhiệm vụ 2 (Phân loại rác tái chế / không tái chế):*
  - *Bỏ phiếu nhiều khung hình theo thời gian:* Khi cầm trên tay, rác bị xoay nhiều góc khác nhau khiến AI có thể đoán nhầm ở một vài khoảnh khắc lẻ. Chương trình lưu lại lịch sử nhận diện của từng mã vật thể và cộng dồn điểm tin cậy qua nhiều khung hình liên tiếp; chỉ khi một nhóm (*Tái chế* hoặc *Không tái chế*) chiếm ưu thế rõ rệt thì hệ thống mới chốt loại rác cuối cùng.
  - *Nhận diện rác biến mất tại miệng thùng kín:* Do thùng rác trường học là thùng kín có lỗ nhỏ, khi một món rác đã chốt loại di chuyển vào bên trong vùng khoanh của ngăn thùng rồi *biến mất* khỏi khung hình quá ngưỡng thời gian quy định (và không xuất hiện lại bên ngoài), chương trình xác định rác đã được bỏ vào ngăn đó, sau đó đối chiếu loại rác với loại ngăn để bật ngay thanh *Bỏ đúng ngăn* hoặc *Bỏ sai ngăn*.

== 3.4. Tính năng tự động làm mờ khuôn mặt (dành riêng cho phiên bản Demo dự thi)
Trong phạm vi *phiên bản thử nghiệm dự thi*, trước khi xuất video hoặc lưu ảnh minh chứng đưa vào báo cáo và poster, chương trình tự động xác định vùng đầu của từng bạn học sinh và áp dụng bộ lọc làm mờ *Gaussian* cường độ cao để tuân thủ quy chế ẩn danh và bảo vệ quyền riêng tư. Khi triển khai ứng dụng thực tế nội bộ trong trường học (kết nối camera nhà trường và ứng dụng quản lý như eNetViet), hệ thống cần tính định danh để giáo viên nhắc nhở đúng học sinh nên *tính năng làm mờ khuôn mặt này sẽ được tắt hoặc loại bỏ*.

#pagebreak()
== 3.5. Các công nghệ, mô hình và thuật ngữ được sử dụng
Để thầy cô và các bạn dễ theo dõi các tên gọi kỹ thuật trong báo cáo, bảng dưới đây giải thích ngắn gọn từng công nghệ, tác dụng và cách nhóm áp dụng trực tiếp vào dự án:

#table(
  columns: (23%, 39%, 38%),
  inset: 6pt,
  align: (left, left, left),
  fill: (_, row) => if row == 0 { rgb("#bbdefb") } else if calc.odd(row) { rgb("#f5f9ff") } else { white },
  stroke: 0.5pt + luma(160),
  [*Công nghệ / Thuật ngữ*], [*Giải thích dễ hiểu & Tác dụng*], [*Cách sử dụng trong dự án*],
  [*Thị giác máy tính* (Computer Vision)], [Lĩnh vực của Trí tuệ nhân tạo giúp máy tính "nhìn" và hiểu được hình ảnh, video tương tự như mắt người.], [Nền tảng để phân tích video quay từ camera sân trường, nhận biết người, rác và hành vi bỏ rác.],
  [*YOLO11n*], [Mô hình nhận diện vật thể thế hệ mới, phiên bản cỡ nhỏ (*nano*) có tốc độ xử lý rất nhanh trên máy tính phổ thông.], [Dùng ở bước quét toàn cảnh để tìm nhanh vị trí bạn học sinh (lọc độ tin cậy ≥ 85%, tối đa 2 người) và thùng rác.],
  [*YOLO-World*], [Mô hình nhận diện đối tượng theo từ khóa mở — có thể nhận diện các loại rác cụ thể bằng mô tả từ khóa mà không cần huấn luyện lại từ đầu.], [Chạy trên vùng ảnh phóng to 4K để nhận diện chính xác chai nhựa, lon nước, hộp bìa, bao nilon, vỏ gói bánh và phân nhóm Tái chế / Không tái chế.],
  [*ByteTrack*], [Thuật toán theo dấu nhiều đối tượng liên tục qua các khung hình, giữ nguyên mã nhận diện ngay cả khi vật thể di chuyển nhanh.], [Giúp chương trình biết cùng một bạn học sinh và cùng một món rác xuyên suốt video, từ đó theo dõi chuỗi hành vi từ lúc cầm đến lúc buông.],
  [*OpenCV & Làm mờ Gaussian*], [Thư viện xử lý ảnh mã nguồn mở phổ biến nhất hiện nay; bộ lọc Gaussian giúp làm nhòe mịn một vùng ảnh.], [Đọc video, cắt vùng ảnh gốc 4K, vẽ khung thông báo trực quan và phủ lớp làm mờ kín khuôn mặt học sinh.],
  [*Python*], [Ngôn ngữ lập trình phổ biến, cú pháp rõ ràng, dễ học đối với học sinh THCS và có hệ sinh thái AI phong phú.], [Viết toàn bộ mã nguồn kết nối các mô hình AI, xử lý logic hành vi xả rác và phân loại rác.]
)
#align(left)[#text(size: 9.5pt, style: "italic")[Bảng 1: Tổng hợp các công nghệ, mô hình và thuật ngữ cốt lõi sử dụng trong dự án]]

#pagebreak()
= PHẦN 4: KẾT QUẢ THỰC NGHIỆM VÀ CÁC TÌNH HUỐNG MINH CHỨNG

Để kiểm chứng khả năng hoạt động ngoài thực tế, nhóm chúng em đã trực tiếp quay các tình huống giả lập tại sân trường và khu vực đặt thùng rác đôi với nhiều loại rác quen thuộc (chai nhựa, hộp bìa carton, khăn giấy, vỏ gói bánh) ở các góc quay khác nhau. Dưới đây là diễn biến chi tiết từng tình huống thực nghiệm được hệ thống ghi nhận lại.

== 4.1. Tình huống 1 (Nhiệm vụ 1): Phát hiện hành vi xả rác ngoài sân trường
Trong tình huống này, một bạn học sinh cầm theo hai món rác (hộp bìa carton và chai nhựa) đi bộ từ phía sân trường tiến lại gần chiếc thùng rác màu cam đặt cạnh hàng rào sân bóng. Phía xa bên trái khung hình có khu vực căng-tin với người ngồi nghỉ.

Nhờ kỹ thuật *"Kính lúp 4K"* và bộ lọc người chính, phần mềm chỉ tập trung theo dõi đúng bạn học sinh đang tiến lại gần thùng rác mà không bị phân tâm bởi người ngồi ở xa. Tại đây diễn ra liên tiếp *hai hành vi ném vật thể*: bạn học sinh lần lượt ném cả hộp bìa carton và chai nhựa ra phía ngoài gần hàng rào lưới. Hệ thống đã bám sát trọn vẹn cả hai diễn biến — từ lúc cầm trên tay, lúc tách khỏi tay cho đến khi vật thể nằm lại bên ngoài thùng rác — đồng thời tự động làm mờ gọn khuôn mặt bạn học sinh.

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 6pt,
  [
    #image("../outputs/report_selected/IMG_6830_task1_0067.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 1: Bạn học sinh cầm hai món rác tiến lại gần thùng rác màu cam ngoài sân trường.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6830_task1_0121.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 2: Bạn học sinh đứng sát thùng rác, tay cầm rõ chai nhựa chuẩn bị ném.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6830_task1_0163.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 3: Bạn học sinh thực hiện hành vi ném hộp bìa carton ở phía trên miệng thùng.]]
  ]
)

#v(0.15cm)

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  [
    #image("../outputs/report_selected/IMG_6830_task1_0178.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 4: Cả hộp bìa carton và chai nhựa đều rơi ra ngoài gần hàng rào lưới; hệ thống vẽ đường nối từ bạn học sinh tới chai nhựa và ghi nhận rác tách khỏi người.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6830_task1_0187.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 5: Hai vật thể nằm lại bên ngoài thùng rác; hệ thống chốt trạng thái và lưu ảnh bằng chứng đã làm mờ khuôn mặt.]]
  ]
)

== 4.2. Tình huống 2 (Nhiệm vụ 2): Bỏ rác không tái chế vào đúng ngăn
Ở tình huống thứ hai, chúng em thử nghiệm tại cụm thùng rác đôi đặt ở hành lang: ngăn bên trái màu xanh lá dành cho *Rác tái chế*, ngăn bên phải màu vàng dành cho *Rác không tái chế*.

Bạn học sinh cầm một chiếc bao nilon trắng bước tới trước thùng. Ngay khi bao nilon xuất hiện trong khung hình, phần mềm đã khoanh khung màu cam và nhận diện chính xác đây là *Rác không tái chế*. Tiếp đó, bạn học sinh đưa bao nilon trắng vào lỗ tròn của ngăn màu vàng bên phải. Khi bao nilon đi khuất vào bên trong thùng, hệ thống lập tức hiển thị thanh thông báo màu xanh lá ở cạnh dưới màn hình xác nhận *Bỏ đúng ngăn*.

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  [
    #image("../outputs/report_selected/IMG_6821_task2_0194.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 1: Bạn học sinh cầm bao nilon trắng tới trước thùng đôi; hệ thống nhận diện đúng là Rác không tái chế (khung màu cam).]]
  ],
  [
    #image("../outputs/report_selected/IMG_6821_task2_0260.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 2: Bao nilon trắng được bỏ vào đúng ngăn Rác không tái chế bên phải — thanh thông báo màu xanh lá xác nhận Bỏ đúng ngăn.]]
  ]
)

== 4.3. Tình huống 3 (Nhiệm vụ 2): Phân biệt hành vi bỏ sai ngăn và bỏ đúng ngăn ở góc nhìn chính diện
Ở tình huống này, chúng em ghi nhận hai lượt thử nghiệm khác nhau trước cùng một cụm thùng rác đôi để kiểm chứng độ nhạy của hệ thống:
- *Lượt 1 (dòng ảnh trên — Bước 1, 2, 3):* Một bạn học sinh mang hộp bìa carton và chai nhựa (đều thuộc nhóm *Rác tái chế*, khung màu xanh lá) tới gần thùng. Khi bạn bỏ nhầm *chai nhựa* vào ngăn *Rác không tái chế* bên phải (trong khi hộp bìa carton vẫn đang cầm ở ngoài, chưa bỏ vào thùng), hệ thống lập tức phát hiện sự nhầm lẫn của chai nhựa và bật thanh cảnh báo màu cam *Bỏ sai ngăn*.
- *Lượt 2 (dòng ảnh dưới — Bước 4, 5):* Ở một lượt thử nghiệm khác, bạn học sinh cầm một chai nhựa và đưa vào đúng ngăn *Rác tái chế* màu xanh lá bên trái; ngay khi chai nhựa đi vào bên trong thùng, thanh thông báo màu xanh lá lập tức hiện lên xác nhận *Bỏ đúng ngăn*.

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 6pt,
  [
    #image("../outputs/report_selected/IMG_6822_task2_0035.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 1: Lượt 1 — Hộp bìa carton tiến lại gần; AI nhận diện đúng là Rác tái chế.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6822_task2_0078.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 2: Chai nhựa và hộp bìa (Rác tái chế) được đưa về phía ngăn Không tái chế.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6822_task2_0120.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 3: Chai nhựa vừa bỏ nhầm vào ngăn Không tái chế (hộp bìa vẫn ở ngoài) — hệ thống bật thanh cam báo Sai ngăn.]]
  ]
)

#v(0.15cm)

#grid(
  columns: (1fr, 1fr),
  gutter: 10pt,
  [
    #image("../outputs/report_selected/IMG_6822_task2_0375.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 4: Lượt 2 — Một chai nhựa khác được đưa về phía ngăn Rác tái chế màu xanh lá bên trái.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6822_task2_0386.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 5: Khi chai nhựa đi vào bên trong ngăn Rác tái chế, thanh màu xanh lá hiện lên xác nhận Bỏ đúng ngăn.]]
  ]
)

== 4.4. Tình huống 4 (Nhiệm vụ 2): Thử nghiệm góc quay từ phía sau thùng rác
Trong thực tế ở trường học, camera thường được gắn phía sau hoặc trên cao nhìn ra sân. Ở góc quay từ sau thùng này, khuôn mặt học sinh hướng thẳng về phía camera nên hệ thống tự động làm mờ hoàn toàn vùng mặt xuyên suốt video. Chúng em cũng tách rõ hai lượt thử nghiệm khác nhau thành hai dòng ảnh:
- *Lượt 1 (dòng ảnh trên — Bước 1):* Một bạn học sinh bỏ nhầm vỏ gói bánh (*Rác không tái chế*) vào ngăn *Rác tái chế*, hệ thống lập tức bật thanh màu cam nhắc *Bỏ sai ngăn*.
- *Lượt 2 (dòng ảnh dưới — Bước 2, 3, 4):* Một bạn học sinh khác cầm hộp bìa carton ở tay phải đưa về phía ngăn *Rác không tái chế* (báo *Sai ngăn*), sau đó chuyển sang phía ngăn *Rác tái chế* và thả vào đúng ngăn — thanh thông báo màu xanh lá lập tức xác nhận *Bỏ đúng ngăn*.

#align(center)[
  #box(width: 58%)[
    #image("../outputs/report_selected/IMG_6823_task2_0210.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 1 (Lượt 1): Góc quay từ sau thùng, khuôn mặt học sinh được tự động làm mờ; hệ thống báo Sai ngăn khi vỏ gói bánh bỏ nhầm vào ngăn Tái chế.]]
  ]
]

#v(0.15cm)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 6pt,
  [
    #image("../outputs/report_selected/IMG_6823_task2_0682.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 2 (Lượt 2): Học sinh cầm hộp bìa đưa về phía ngăn Không tái chế — báo Sai ngăn.]]
  ],
  [
    #image("../outputs/report_selected/IMG_6823_task2_0712.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 3: Chuyển hộp bìa sang phía ngăn Rác tái chế; AI nhận diện rõ hộp bìa (khung xanh lá).]]
  ],
  [
    #image("../outputs/report_selected/IMG_6823_task2_0736.jpg", width: 100%)
    #align(center)[#text(size: 8.5pt, style: "italic")[Bước 4: Thả hộp bìa vào đúng ngăn Rác tái chế — thanh xanh lá xác nhận Bỏ đúng ngăn.]]
  ]
)

== 4.5. Tổng hợp kết quả thực nghiệm phân loại rác
Bảng dưới đây tóm tắt kết quả hệ thống ghi nhận trên các tình huống thực nghiệm phân loại rác tại cụm thùng rác đôi của trường học:

#table(
  columns: (22%, 14%, 14%, 50%),
  inset: 6pt,
  align: (left, center, center, left),
  fill: (_, row) => if row == 0 { rgb("#c8e6c9") } else if calc.odd(row) { rgb("#f9fbe7") } else { white },
  stroke: 0.5pt + luma(160),
  [*Tình huống*], [*Đúng ngăn*], [*Sai ngăn*], [*Diễn biến hệ thống ghi nhận được*],
  [Thử nghiệm 1], [3], [0], [Lon nước, hộp bìa, chai nhựa bỏ vào đúng ngăn Tái chế],
  [Thử nghiệm 2], [2], [0], [Bao nilon trắng bỏ vào đúng ngăn Không tái chế],
  [Thử nghiệm 3], [1], [3], [Chai nhựa bỏ nhầm ngăn Không tái chế; 1 lượt bỏ đúng ngăn Tái chế],
  [Thử nghiệm 4], [3], [3], [Góc quay từ sau thùng: vỏ gói bánh bỏ nhầm ngăn Tái chế; chai nhựa và hộp bìa được phân loại đúng theo từng lượt]
)
#align(left)[#text(size: 10pt, style: "italic")[Bảng 2: Tổng hợp kết quả thực nghiệm phân loại rác trên 4 tình huống quay tại trường học]]

#pagebreak()
= PHẦN 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN TƯƠNG LAI

== 5.1. Kết luận
Qua quá trình nghiên cứu và thử nghiệm thực tế, nhóm chúng em đã hoàn thiện thành công *phiên bản thử nghiệm lõi*, chứng minh rằng học sinh THCS hoàn toàn có thể ứng dụng Trí tuệ nhân tạo để giải quyết đồng thời hai vấn đề thiết thực trong trường học: *phát hiện hành vi xả rác* và *hỗ trợ phân loại rác tái chế / không tái chế*.

Nhờ áp dụng 4 kỹ thuật cốt lõi gọn nhẹ ("Kính lúp 4K", lọc người chính, bỏ phiếu nhiều khung hình và tự động làm mờ khuôn mặt), phần mềm nhận diện rõ những mẩu rác nhỏ ngoài sân trường, đánh giá đúng các tình huống bỏ rác đúng hoặc sai ngăn ở nhiều góc quay khác nhau mà vẫn giữ gìn trọn vẹn quyền riêng tư của bạn bè.

== 5.2. Hướng phát triển tương lai
Hướng đi mà dự án nhắm tới là *đưa hệ thống AI này vào ứng dụng thực tế trong môi trường giáo dục*:
1. *Hợp tác từ phía nhà trường:* Xin sự đồng thuận và hỗ trợ từ Ban Giám hiệu để kết nối an toàn với hệ thống camera sẵn có tại hành lang, sân trường và khu vực đặt thùng rác phân loại.
2. *Hợp tác với các ứng dụng quản lý học sinh (như eNetViet):* Kết nối gửi thông báo nhắc nhở tự động, kín đáo đến giáo viên và học sinh khi có hành vi xả rác hoặc bỏ nhầm ngăn phân loại, góp phần xây dựng ngôi trường xanh - sạch - đẹp một cách tự giác.

#pagebreak()
= TÀI LIỆU THAM KHẢO

#set text(size: 11.5pt)
#set par(leading: 0.65em, spacing: 4pt)
1. Quốc hội nước Cộng hòa xã hội chủ nghĩa Việt Nam (2020), *Luật Bảo vệ môi trường số 72/2020/QH14* (Điều 75 về phân loại chất thải rắn sinh hoạt tại nguồn), Hà Nội.
2. Bộ Giáo dục và Đào tạo (2026), *Thông tư số 84/2026/TT-BGDĐT ban hành Quy chế Cuộc thi nghiên cứu khoa học, kỹ thuật cấp quốc gia dành cho học sinh trung học cơ sở và trung học phổ thông*, Hà Nội.
3. Sở Giáo dục và Đào tạo thành phố Đà Nẵng (2026), *Công văn số 6068/SGDĐT-GDTrH&HSSV về việc hướng dẫn tổ chức và nộp hồ sơ Cuộc thi nghiên cứu khoa học, kỹ thuật cấp thành phố năm học 2026 - 2027*, Đà Nẵng.
4. Cheng, T., Song, L., Ge, Y., Liu, W., Wang, X., & Shan, Y. (2024), *YOLO-World: Real-Time Open-Vocabulary Object Detection* (Mô hình nhận diện đối tượng từ vựng mở theo thời gian thực), Kỷ yếu Hội nghị IEEE/CVF CVPR 2024, tr. 16901–16911.
5. Zhang, Y., Sun, P., Jiang, Y., Yu, D., Weng, F., Yuan, Z., Luo, P., Liu, W., & Wang, X. (2022), *ByteTrack: Multi-Object Tracking by Associating Every Detection Box* (Theo dõi đa đối tượng bằng liên kết mọi khung phát hiện), Kỷ yếu Hội nghị Châu Âu về Thị giác máy tính (ECCV 2022), Nhà xuất bản Springer, tr. 1–21.
6. Jocher, G., & Qiu, J. (2024), *Ultralytics YOLO11: Real-Time Object Detection and Computer Vision Models*, Tài liệu kỹ thuật mã nguồn mở Ultralytics.
7. Bradski, G. (2000), *The OpenCV Library* (Thư viện xử lý ảnh và thị giác máy tính mã nguồn mở OpenCV), Tạp chí Dr. Dobb's Journal of Software Tools.

#v(0.3cm)
#align(center)[#text(size: 10.5pt, style: "italic")[(Hết báo cáo kết quả dự án - Nhóm tác giả học sinh THCS tự thực hiện)]]
