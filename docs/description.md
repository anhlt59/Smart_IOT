## Mô tả dự án

**Industrial IoT Platform** là nền tảng quản lý và vận hành tập trung dành cho các **khu công nghiệp thông minh**, được thiết kế theo mô hình **Hybrid Architecture**, bao gồm hai thành phần chính:

1. **On-Premise Platform** triển khai tại từng khu công nghiệp.
2. **Cloud Platform** triển khai trên **VNPT Cloud** để quản lý tập trung nhiều khu công nghiệp.

Kiến trúc này giúp đảm bảo các chức năng điều khiển và giám sát tại hiện trường vẫn hoạt động ổn định ngay cả khi mất kết nối Internet, đồng thời cung cấp khả năng quản lý tập trung, mở rộng và phân tích dữ liệu trên nền tảng Cloud.

---

## 1. On-Premise Platform (Industrial Site)

On-Premise Platform được triển khai trực tiếp tại từng khu công nghiệp hoặc nhà máy, kết nối với các hệ thống OT (Operational Technology) hiện hữu như PLC, RTU, SCADA, cảm biến, đồng hồ đo, camera AI và các thiết bị điều khiển.

Nền tảng này chịu trách nhiệm:

* Thu thập dữ liệu từ các thiết bị và hệ thống công nghiệp thông qua các giao thức như Modbus RTU/TCP, OPC-UA, MQTT...
* Xử lý dữ liệu và thực thi các quy tắc điều khiển (Local Rule Engine) với độ trễ thấp.
* Điều khiển thiết bị tại hiện trường theo thời gian thực.
* Lưu trữ dữ liệu cục bộ và hỗ trợ **Store & Forward** để đảm bảo không mất dữ liệu khi mất kết nối Internet.
* Đồng bộ dữ liệu và sự kiện lên Cloud khi kết nối được khôi phục.
* Hỗ trợ Dashboard cục bộ để vận hành khu công nghiệp ngay cả khi Cloud không khả dụng.

Mục tiêu của On-Premise Platform là đảm bảo **tính liên tục của hoạt động sản xuất**, **độ trễ thấp** và **khả năng vận hành độc lập**.

---

## 2. Cloud Platform (VNPT Cloud)

Cloud Platform được triển khai trên **VNPT Cloud**, đóng vai trò là trung tâm quản lý tập trung cho toàn bộ các khu công nghiệp.

Nền tảng sử dụng các dịch vụ Managed của VNPT Cloud như:

* VNPT Kubernetes Service (VKS)
* API Gateway
* Load Balancer
* WAAP
* Managed PostgreSQL
* Managed Redis
* Managed Kafka
* Object Storage
* Backup

Các thành phần chưa có dịch vụ Managed tương ứng sẽ được triển khai trên VKS hoặc VServer.

Cloud Platform cung cấp các chức năng:

* Quản lý tập trung nhiều khu công nghiệp (Multi-site Management).
* Quản lý Gateway, thiết bị và cấu hình từ xa.
* Thu thập và xử lý dữ liệu thời gian thực từ các On-Premise Platform.
* Quản lý cảnh báo, sự kiện và thông báo tập trung.
* Lưu trữ dữ liệu lịch sử và dữ liệu chuỗi thời gian.
* Dashboard và báo cáo tổng hợp toàn hệ thống.
* Quản lý người dùng, phân quyền và xác thực tập trung.
* Giám sát sức khỏe hệ thống và hạ tầng.
* Hỗ trợ phân tích dữ liệu, Digital Twin và các ứng dụng AI trong tương lai.

Cloud Platform được thiết kế theo kiến trúc **Cloud-native Microservices**, có khả năng mở rộng theo chiều ngang (Horizontal Scaling), hỗ trợ High Availability và Multi-tenant, cho phép phục vụ nhiều khu công nghiệp trên cùng một nền tảng.

---

## Mô hình triển khai tổng thể

```text
                VNPT Cloud
        ┌──────────────────────────────┐
        │ Cloud Management Platform    │
        │ - Multi Industrial Parks     │
        │ - Device Management          │
        │ - Monitoring & Dashboard     │
        │ - Alarm & Notification       │
        │ - Historical Data            │
        │ - Digital Twin              │
        └──────────────┬───────────────┘
                       │
                VPN / TLS / MQTT
                       │
 ┌─────────────────────┼─────────────────────┐
 │                     │                     │
 ▼                     ▼                     ▼
Industrial Park A  Industrial Park B  Industrial Park C
(On-Premise)       (On-Premise)       (On-Premise)

- PLC             - PLC             - PLC
- RTU             - RTU             - RTU
- SCADA           - SCADA           - SCADA
- Edge Gateway    - Edge Gateway    - Edge Gateway
- Local Rule      - Local Rule      - Local Rule
- Local Storage   - Local Storage   - Local Storage
```

Kiến trúc này cho phép mỗi khu công nghiệp **vận hành độc lập tại hiện trường**, đồng thời **được quản lý tập trung trên VNPT Cloud**, đáp ứng các yêu cầu về hiệu năng, tính sẵn sàng, khả năng mở rộng và an toàn thông tin trong môi trường Industrial IoT.
