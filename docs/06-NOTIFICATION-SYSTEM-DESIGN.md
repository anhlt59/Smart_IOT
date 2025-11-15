# Notification System Design - IoT Monitoring Application

## 1. Overview

The Notification System is a critical component responsible for delivering timely alerts to users across multiple channels (Email, Push Notifications, SMS) based on alert severity, user preferences, and delivery policies.

### 1.1 Design Goals

1. **Reliability**: Ensure notifications are delivered successfully
2. **Scalability**: Handle thousands of notifications per minute
3. **Flexibility**: Support multiple channels and templates
4. **User Control**: Respect user preferences and quiet hours
5. **Traceability**: Track notification delivery status
6. **Cost Optimization**: Minimize notification costs

### 1.2 Supported Channels

| Channel | Provider | Use Case | Cost |
|---------|----------|----------|------|
| **Email** | Amazon SES | All severity levels, detailed info | $0.10 per 1,000 emails |
| **Push Notification** | Firebase FCM | Time-sensitive alerts | Free |
| **SMS** | Amazon SNS | Critical alerts only | $0.00645 per SMS (US) |
| **Webhook** | Custom HTTP endpoints | Third-party integrations | Free |

## 2. Architecture

### 2.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Alert Generation                             │
│  (Alert Rule Evaluator Lambda)                                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ 1. Alert Created
                            ▼
                 ┌──────────────────────┐
                 │  Amazon SQS          │
                 │  (Alert Queue)       │
                 │                      │
                 │  - Decoupling        │
                 │  - Buffering         │
                 │  - Retry logic       │
                 └──────────┬───────────┘
                            │
                            │ 2. Lambda polls SQS (batch)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│           Notification Dispatcher Lambda                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 1: Fetch Alert & Device Details                     │  │
│  │  - DynamoDB: Alerts Table                                │  │
│  │  - DynamoDB: Devices Table                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 2: Determine Recipients                             │  │
│  │  - Query Users by Organization                           │  │
│  │  - Filter by device subscriptions                        │  │
│  │  - Apply on-call schedules                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 3: For Each User                                    │  │
│  │  - Fetch preferences                                     │  │
│  │  - Check quiet hours                                     │  │
│  │  - Determine channels (based on severity + prefs)        │  │
│  │  - Generate content (using templates)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 4: Send Notifications (Parallel)                    │  │
│  │  - Email via SES                                         │  │
│  │  - Push via FCM                                          │  │
│  │  - SMS via SNS (optional)                                │  │
│  │  - Webhook calls                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Step 5: Log Notification Delivery                        │  │
│  │  - DynamoDB: Notifications Table                         │  │
│  │  - Update Alert with notification status                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ 3. Notifications Sent
                            ▼
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌───────────────┐                    ┌──────────────────┐
│ Amazon SES    │                    │ Firebase FCM     │
│ (Email)       │                    │ (Push)           │
└───────┬───────┘                    └────────┬─────────┘
        │                                     │
        │ 4. Delivery Status                  │
        │                                     │
        ▼                                     ▼
┌─────────────────────────────────────────────────────┐
│  SNS Topic: Notification Delivery Status           │
│  - Email bounces/complaints                        │
│  - Push delivery failures                          │
└──────────────────────┬──────────────────────────────┘
                       │
                       │ 5. Process delivery status
                       ▼
             ┌──────────────────────┐
             │  Lambda:             │
             │  Delivery Status     │
             │  Handler             │
             │                      │
             │  - Update logs       │
             │  - Handle failures   │
             └──────────────────────┘
```

## 3. Notification Routing Logic

### 3.1 Channel Selection Matrix

**Decision Logic:**

```python
def determine_channels(alert_severity: str, user_prefs: dict, current_time: datetime) -> List[str]:
    """
    Determine which notification channels to use based on:
    - Alert severity
    - User preferences
    - Current time (quiet hours)
    """
    channels = []

    # Check if in quiet hours
    in_quiet_hours = is_in_quiet_hours(current_time, user_prefs)

    # Critical alerts override quiet hours
    if alert_severity == 'critical':
        if user_prefs['notifications']['email']:
            channels.append('email')
        if user_prefs['notifications']['push']:
            channels.append('push')
        if user_prefs['notifications']['sms']:
            channels.append('sms')
    elif alert_severity == 'warning':
        if not in_quiet_hours:
            if user_prefs['notifications']['email']:
                channels.append('email')
            if user_prefs['notifications']['push']:
                channels.append('push')
    elif alert_severity == 'info':
        if not in_quiet_hours:
            if user_prefs['notifications']['email']:
                channels.append('email')

    return channels
```

### 3.2 Routing Rules

| Alert Severity | Quiet Hours | Email | Push | SMS |
|----------------|-------------|-------|------|-----|
| **Critical** | Ignore | ✓ | ✓ | ✓ (optional) |
| **Warning** | Respect | ✓ | ✓ | ✗ |
| **Info** | Respect | ✓ | ✗ | ✗ |

**Additional Rules:**
- If user has no device tokens, skip push notifications
- If user has no verified phone number, skip SMS
- If email bounces/complaints exceed threshold, disable email channel
- Respect user's explicit channel opt-outs

## 4. Notification Templates

### 4.1 Template System

**Template Structure:**
```python
class NotificationTemplate:
    def __init__(self, template_id, channel, subject_template, body_template):
        self.template_id = template_id
        self.channel = channel
        self.subject = subject_template
        self.body = body_template

    def render(self, context: dict) -> dict:
        """Render template with context data"""
        return {
            'subject': self.subject.format(**context),
            'body': self.body.format(**context)
        }
```

### 4.2 Email Templates

#### Template: High Temperature Alert

**Subject:**
```
[{severity}] High Temperature Detected - {device_name}
```

**Body (HTML):**
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #f44336; color: white; padding: 20px; }
        .content { padding: 20px; }
        .details { background-color: #f5f5f5; padding: 15px; margin: 15px 0; }
        .button { background-color: #2196F3; color: white; padding: 10px 20px; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h2>⚠️ High Temperature Alert</h2>
    </div>
    <div class="content">
        <p>Hello {user_name},</p>

        <p>A high temperature condition has been detected:</p>

        <div class="details">
            <strong>Device:</strong> {device_name}<br>
            <strong>Location:</strong> {device_location}<br>
            <strong>Current Temperature:</strong> {current_value}°C<br>
            <strong>Threshold:</strong> {threshold}°C<br>
            <strong>Time:</strong> {timestamp}<br>
        </div>

        <p>Please take appropriate action.</p>

        <p>
            <a href="{dashboard_url}/devices/{device_id}" class="button">View Device</a>
            <a href="{dashboard_url}/alerts/{alert_id}/acknowledge" class="button">Acknowledge Alert</a>
        </p>

        <hr>
        <p style="color: #666; font-size: 12px;">
            You received this notification because you are subscribed to alerts for this device.
            <a href="{dashboard_url}/settings/notifications">Manage notification preferences</a>
        </p>
    </div>
</body>
</html>
```

**Body (Plain Text):**
```
HIGH TEMPERATURE ALERT
======================

Hello {user_name},

A high temperature condition has been detected:

Device: {device_name}
Location: {device_location}
Current Temperature: {current_value}°C
Threshold: {threshold}°C
Time: {timestamp}

Please take appropriate action.

View Device: {dashboard_url}/devices/{device_id}
Acknowledge Alert: {dashboard_url}/alerts/{alert_id}/acknowledge

---
You received this notification because you are subscribed to alerts for this device.
Manage notification preferences: {dashboard_url}/settings/notifications
```

#### Template: Device Offline Alert

**Subject:**
```
[{severity}] Device Offline - {device_name}
```

**Body:**
```html
<p>Hello {user_name},</p>

<p>Device <strong>{device_name}</strong> has been offline for {offline_duration}.</p>

<div class="details">
    <strong>Device:</strong> {device_name}<br>
    <strong>Location:</strong> {device_location}<br>
    <strong>Last Seen:</strong> {last_seen}<br>
    <strong>Offline Duration:</strong> {offline_duration}<br>
</div>

<p>Please check the device connectivity.</p>
```

### 4.3 Push Notification Templates

#### Template: High Temperature Alert

**FCM Payload:**
```json
{
  "notification": {
    "title": "High Temperature - {device_name}",
    "body": "Current: {current_value}°C (Threshold: {threshold}°C)",
    "icon": "alert_warning",
    "color": "#f44336",
    "sound": "default",
    "click_action": "FLUTTER_NOTIFICATION_CLICK"
  },
  "data": {
    "alertId": "{alert_id}",
    "deviceId": "{device_id}",
    "severity": "{severity}",
    "type": "alert",
    "route": "/alerts/{alert_id}"
  },
  "android": {
    "priority": "high",
    "notification": {
      "channel_id": "alerts"
    }
  },
  "apns": {
    "headers": {
      "apns-priority": "10"
    },
    "payload": {
      "aps": {
        "badge": 1,
        "sound": "default"
      }
    }
  }
}
```

#### Template: Device Offline Alert

**FCM Payload:**
```json
{
  "notification": {
    "title": "Device Offline - {device_name}",
    "body": "Last seen {last_seen}",
    "icon": "device_offline",
    "color": "#ff9800"
  },
  "data": {
    "alertId": "{alert_id}",
    "deviceId": "{device_id}",
    "severity": "warning",
    "type": "alert"
  }
}
```

### 4.4 SMS Templates

#### Template: Critical Alert

**Message:**
```
IoT Alert: {device_name} - {alert_type}. Value: {current_value}. Check dashboard: {short_url}
```

**Constraints:**
- Maximum 160 characters
- Use URL shortener for dashboard links
- Only for critical alerts

### 4.5 Webhook Templates

#### Payload:
```json
{
  "event": "alert.triggered",
  "timestamp": "2025-11-15T10:00:00Z",
  "alert": {
    "id": "alert-123",
    "severity": "warning",
    "type": "high_temperature",
    "device": {
      "id": "dev-abc123",
      "name": "Office-Temp-Sensor-1",
      "location": "Office 301, Building A"
    },
    "condition": "temperature > 40",
    "currentValue": 42.5,
    "threshold": 40,
    "unit": "°C"
  },
  "links": {
    "dashboard": "https://app.example.com/alerts/alert-123",
    "device": "https://app.example.com/devices/dev-abc123"
  }
}
```

## 5. Notification Delivery Implementation

### 5.1 Email Delivery (Amazon SES)

**Implementation:**
```python
import boto3
from botocore.exceptions import ClientError

class SESNotificationProvider:
    def __init__(self):
        self.ses = boto3.client('ses', region_name='us-east-1')
        self.sender_email = 'noreply@iot-monitoring.example.com'

    def send_email(self, recipient: str, subject: str, body_html: str, body_text: str) -> bool:
        """
        Send email via Amazon SES

        Args:
            recipient: Email address
            subject: Email subject
            body_html: HTML body
            body_text: Plain text body

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            response = self.ses.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': body_html, 'Charset': 'UTF-8'},
                        'Text': {'Data': body_text, 'Charset': 'UTF-8'}
                    }
                },
                ConfigurationSetName='iot-monitoring-config-set'  # For tracking
            )

            message_id = response['MessageId']
            logger.info(f"Email sent successfully: {message_id}")
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']

            if error_code == 'MessageRejected':
                logger.error(f"Email rejected: {e}")
            elif error_code == 'MailFromDomainNotVerifiedException':
                logger.error(f"Domain not verified: {e}")
            else:
                logger.error(f"SES error: {e}")

            return False

    def send_bulk_email(self, recipients: List[str], template_name: str, template_data: dict) -> dict:
        """
        Send bulk emails using SES template

        Returns:
            {
                'success': [...],
                'failed': [...]
            }
        """
        try:
            response = self.ses.send_bulk_templated_email(
                Source=self.sender_email,
                Template=template_name,
                Destinations=[
                    {
                        'Destination': {'ToAddresses': [recipient]},
                        'ReplacementTemplateData': json.dumps(template_data)
                    }
                    for recipient in recipients
                ],
                ConfigurationSetName='iot-monitoring-config-set'
            )

            return {
                'success': [r['MessageId'] for r in response['Status'] if r['Status'] == 'Success'],
                'failed': [r for r in response['Status'] if r['Status'] != 'Success']
            }

        except ClientError as e:
            logger.error(f"Bulk email error: {e}")
            return {'success': [], 'failed': recipients}
```

**SES Configuration Set:**
- Track email opens (optional)
- Track link clicks
- Handle bounces and complaints via SNS

**Bounce/Complaint Handling:**
```python
def handle_ses_notification(event):
    """
    Handle SES bounce/complaint notifications
    """
    message = json.loads(event['Records'][0]['Sns']['Message'])
    notification_type = message['notificationType']

    if notification_type == 'Bounce':
        handle_bounce(message)
    elif notification_type == 'Complaint':
        handle_complaint(message)

def handle_bounce(message):
    """
    Hard bounces: Remove email from list
    Soft bounces: Retry with backoff
    """
    bounce_type = message['bounce']['bounceType']
    recipients = [r['emailAddress'] for r in message['bounce']['bouncedRecipients']]

    if bounce_type == 'Permanent':
        # Disable email notifications for these users
        for email in recipients:
            disable_email_notifications(email)
            logger.warning(f"Disabled email notifications for {email} (hard bounce)")
    else:
        # Log soft bounce, will retry
        logger.info(f"Soft bounce for {recipients}")

def handle_complaint(message):
    """
    Mark email as complained, disable notifications
    """
    recipients = [r['emailAddress'] for r in message['complaint']['complainedRecipients']]

    for email in recipients:
        disable_email_notifications(email)
        logger.warning(f"Disabled email notifications for {email} (complaint)")
```

### 5.2 Push Notification Delivery (Firebase FCM)

**Implementation:**
```python
import firebase_admin
from firebase_admin import credentials, messaging

class FCMNotificationProvider:
    def __init__(self):
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate('/path/to/firebase-credentials.json')
        firebase_admin.initialize_app(cred)

    def send_push(self, device_token: str, notification_data: dict) -> bool:
        """
        Send push notification via FCM

        Args:
            device_token: FCM device token
            notification_data: Notification payload

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification_data['title'],
                    body=notification_data['body'],
                    image=notification_data.get('image')
                ),
                data=notification_data.get('data', {}),
                token=device_token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='alerts',
                        color='#f44336',
                        sound='default'
                    )
                ),
                apns=messaging.APNSConfig(
                    headers={'apns-priority': '10'},
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            badge=1,
                            sound='default'
                        )
                    )
                )
            )

            response = messaging.send(message)
            logger.info(f"Push notification sent: {response}")
            return True

        except messaging.UnregisteredError:
            # Token is invalid, remove from user's device tokens
            logger.warning(f"Invalid device token: {device_token}")
            remove_device_token(device_token)
            return False

        except Exception as e:
            logger.error(f"FCM error: {e}")
            return False

    def send_multicast(self, device_tokens: List[str], notification_data: dict) -> dict:
        """
        Send to multiple devices

        Returns:
            {
                'success_count': int,
                'failure_count': int,
                'failed_tokens': [...]
            }
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=notification_data['title'],
                    body=notification_data['body']
                ),
                data=notification_data.get('data', {}),
                tokens=device_tokens
            )

            batch_response = messaging.send_multicast(message)

            failed_tokens = []
            for idx, response in enumerate(batch_response.responses):
                if not response.success:
                    failed_tokens.append(device_tokens[idx])
                    # Check if token is invalid
                    if isinstance(response.exception, messaging.UnregisteredError):
                        remove_device_token(device_tokens[idx])

            return {
                'success_count': batch_response.success_count,
                'failure_count': batch_response.failure_count,
                'failed_tokens': failed_tokens
            }

        except Exception as e:
            logger.error(f"Multicast error: {e}")
            return {
                'success_count': 0,
                'failure_count': len(device_tokens),
                'failed_tokens': device_tokens
            }

    def send_to_topic(self, topic: str, notification_data: dict) -> bool:
        """
        Send to topic subscribers
        Useful for organization-wide notifications
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notification_data['title'],
                    body=notification_data['body']
                ),
                topic=topic
            )

            response = messaging.send(message)
            logger.info(f"Topic notification sent: {response}")
            return True

        except Exception as e:
            logger.error(f"Topic notification error: {e}")
            return False
```

**Topic Subscription:**
```python
def subscribe_to_topics(device_token: str, user_id: str, organization_id: str):
    """
    Subscribe device to relevant topics
    """
    topics = [
        f'org-{organization_id}',  # Organization-wide notifications
        f'user-{user_id}'          # User-specific notifications
    ]

    for topic in topics:
        messaging.subscribe_to_topic([device_token], topic)
```

### 5.3 SMS Delivery (Amazon SNS)

**Implementation:**
```python
import boto3

class SNSNotificationProvider:
    def __init__(self):
        self.sns = boto3.client('sns')

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Send SMS via Amazon SNS

        Args:
            phone_number: Phone number in E.164 format (+1234567890)
            message: SMS message (max 160 characters)

        Returns:
            True if sent successfully
        """
        try:
            # Set SMS attributes for better deliverability
            self.sns.set_sms_attributes(
                attributes={
                    'DefaultSMSType': 'Transactional',  # Critical alerts
                    'DefaultSenderID': 'IoTAlert'
                }
            )

            response = self.sns.publish(
                PhoneNumber=phone_number,
                Message=message[:160],  # Enforce 160 char limit
                MessageAttributes={
                    'AWS.SNS.SMS.SMSType': {
                        'DataType': 'String',
                        'StringValue': 'Transactional'
                    }
                }
            )

            message_id = response['MessageId']
            logger.info(f"SMS sent: {message_id}")
            return True

        except Exception as e:
            logger.error(f"SNS SMS error: {e}")
            return False
```

**SMS Optimization:**
- Use short URLs (bit.ly API)
- Abbreviate when possible
- Only send for critical alerts
- Respect user's phone number verification status

### 5.4 Webhook Delivery

**Implementation:**
```python
import requests

class WebhookNotificationProvider:
    def __init__(self):
        self.timeout = 10  # seconds

    def send_webhook(self, webhook_url: str, payload: dict) -> bool:
        """
        Send webhook notification

        Args:
            webhook_url: Destination URL
            payload: JSON payload

        Returns:
            True if successful (2xx response)
        """
        try:
            # Add signature for security
            signature = self._generate_signature(payload)

            response = requests.post(
                webhook_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                    'X-IoT-Signature': signature,
                    'User-Agent': 'IoT-Monitoring-Webhook/1.0'
                },
                timeout=self.timeout
            )

            if response.status_code < 300:
                logger.info(f"Webhook delivered: {webhook_url}")
                return True
            else:
                logger.warning(f"Webhook failed: {webhook_url} - {response.status_code}")
                return False

        except requests.Timeout:
            logger.error(f"Webhook timeout: {webhook_url}")
            return False
        except Exception as e:
            logger.error(f"Webhook error: {webhook_url} - {e}")
            return False

    def _generate_signature(self, payload: dict) -> str:
        """
        Generate HMAC signature for webhook security
        """
        import hmac
        import hashlib

        secret = get_secret('webhook-secret')
        message = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature
```

## 6. Notification Logging & Tracking

### 6.1 Notifications Table Schema

**DynamoDB Table:**
```
Table: iot-monitoring-notifications
Partition Key: notificationId (String)
Sort Key: timestamp (Number)
GSIs:
  - alertId-index (PK: alertId, SK: timestamp)
  - userId-status-index (PK: userId, SK: status-timestamp)

Attributes:
{
  notificationId: String (PK)
  alertId: String
  userId: String
  channel: String (email|push|sms|webhook)
  status: String (queued|sent|delivered|failed|bounced)
  recipient: String (email/phone/token/url)
  timestamp: Number (SK)
  sentAt: Number (optional)
  deliveredAt: Number (optional)
  failedAt: Number (optional)
  errorMessage: String (optional)
  metadata: Map {
    messageId: String (SES/FCM message ID)
    subject: String (for emails)
    retryCount: Number
  }
}
```

### 6.2 Logging Implementation

```python
def log_notification(notification_data: dict):
    """
    Log notification delivery attempt
    """
    notifications_table.put_item(
        Item={
            'notificationId': f"notif-{uuid.uuid4()}",
            'alertId': notification_data['alertId'],
            'userId': notification_data['userId'],
            'channel': notification_data['channel'],
            'status': 'queued',
            'recipient': notification_data['recipient'],
            'timestamp': int(time.time() * 1000),
            'metadata': notification_data.get('metadata', {})
        }
    )

def update_notification_status(notification_id: str, status: str, **kwargs):
    """
    Update notification status
    """
    update_expression = 'SET #status = :status'
    expression_values = {':status': status}
    expression_names = {'#status': 'status'}

    if status == 'sent':
        update_expression += ', sentAt = :sentAt'
        expression_values[':sentAt'] = int(time.time() * 1000)
    elif status == 'delivered':
        update_expression += ', deliveredAt = :deliveredAt'
        expression_values[':deliveredAt'] = int(time.time() * 1000)
    elif status == 'failed':
        update_expression += ', failedAt = :failedAt, errorMessage = :error'
        expression_values[':failedAt'] = int(time.time() * 1000)
        expression_values[':error'] = kwargs.get('error', 'Unknown error')

    notifications_table.update_item(
        Key={'notificationId': notification_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values
    )
```

## 7. Error Handling & Retry Logic

### 7.1 Retry Strategy

**SQS Configuration:**
```yaml
AlertQueue:
  Type: AWS::SQS::Queue
  Properties:
    VisibilityTimeout: 30  # Seconds
    MessageRetentionPeriod: 1209600  # 14 days
    ReceiveMessageWaitTimeSeconds: 20  # Long polling
    RedrivePolicy:
      deadLetterTargetArn: !GetAtt AlertDLQ.Arn
      maxReceiveCount: 3  # Retry 3 times before DLQ
```

**Lambda Retry Configuration:**
```yaml
functions:
  notificationDispatcher:
    handler: src/functions/stream_processing/notification_dispatcher.handler
    events:
      - sqs:
          arn: !GetAtt AlertQueue.Arn
          batchSize: 10
          functionResponseType: ReportBatchItemFailures  # Partial batch failures
```

### 7.2 Failure Handling

```python
def lambda_handler(event, context):
    """
    Process SQS messages with partial failure handling
    """
    batch_item_failures = []

    for record in event['Records']:
        try:
            # Process notification
            process_notification(record)

        except RecoverableError as e:
            # Temporary failure, will retry
            logger.warning(f"Recoverable error: {e}")
            batch_item_failures.append({
                'itemIdentifier': record['messageId']
            })

        except NonRecoverableError as e:
            # Permanent failure, send to DLQ
            logger.error(f"Non-recoverable error: {e}")
            # Do not add to batch_item_failures, will be deleted from queue

    # Return failed items for retry
    return {
        'batchItemFailures': batch_item_failures
    }
```

### 7.3 Dead Letter Queue Processing

```python
def process_dlq_messages(event):
    """
    Process messages from DLQ
    - Log for manual investigation
    - Alert operations team
    - Optionally attempt manual retry
    """
    for record in event['Records']:
        message = json.loads(record['body'])

        logger.error(f"DLQ message: {message}")

        # Alert ops team
        send_ops_alert({
            'title': 'Notification DLQ Alert',
            'message': f"Failed to process alert: {message['alertId']}",
            'severity': 'high'
        })

        # Store for manual review
        store_failed_notification(message)
```

## 8. Rate Limiting & Throttling

### 8.1 SES Rate Limits

**Default Limits:**
- Sending rate: 14 messages/second
- Daily quota: 50,000 emails/day

**Request Limit Increase:**
- Production: Request 100/second, 500,000/day

**Implementation:**
```python
class RateLimiter:
    def __init__(self, max_per_second):
        self.max_per_second = max_per_second
        self.tokens = max_per_second
        self.last_update = time.time()

    def acquire(self):
        """
        Token bucket algorithm
        """
        now = time.time()
        elapsed = now - self.last_update

        # Refill tokens
        self.tokens = min(
            self.max_per_second,
            self.tokens + elapsed * self.max_per_second
        )
        self.last_update = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        else:
            # Rate limited, wait
            time.sleep((1 - self.tokens) / self.max_per_second)
            self.tokens = 0
            return True

# Usage
ses_rate_limiter = RateLimiter(14)  # 14 emails/second

def send_email_with_rate_limit(recipient, subject, body):
    ses_rate_limiter.acquire()
    return ses_provider.send_email(recipient, subject, body)
```

### 8.2 FCM Rate Limits

**Limits:**
- No official rate limit
- Best practice: Use multicast for bulk sends

### 8.3 SNS SMS Rate Limits

**Limits:**
- 20 messages/second (US)
- 100 messages/day per phone number

## 9. Notification Analytics

### 9.1 Metrics to Track

```python
# CloudWatch Metrics
publish_metric('NotificationsSent', count=1, dimensions=[
    {'Name': 'Channel', 'Value': 'email'},
    {'Name': 'Severity', 'Value': 'critical'}
])

publish_metric('NotificationDeliveryTime', value=delivery_time_ms, unit='Milliseconds')

publish_metric('NotificationFailureRate', value=failure_rate, unit='Percent')
```

### 9.2 Dashboard Queries

**Daily Notification Volume:**
```sql
SELECT channel, COUNT(*) as count
FROM notifications
WHERE timestamp > ago(24h)
GROUP BY channel
```

**Delivery Success Rate:**
```sql
SELECT
  channel,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) as delivered,
  (SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as success_rate
FROM notifications
WHERE timestamp > ago(7d)
GROUP BY channel
```

## 10. Cost Optimization

### 10.1 Cost Analysis

| Channel | Cost per 1,000 | Monthly Estimate (100k alerts) |
|---------|----------------|--------------------------------|
| Email (SES) | $0.10 | $10 |
| Push (FCM) | Free | $0 |
| SMS (SNS) | $6.45 (US) | $645 |

**Optimization Strategies:**
1. **Prefer push over email** for real-time alerts
2. **Use SMS sparingly** (only critical alerts)
3. **Batch email notifications** for non-critical alerts
4. **Implement notification de-duplication** to reduce volume

### 10.2 De-duplication

**Strategy:**
```python
def should_send_notification(alert_id, user_id, channel):
    """
    Check if notification was already sent recently
    """
    recent_notifications = query_recent_notifications(
        alertId=alert_id,
        userId=user_id,
        channel=channel,
        time_window=300  # 5 minutes
    )

    if len(recent_notifications) > 0:
        logger.info(f"Skipping duplicate notification: {alert_id}")
        return False

    return True
```

### 10.3 Digest Notifications

**Batch non-critical alerts:**
```python
def send_digest_notification(user_id):
    """
    Send digest of non-critical alerts (hourly)
    """
    pending_alerts = get_pending_alerts(user_id, severity=['info', 'warning'])

    if len(pending_alerts) == 0:
        return

    # Group by device
    alerts_by_device = group_by(pending_alerts, key='deviceId')

    # Generate digest email
    email_body = render_digest_template(alerts_by_device)

    send_email(
        recipient=user_email,
        subject=f"Alert Digest - {len(pending_alerts)} new alerts",
        body=email_body
    )

    # Mark alerts as notified
    mark_alerts_notified(pending_alerts)
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Document Owner:** Notification Team
