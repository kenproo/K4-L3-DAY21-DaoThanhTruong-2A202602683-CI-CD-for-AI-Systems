# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Đào Thanh Trường |
| MSSV | 2A202602683 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/kenproo/K4-L3-DAY21-DaoThanhTruong-2A202602683-CI-CD-for-AI-Systems |
| Ngày nộp | 08/10/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |
| 4 | 150 | 0.15 | 4 | 0.7182 | 0.8760 |

**Bộ siêu tham số đã chọn:** `n_estimators=150`, `learning_rate=0.15`, `max_depth=4`.

**Lý do:** Bộ siêu tham số được chọn đạt điểm f1_score cao nhất trên tập holdout (0.7182), vượt qua ngưỡng kiểm định chất lượng 0.65 của hệ thống. Đáng chú ý, lần chạy 1 có accuracy cao nhất (0.8780) nhưng f1_score lại thấp hơn (0.7109), cho thấy accuracy cao không đồng nghĩa với khả năng nhận diện tốt lớp thiểu số thu nhập cao. Quan sát thực nghiệm cho thấy giữa n_estimators và learning_rate có sự đánh đổi rõ rệt: việc tăng nhẹ learning_rate lên 0.15 kết hợp với 150 cây giúp mô hình hội tụ tốt hơn mà không bị hiện tượng overfitting như khi đặt max_depth quá sâu.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Tập dữ liệu Census Income có phân bố lớp mất cân bằng nghiêm trọng với chỉ khoảng 24.8% số mẫu thuộc lớp thu nhập cao (>50K) và 75.2% thuộc lớp thu nhập thấp. Nếu một mô hình cơ sở luôn đưa ra dự đoán nhãn "thu nhập thấp" cho tất cả trường hợp, nó vẫn đạt độ chính xác accuracy lên tới 75.2% (0.752) mặc dù hoàn toàn vô dụng vì không phát hiện được bất kỳ ai có thu nhập cao. Chỉ số F1 của lớp dương giải quyết triệt để vấn đề này nhờ đo lường trung bình điều hòa giữa Precision và Recall riêng cho nhóm đối tượng mục tiêu (>50K). Khi đánh giá chất lượng mô hình, ta không sử dụng average="weighted" hay average="macro" bởi vì các trọng số này sẽ bị lớp đa số chiếm ưu thế kéo điểm lên cao, làm mất đi tính nghiêm ngặt và ý nghĩa thực tế của Quality Gate.

---

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
| Cấu hình DVC remote với AWS S3 | Cần phân quyền IAM và cài đặt driver hỗ trợ S3 cho DVC | Cấp quyền AmazonS3FullAccess cho IAM user và cài đặt gói dvc-s3 để đồng bộ dữ liệu |
| Service FastAPI trên EC2 không nạp được model | Service systemd thiếu biến môi trường ARTIFACT_BUCKET và quyền truy cập AWS | Khai báo biến môi trường trong file service systemd và cấu hình AWS credentials cho user ubuntu |
| Kết nối SSH tự động từ GitHub Actions sang EC2 | Runner GitHub cần private key hợp lệ để SSH tự động không cần mật khẩu | Tạo cặp khóa SSH riêng biệt income_deploy, lưu private key vào GitHub Secrets và gắn public key vào authorized_keys trên EC2 |

---

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (chỉ `train_batch1`) | 0.7182 | 0.8760 |
| Bước 3 (thêm `train_batch2`) | 0.7297 | 0.8800 |

**Nhận xét:** Khi bổ sung thêm 22.361 mẫu từ train_batch2, cả f1_score và accuracy đều có sự cải thiện nhẹ (f1_score tăng từ 0.7182 lên 0.7297 và accuracy tăng từ 0.8760 lên 0.8800). Mức tăng không quá đột biến do dữ liệu bổ sung có cùng phân phối với tập ban đầu, nhưng điều này chứng minh quy trình Continuous Training tự động hoạt động ổn định và mô hình mới đã xuất sắc vượt qua Quality Gate để triển khai.
