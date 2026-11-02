"""
Push Notifications Service
KCo Fleet Intelligence Platform - Old But Gold TR8 IVSTO

Supports:
- Web Push (Chrome, Firefox, Edge)
- Firebase Cloud Messaging (FCM)
- Apple Push Notification Service (APNS)
- Email notifications
- SMS notifications (via Twilio)
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
from dataclasses import dataclass, field

from backend.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class PushNotification:
    """Push notification data"""
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    image: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationSubscription:
    """Push notification subscription"""
    endpoint: str
    keys: Dict[str, Any]
    user_id: Optional[str] = None
    device_type: str = "web"
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None


class PushNotificationService:
    """Push notification service"""
    
    def __init__(self):
        self.subscriptions: Dict[str, NotificationSubscription] = {}
        self._load_subscriptions()
    
    def _load_subscriptions(self):
        """Load subscriptions from storage"""
        # In production, load from database
        pass
    
    def save_subscription(self, subscription: NotificationSubscription) -> str:
        """Save push notification subscription"""
        subscription_id = str(uuid.uuid4())
        self.subscriptions[subscription_id] = subscription
        
        # In production, save to database
        logger.info(f"Saved subscription {subscription_id}")
        
        return subscription_id
    
    def get_subscription(self, subscription_id: str) -> Optional[NotificationSubscription]:
        """Get subscription by ID"""
        return self.subscriptions.get(subscription_id)
    
    def get_subscriptions_by_user(self, user_id: str) -> List[NotificationSubscription]:
        """Get all subscriptions for a user"""
        return [s for s in self.subscriptions.values() if s.user_id == user_id]
    
    def delete_subscription(self, subscription_id: str) -> bool:
        """Delete subscription"""
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            logger.info(f"Deleted subscription {subscription_id}")
            return True
        return False
    
    async def send_notification(
        self,
        notification: PushNotification,
        user_id: Optional[str] = None,
        subscription_id: Optional[str] = None
    ) -> bool:
        """Send push notification"""
        try:
            # Determine targets
            if subscription_id:
                targets = [self.subscriptions.get(subscription_id)]
            elif user_id:
                targets = self.get_subscriptions_by_user(user_id)
            else:
                # Send to all subscriptions
                targets = list(self.subscriptions.values())
            
            # Filter valid targets
            targets = [t for t in targets if t is not None]
            
            if not targets:
                logger.warning("No valid targets for notification")
                return False
            
            # Send to each target
            results = []
            for target in targets:
                result = await self._send_to_target(target, notification)
                results.append(result)
            
            # Return True if at least one succeeded
            return any(results)
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _send_to_target(
        self,
        target: NotificationSubscription,
        notification: PushNotification
    ) -> bool:
        """Send notification to specific target"""
        try:
            if target.device_type == "web":
                return await self._send_web_push(target, notification)
            elif target.device_type == "android":
                return await self._send_fcm(target, notification)
            elif target.device_type == "ios":
                return await self._send_apns(target, notification)
            else:
                logger.warning(f"Unknown device type: {target.device_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to target {target.endpoint}: {e}")
            return False
    
    async def _send_web_push(
        self,
        subscription: NotificationSubscription,
        notification: PushNotification
    ) -> bool:
        """Send web push notification"""
        try:
            import requests
            
            # Prepare payload
            payload = {
                "notification": {
                    "title": notification.title,
                    "body": notification.body,
                    "icon": notification.icon or "/icons/icon-192x192.png",
                    "badge": notification.badge or "/icons/badge-72x72.png",
                    "image": notification.image,
                    "timestamp": int(notification.timestamp.timestamp() * 1000)
                },
                "data": notification.data
            }
            
            # Add actions if provided
            if notification.actions:
                payload["notification"]["actions"] = notification.actions
            
            # Convert to JSON string
            payload_json = json.dumps(payload)
            
            # Send to push service
            headers = {
                "Content-Type": "application/json",
                "Content-Length": str(len(payload_json)),
                "TTL": "86400"  # 1 day
            }
            
            # Add VAPID headers for web push
            vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", settings.VAPID_PRIVATE_KEY)
            vapid_public_key = os.getenv("VAPID_PUBLIC_KEY", settings.VAPID_PUBLIC_KEY)
            
            if vapid_private_key and vapid_public_key:
                import jwt
                import time
                
                # Generate JWT token
                claims = {
                    "aud": "https://fcm.googleapis.com",
                    "exp": int(time.time()) + 86400,  # 24 hours
                    "sub": "mailto:notifications@kco.ai"
                }
                
                token = jwt.encode(claims, vapid_private_key, algorithm="ES256")
                headers["Authorization"] = f"Bearer {token}"
            
            # Send request
            response = requests.post(
                subscription.endpoint,
                data=payload_json,
                headers=headers,
                timeout=10
            )
            
            # Update last_used
            subscription.last_used = datetime.utcnow()
            
            return response.status_code in [200, 201]
            
        except ImportError:
            logger.error("Requests library not installed. Install with: pip install requests")
            return False
        except Exception as e:
            logger.error(f"Error sending web push: {e}")
            return False
    
    async def _send_fcm(
        self,
        subscription: NotificationSubscription,
        notification: PushNotification
    ) -> bool:
        """Send FCM notification"""
        try:
            import requests
            
            # Prepare payload
            payload = {
                "to": subscription.endpoint,
                "notification": {
                    "title": notification.title,
                    "body": notification.body,
                    "icon": notification.icon,
                    "image": notification.image,
                    "click_action": "OPEN_URL"
                },
                "data": notification.data
            }
            
            # Add actions
            if notification.actions:
                payload["notification"]["actions"] = notification.actions
            
            # Get FCM server key
            fcm_server_key = os.getenv("FCM_SERVER_KEY", settings.FCM_SERVER_KEY)
            
            if not fcm_server_key:
                logger.error("FCM server key not configured")
                return False
            
            # Send request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"key={fcm_server_key}"
            }
            
            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                data=json.dumps(payload),
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except ImportError:
            logger.error("Requests library not installed")
            return False
        except Exception as e:
            logger.error(f"Error sending FCM notification: {e}")
            return False
    
    async def _send_apns(
        self,
        subscription: NotificationSubscription,
        notification: PushNotification
    ) -> bool:
        """Send APNS notification"""
        try:
            import requests
            import jwt
            import time
            
            # Prepare payload
            payload = {
                "aps": {
                    "alert": {
                        "title": notification.title,
                        "body": notification.body
                    },
                    "badge": 1,
                    "sound": "default"
                },
                "data": notification.data
            }
            
            # Get APNS auth key
            apns_auth_key = os.getenv("APNS_AUTH_KEY", settings.APNS_AUTH_KEY)
            apns_key_id = os.getenv("APNS_KEY_ID", settings.APNS_KEY_ID)
            apns_team_id = os.getenv("APNS_TEAM_ID", settings.APNS_TEAM_ID)
            
            if not all([apns_auth_key, apns_key_id, apns_team_id]):
                logger.error("APNS credentials not configured")
                return False
            
            # Generate JWT token
            headers = {
                "alg": "ES256",
                "kid": apns_key_id
            }
            
            claims = {
                "iss": apns_team_id,
                "iat": int(time.time())
            }
            
            token = jwt.encode(claims, apns_auth_key, headers=headers, algorithm="ES256")
            
            # Send request
            headers = {
                "apns-topic": f"{apns_team_id}.com.kco.ml",
                "apns-push-type": "alert",
                "authorization": f"bearer {token}"
            }
            
            response = requests.post(
                f"https://api.sandbox.push.apple.com/3/device/{subscription.endpoint}",
                data=json.dumps(payload),
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except ImportError:
            logger.error("PyJWT or requests library not installed")
            return False
        except Exception as e:
            logger.error(f"Error sending APNS notification: {e}")
            return False
    
    async def send_email_notification(
        self,
        email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email notification"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Get SMTP settings
            smtp_host = os.getenv("SMTP_HOST", settings.SMTP_HOST)
            smtp_port = int(os.getenv("SMTP_PORT", settings.SMTP_PORT))
            smtp_user = os.getenv("SMTP_USER", settings.SMTP_USER)
            smtp_password = os.getenv("SMTP_PASSWORD", settings.SMTP_PASSWORD)
            smtp_from = os.getenv("SMTP_FROM", settings.SMTP_FROM)
            
            if not all([smtp_host, smtp_port, smtp_user, smtp_password, smtp_from]):
                logger.error("SMTP settings not configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_from
            msg['To'] = email
            msg['Subject'] = subject
            
            # Add body
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            return True
            
        except ImportError:
            logger.error("Email libraries not installed")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    async def send_sms_notification(
        self,
        phone: str,
        message: str
    ) -> bool:
        """Send SMS notification via Twilio"""
        try:
            from twilio.rest import Client
            
            # Get Twilio settings
            twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", settings.TWILIO_ACCOUNT_SID)
            twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", settings.TWILIO_AUTH_TOKEN)
            twilio_phone = os.getenv("TWILIO_PHONE", settings.TWILIO_PHONE)
            
            if not all([twilio_account_sid, twilio_auth_token, twilio_phone]):
                logger.error("Twilio settings not configured")
                return False
            
            # Create client
            client = Client(twilio_account_sid, twilio_auth_token)
            
            # Send SMS
            message = client.messages.create(
                body=message,
                from_=twilio_phone,
                to=phone
            )
            
            return message.sid is not None
            
        except ImportError:
            logger.error("Twilio library not installed. Install with: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    def generate_vapid_keys(self) -> Dict[str, str]:
        """Generate VAPID keys for web push"""
        try:
            from pywebpush import webpush
            
            vapid_private_key = webpush.generate_vapid_keys()
            
            return {
                "public_key": vapid_private_key.public_key,
                "private_key": vapid_private_key.private_key
            }
            
        except ImportError:
            logger.error("PyWebPush not installed. Install with: pip install pywebpush")
            return {"public_key": "", "private_key": ""}
        except Exception as e:
            logger.error(f"Error generating VAPID keys: {e}")
            return {"public_key": "", "private_key": ""}


# Singleton instance
notification_service = PushNotificationService()
