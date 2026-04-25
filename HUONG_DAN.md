# Hướng Dẫn Sử Dụng TikTok Live Restreamer (v1.1)

Công cụ này cho phép bạn bắt luồng livestream từ nhiều tài khoản TikTok và phát lại về kênh của mình (qua RTMP) hoặc hiển thị lên cửa sổ xem trước để quay lại bằng TikTok LIVE Studio.

---

## 1. Yêu Cầu Hệ Thống
*   **Python 3.10+**: Đã cài đặt.
*   **FFmpeg & FFplay**: Đã được cài đặt và thêm vào PATH.
*   **Cookies**: Cần tệp `cookies.txt` (định dạng Netscape) để tránh bị TikTok chặn.

---

## 2. Các Tính Năng Chính

### A. Chế độ Phát Trực Tiếp (RTMP)
Dùng khi bạn có mã **Server URL** và **Stream Key** (thường lấy từ YouTube, Facebook hoặc TikTok Web nếu được cấp quyền OBS).
1. Nhập danh sách URL TikTok.
2. Nhập thông tin RTMP.
3. Nhấn **Start Restreaming**.

### B. Chế độ Preview (Dành cho TikTok LIVE Studio)
Dùng khi bạn không có mã RTMP và muốn dùng LIVE Studio để phát lại.
1. Nhập danh sách URL TikTok (mỗi dòng 1 link).
2. Nhấn **Open Preview (for Live Studio)**.
3. Ứng dụng sẽ mở các cửa sổ video riêng biệt cho từng link (cách nhau 3 giây).
4. Trong LIVE Studio: Chọn **Add Source** -> **Window Capture** -> Chọn cửa sổ **Preview**.

### C. Gắn Link Affiliate / Chèn Chữ
* Nhập nội dung vào ô **Affiliate Link / Overlay Text**.
* Chữ này sẽ tự động hiện lên ở phía dưới video (cả bản RTMP và bản Preview).

---

## 3. Cách Lấy Cookies Để Không Bị Chặn (Quan trọng)
Nếu bạn gặp lỗi "Could not get stream URL" hoặc "Blocked", hãy làm theo các bước sau:
1. Cài extension **"Get cookies.txt LOCALLY"** trên trình duyệt Chrome/Edge.
2. Đăng nhập vào TikTok trên trình duyệt.
3. Bấm vào extension -> Chọn **Export** để lưu tệp `cookies.txt`.
4. Trong ứng dụng: Tại ô **Cookie File**, bấm **Browse** và chọn tệp vừa lưu.

---

## 4. Mẹo Xử Lý Khi Gặp Lỗi

### Lỗi Video bị mờ
* **Nguyên nhân:** Cửa sổ Preview quá nhỏ hoặc mạng yếu.
* **Xử lý:** Kéo to cửa sổ Preview trước khi quay màn hình trong LIVE Studio. Chúng tôi đã mặc định ép chất lượng cao nhất (Best Quality).

### Lỗi Giật lag / Lệch tiếng
* **Nguyên nhân:** Bitrate quá cao hoặc CPU quá tải.
* **Xử lý:** Chúng tôi đã tối ưu bitrate xuống 2500k và dùng preset `superfast` để đảm bảo mượt mà trên cả máy cấu hình trung bình.

### Lỗi Không hiện cửa sổ Preview
* **Xử lý:** Đảm bảo bạn đã chọn đúng tệp Cookies mới nhất. Nếu vẫn không được, hãy kiểm tra phần Log để xem câu lệnh chạy có báo lỗi gì không.

---

## 5. Lưu Ý Khác
* **Tự động lưu:** Ứng dụng sẽ tự lưu lại toàn bộ link và cấu hình vào tệp `config.json` mỗi khi bạn nhấn Start hoặc Preview. Lần sau mở lên sẽ không cần nhập lại.
* **Anti-Spam:** Khi quét danh sách (Auto-Switch), hãy để thời gian nghỉ ít nhất 120 giây để tránh bị TikTok quét IP.
