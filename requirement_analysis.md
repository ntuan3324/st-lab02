1. PHÂN TÍCH REQUIREMENT & QUY TẮC NGHIỆP VỤ (REQUIREMENT ANALYSIS)

REQ-01 (Catalog):
Actor: Customer / System.
Rule: Chỉ sản phẩm có active = True mới được phép tìm kiếm/thêm vào giỏ hàng. Khi tìm sản phẩm không tồn tại hoặc active = False, hệ thống ném lỗi PRODUCT_UNAVAILABLE.
Input/Output: Input SKU (string) -> Output Product object hoặc Exception PRODUCT_UNAVAILABLE.

REQ-02 (Cart):
Actor: Customer.
Rule: Số lượng (quantity) thêm vào giỏ phải là số nguyên dương > 1 . Nếu số lượng không phải số nguyên hoặc < 1, ném lỗi INVALID_QUANTITY. Thêm cùng SKU nhiều lần thì cộng dồn số lượng. 
Input/Output: Input SKU, quantity -> Output CartLine list cập nhật hoặc Exception INVALID_QUANTITY.

REQ-03 (Pricing):
Actor: System.
Rule: Subtotal = tổng price X quantity tính chính xác bằng kiểu dữ liệu Decimal. Không dùng kiểu float để tránh lỗi rounding.
Input/Output: Input CartLines -> Output Subtotal (Decimal).

REQ-05 (Promotion - SAVE10 Conditions):
Actor: Customer.
Rule: Mã SAVE10 chỉ áp dụng cho tài khoản đã đăng nhập (authenticated = True) và chưa nằm trong danh sách mã đã sử dụng (used_codes) của tài khoản đó. Chưa đăng nhập -> LOGIN_REQUIRED; đã dùng -> VOUCHER_USED.
Input/Output: Input code, customer -> Output discount amount hoặc Exception tương ứng.

REQ-07 (Promotion Lifecycle & Rollback):
Actor: Customer / Checkout Engine.
Rule: Mã không hợp lệ hoặc đã dùng phải bị từ chối. Mã chỉ được thêm vào customer.used_codes SAU KHI đơn hàng tạo thành công. Nếu thanh toán trực tuyến bị declined (thất bại), mã không được đánh dấu là used.
Input/Output: Input Checkout request -> Output Order status và cập nhật/không cập nhật used_codes.


























