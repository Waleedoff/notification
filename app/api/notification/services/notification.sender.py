# notification_sender.py

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload
from app.api.notification.enums import NotificationStatus, NotificationType
from app.api.notification.models import Device, Notification
from app.api.auth.models import User
from app.common.google_client import GoogleClient
from app.common.utils import chunk_list, generate_random_uuid

def send_notification(
    session: Session,
    notification_type: NotificationType,
    title: str,
    body: str,
    user_ids: list[str] = [],
    user_emails: list[str] = [],
    data: dict | None = None,
    image: str | None = None,
):
    """
    Main function to send notifications to devices.
    """
    google_client = GoogleClient()
    data = {k: v for k, v in (data or {}).items() if v is not None}
    
    device_tokens, user_device_map = fetch_user_devices(session, user_ids, user_emails)

    if not device_tokens and user_device_map:
        create_notifications_for_users(session, user_device_map, notification_type, title, body, data, image)
        return "Notification saved successfully"

    token_batches = chunk_list(device_tokens, 450)
    for token_batch in token_batches:
        fcm_response = google_client.send_messages_to_multiple_devices(
            title=title,
            body=body,
            tokens=token_batch,
            data=data,
            image=image,
        )

        handle_fcm_response_batch(
            session=session,
            user_device_map=user_device_map,
            fcm_response=fcm_response,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data,
            image=image,
        )

    return "Notification sent successfully"


def create_notifications_for_users(
    session: Session,
    user_device_map: dict,
    notification_type: NotificationType,
    title: str,
    body: str,
    data: dict | None,
    image: str | None,
):
    """
    Creates notifications for users without sending them immediately.
    """
    notifications = [
        create_notification(
            notification_type=notification_type,
            user_id=user_id,
            title=title,
            body=body,
            notification_id=None,
            device_id=None,
            data=data,
            image=image,
            is_sent=False,
        )
        for user_id in user_device_map.keys()
    ]
    save_notifications_bulk(session=session, notifications=notifications)


def fetch_user_devices(session: Session, user_ids: list[str], user_emails: list[str]):
    """
    Retrieves device tokens and maps users to their devices.
    """
    device_tokens = []
    user_device_map = {}

    stmt = select(User).options(selectinload(User.devices))
    if user_ids or user_emails:
        stmt = stmt.where(or_(User.id.in_(user_ids), User.email.in_(user_emails)))

    users = session.execute(stmt).scalars().all()

    for user in users:
        tokens = [device.device_token for device in user.devices if user.allow_notification]
        device_tokens.extend(tokens)
        user_device_map[user.id] = user.devices

    return device_tokens, user_device_map


def create_notification(
    notification_type: NotificationType,
    user_id: str,
    title: str,
    body: str,
    notification_id: str | None,
    device_id: str | None = None,
    data: dict | None = None,
    image: str | None = None,
    is_sent: bool = False,
):
    """
    Helper function to create a notification object.
    """
    return Notification(
        notification_id=notification_id or generate_random_uuid(),
        device_id=device_id,
        title=title,
        body=body,
        image=image,
        data=data or {},
        user_id=user_id,
        created_by=user_id,
        notification_status=(
            NotificationStatus.SENT.value if is_sent else NotificationStatus.STORED_ONLY.value
        ),
        notification_type=notification_type,
    )


def handle_fcm_response_batch(
    session: Session,
    user_device_map: dict[str, list[Device]],
    fcm_response: dict,
    title: str,
    body: str,
    notification_type: NotificationType,
    data: dict | None,
    image: str | None,
):
    """
    Handles the FCM response and updates notification status based on response.
    """
    notifications = []

    if "response" not in fcm_response or not fcm_response["response"]:
        create_notifications_for_users(session, user_device_map, notification_type, title, body, data, image)
        return None

    all_failed = True
    successful_device_ids = {}
    token_to_user_map = {device.device_token: (user_id, devices)
                         for user_id, devices in user_device_map.items() for device in devices}

    for device_response in fcm_response.get("response", []):
        token = device_response["token"]
        user_info = token_to_user_map.get(token)

        if not user_info:
            continue

        user_id, user_devices = user_info
        active_device = next((device for device in user_devices if device.is_active and device.user_id == user_id), None)

        if device_response["success"]:
            all_failed = False
            if user_id not in successful_device_ids and active_device:
                successful_device_ids[user_id] = {
                    "message_id": device_response["message_id"],
                    "device_id": active_device.id,
                }
        else:
            if user_id not in successful_device_ids:
                for check_response in fcm_response.get("response", []):
                    if check_response.get("success") and user_info:
                        success_device_token = next(
                            (device for device in user_devices if device.device_token == token), None
                        )
                        successful_device_ids[user_id] = {
                            "message_id": check_response["message_id"],
                            "device_id": success_device_token.id,
                        }
                        break

    for user_id in user_device_map.keys():
        device_info = successful_device_ids.get(user_id, None)

        notifications.append(
            create_notification(
                notification_type=notification_type,
                user_id=user_id,
                title=title,
                body=body,
                notification_id=(
                    None if all_failed else device_info["message_id"] if device_info else None
                ),
                device_id=(device_info["device_id"] if device_info else None),
                data=data,
                image=image,
                is_sent=not all_failed,
            )
        )

    save_notifications_bulk(session=session, notifications=notifications)


def save_notifications_bulk(session: Session, notifications: list[Notification]):
    """
    Saves multiple notifications in bulk.
    """
    session.bulk_save_objects(notifications)
