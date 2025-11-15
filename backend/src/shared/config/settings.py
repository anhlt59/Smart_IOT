"""Configuration settings for the application"""
import os
from typing import Optional


class Settings:
    """Application settings from environment variables"""

    # Environment
    ENVIRONMENT: str = os.getenv('ENVIRONMENT', 'dev')
    REGION: str = os.getenv('AWS_REGION', 'us-east-1')

    # DynamoDB Tables
    DEVICES_TABLE: str = os.getenv('DEVICES_TABLE', 'iot-monitoring-devices')
    USERS_TABLE: str = os.getenv('USERS_TABLE', 'iot-monitoring-users')
    ALERTS_TABLE: str = os.getenv('ALERTS_TABLE', 'iot-monitoring-alerts')
    ALERT_RULES_TABLE: str = os.getenv('ALERT_RULES_TABLE', 'iot-monitoring-alert-rules')
    FIRMWARE_TABLE: str = os.getenv('FIRMWARE_TABLE', 'iot-monitoring-firmware')
    DEPLOYMENTS_TABLE: str = os.getenv('DEPLOYMENTS_TABLE', 'iot-monitoring-deployments')
    NOTIFICATIONS_TABLE: str = os.getenv('NOTIFICATIONS_TABLE', 'iot-monitoring-notifications')
    CONNECTIONS_TABLE: str = os.getenv('CONNECTIONS_TABLE', 'iot-monitoring-connections')

    # Timestream
    TIMESTREAM_DATABASE: str = os.getenv('TIMESTREAM_DATABASE', 'iot_monitoring')
    TIMESTREAM_TABLE: str = os.getenv('TIMESTREAM_TABLE', 'sensor_data')

    # S3 Buckets
    FIRMWARE_BUCKET: str = os.getenv('FIRMWARE_BUCKET', 'iot-monitoring-firmware')
    DATA_EXPORT_BUCKET: str = os.getenv('DATA_EXPORT_BUCKET', 'iot-monitoring-exports')

    # SQS Queues
    ALERT_QUEUE_URL: str = os.getenv('ALERT_QUEUE_URL', '')
    NOTIFICATION_QUEUE_URL: str = os.getenv('NOTIFICATION_QUEUE_URL', '')

    # Cognito
    USER_POOL_ID: str = os.getenv('USER_POOL_ID', '')
    USER_POOL_CLIENT_ID: str = os.getenv('USER_POOL_CLIENT_ID', '')

    # API Gateway
    WEBSOCKET_API_ENDPOINT: str = os.getenv('WEBSOCKET_API_ENDPOINT', '')

    # Notification Settings
    SES_SENDER_EMAIL: str = os.getenv('SES_SENDER_EMAIL', 'noreply@example.com')
    FCM_CREDENTIALS_SECRET: str = os.getenv('FCM_CREDENTIALS_SECRET', '')

    # Application Settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    PAGE_SIZE_DEFAULT: int = int(os.getenv('PAGE_SIZE_DEFAULT', '25'))
    PAGE_SIZE_MAX: int = int(os.getenv('PAGE_SIZE_MAX', '100'))

    # IoT Core
    IOT_ENDPOINT: str = os.getenv('IOT_ENDPOINT', '')

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT == 'prod'

    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.ENVIRONMENT == 'dev'


settings = Settings()
