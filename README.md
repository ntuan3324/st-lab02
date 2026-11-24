# STLab02 – EduCommerce: Automated Test Case Execution & Reporting

Repository lưu trữ mã nguồn ứng dụng mô phỏng **EduCommerce**, bộ dữ liệu kiểm thử (Data-driven Test Cases), công cụ thực thi kiểm thử tự động (Python Test Runner) và báo cáo kết quả cho bài thực hành **STLab02 – Software Testing**.

---

## 📋 Mục lục
- [Tổng quan dự án](#-tổng-quan-dự-án)
- [Phạm vi kiểm thử (Requirements)](#-phạm-vi-kiểm-thử-requirements)
- [Cấu trúc Repository](#-cấu-trúc-repository)
- [Yêu cầu môi trường](#-yêu-cầu-môi-trường)
- [Hướng dẫn chạy từ môi trường sạch](#-hướng-dẫn-chạy-từ-môi-trường-sạch)
- [Xem Báo cáo & Dashboard](#-xem-báo-cáo--dashboard)
- [Cấu trúc dữ liệu Test Cases](#-cấu-trúc-dữ-liệu-test-cases)

---

## 🎯 Tổng quan dự án
Dự án thực hiện quy trình kiểm thử phần mềm tự động theo luồng:
`Requirement` $\rightarrow$ `Test Condition` $\rightarrow$ `Test Scenario` $\rightarrow$ `Detailed Test Case` $\rightarrow$ `Automated Execution` $\rightarrow$ `Test Reporting`.

* **Ứng dụng kiểm thử (`ecommerce_app.py`):** Mô phỏng luồng mua hàng in-memory gồm các module: `Catalog`, `Cart`, `Promotions`, `Shipping`, `Inventory`, `Payments`, và `Checkout`.
* **Nguyên tắc kiểm thử:** 
  * Sử dụng `fixture()` khởi tạo trạng thái độc lập cho từng test case (Test Isolation).
  * `Expected Result` được xác định độc lập dựa trên Acceptance Criteria, không sửa đổi theo kết quả thực tế của ứng dụng.
  * Kiểm tra đồng thời cả giá trị trả về (return value), ngoại lệ (`ValueError`), và trạng thái hệ thống sau thao tác (tồn kho, đơn hàng, trạng thái voucher).

---

## 📌 Phạm vi kiểm thử (Requirements)

Bài làm lựa chọn **05 requirement** mới (không bao gồm `REQ-06`, `REQ-08`, `REQ-11` đã dùng làm ví dụ mẫu trong Instruction) trải trên nhiều module nghiệp vụ:

| REQ ID | Module | Acceptance Criterion |
| :--- | :--- | :--- |
| **REQ-01** | Catalog | Chỉ sản phẩm `active` mới có thể truy vấn để mua. |
| **REQ-02** | Cart | Số lượng thêm vào giỏ là số nguyên dương; cộng dồn cùng SKU. |
| **REQ-03** | Pricing | Subtotal = Σ price × quantity, tính bằng `Decimal`. |
| **REQ-05** | Promotion | `SAVE10` chỉ áp dụng cho tài khoản đã đăng nhập và chưa dùng mã. |
| **REQ-07** | Promotion | Mã không hợp lệ hoặc đã dùng bị từ chối; chỉ đánh dấu `used` sau khi order thành công. |
---

## 📁 Cấu trúc Repository

```text
├── ecommerce_app.py             # Mã nguồn ứng dụng EduCommerce và hàm fixture()
├── test_runner.py               # Script đọc dữ liệu CSV/Excel, điều phối và chạy test tự động
├── test_cases.csv               # Dữ liệu các ca kiểm thử (hoặc file .xlsx)
├── STLab02_EduCommerce.ipynb    # Google Colab Notebook thực thi toàn bộ quy trình
├── reports/                     # Thư mục chứa kết quả xuất ra sau khi chạy test
│   ├── test_execution.csv       # Chi tiết kết quả thực thi từng test case (Actual, Status, Evidence)
│   ├── test_report.xlsx         # Báo cáo Excel (gồm các sheet: Execution, Traceability, Summary)
│   └── test_dashboard.html      # Báo cáo dạng bảng HTML tĩnh
└── README.md                    # Tài liệu hướng dẫn sử dụng repository
```

---

## ⚙️ Yêu cầu môi trường
* **Python:** Python 3.12.2 (Khuyến nghị chạy trên **Google Colab**).
* **Thư viện Python cần thiết:**
  * `pandas` (đọc/xử lý file CSV, Excel và tổng hợp dữ liệu)
  * `openpyxl` (xuất báo cáo định dạng `.xlsx`)
  * `matplotlib` (vẽ biểu đồ thống kê kết quả)
  * `gradio` (khởi chạy giao diện Dashboard tương tác)

---

## 🚀 Hướng dẫn chạy từ môi trường sạch

### Cách 1: Chạy trên Local (Terminal / Command Prompt)

**Bước 1: Clone repository về máy**
```bash
git clone <URL_GITHUB_CUA_BAN>
cd <TEN_THU_MUC_REPO>
```

**Bước 2: Cài đặt các thư viện phụ thuộc**
```bash
pip install pandas openpyxl matplotlib gradio
```

**Bước 3: Chạy bộ kiểm thử tự động**
```bash
python test_runner.py
```
Sau khi chạy xong, toàn bộ kết quả sẽ được xuất vào thư mục `reports/` và tóm tắt PASS/FAIL sẽ hiển thị trực tiếp trên màn hình console.

---

### Cách 2: Chạy trên Google Colab

1. Tải file `STLab02_EduCommerce.ipynb` lên [Google Colab](https://colab.research.google.com/) (hoặc clone repo trực tiếp trong một cell của Colab bằng lệnh `!git clone <URL_GITHUB_CUA_BAN>`).
2. Cài đặt thư viện trong cell đầu tiên:
   ```python
   !pip -q install pandas openpyxl matplotlib gradio
   ```
3. Chạy lệnh thực thi test suite:
   ```python
   !python test_runner.py
   ```
4. *(Tùy chọn)* Khởi chạy Gradio Dashboard trực tiếp trên Colab để xem biểu đồ và lọc kết quả theo từng Requirement.

---

## 📊 Xem Báo cáo & Dashboard
Sau khi chạy `test_runner.py`, bạn có thể kiểm tra kết quả qua 3 định dạng:
1. **Excel Report (`reports/test_report.xlsx`):** Mở bằng Microsoft Excel hoặc Google Sheets để xem chi tiết 3 trang tính: `Execution`, `Traceability`, và `Summary`.
2. **HTML Dashboard (`reports/test_dashboard.html`):** Mở trực tiếp bằng bất kỳ trình duyệt web nào (Chrome, Edge, Safari) để xem tổng quan số lượng PASS/FAIL.
3. **Gradio Interactive Dashboard:** Chạy cell giao diện Gradio trong file `.ipynb` để lọc kết quả theo `Requirement ID` và `Test Status` kèm biểu đồ trực quan.

---

## 🗂️ Cấu trúc dữ liệu Test Cases
File `test_cases.csv` tuân thủ cấu trúc chuẩn phục vụ Data-driven Testing:
* **Thông tin định danh & Traceability:** `test_case_id`, `requirement_id`, `condition_id`, `scenario_id`, `title`, `priority`.
* **Dữ liệu đầu vào & Môi trường:** `precondition`, `fixture_key`, `input_json`.
* **Kỳ vọng (Test Oracle):** `expected_type`, `expected_json`.
* **Kết quả thực thi (Do Runner ghi nhận):** `execution_status` (`PASS`/`FAIL`/`BLOCKED`), `actual_result`, `error_message`, `evidence_reference`.
