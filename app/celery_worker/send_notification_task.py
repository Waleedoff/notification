from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.api.notification.enums import NotificationStatus, NotificationType
from app.api.notification.models import Device, Notification
from app.api.auth.models import User
from app.celery_worker.app import CustomTask
from app.common.google_client import GoogleClient
from app.common.utils import chunk_list, generate_random_uuid


# Do not pass user_emails and user_ids if you wish to notify every user.
def send_notification_task_(
    self: CustomTask,
    notification_type: NotificationType,
    title: str,
    body: str,
    user_ids: list[str] = [],
    user_emails: list[str] = [],
    data: dict | None = None,
    image: str | None = None,
):
    google_client = GoogleClient()

    # Remove None values from the data dictionary
    data = {k: v for k, v in (data or {}).items() if v is not None}

    device_tokens, user_device_map = fetch_user_devices(
        self.session, user_ids, user_emails
    )

    if not device_tokens and user_device_map:
        create_notifications_for_users(
            self.session,
            user_device_map,
            notification_type,
            title,
            body,
            data,
            image,
        )
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
            session=self.session,
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
    notifications = []
    for user_id in user_device_map.keys():
        notifications.append(
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
        )
    save_notifications_bulk(session=session, notifications=notifications)


def fetch_user_devices(session: Session, user_ids: list[str], user_emails: list[str]):
    device_tokens = []
    user_device_map = {}

    if not (user_emails or user_ids):
        stmt = select(User).options(selectinload(User.devices))
    else:
        stmt = (
            select(User)
            .where(or_(User.id.in_(user_ids), User.email.in_(user_emails)))
            .options(selectinload(User.devices))
        )

    users = session.execute(stmt).scalars().all()

    for user in users:
        tokens = [
            device.device_token for device in user.devices if user.allow_notification
        ]
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
            NotificationStatus.SENT.value
            if is_sent
            else NotificationStatus.STORED_ONLY.value
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
    notifications = []

    if "response" not in fcm_response or not fcm_response["response"]:
        create_notifications_for_users(
            session,
            user_device_map,
            notification_type,
            title,
            body,
            data,
            image,
        )
        return None

    all_failed = True
    successful_device_ids = {}

    token_to_user_map = {}
    for user_id, devices in user_device_map.items():
        for device in devices:
            token_to_user_map[device.device_token] = (user_id, devices)

    for device_response in fcm_response.get("response", []):
        token = device_response["token"]
        user_info = token_to_user_map.get(token)

        if not user_info:
            continue

        user_id, user_devices = user_info
        active_device = next(
            (
                device
                for device in user_devices
                if device.is_active and device.user_id == user_id
            ),
            None,
        )

        if device_response["success"]:
            all_failed = False

            if user_id not in successful_device_ids and active_device:
                successful_device_ids[user_id] = {
                    "message_id": device_response["message_id"],
                    "device_id": active_device.id,
                }
        else:
            #  not success
            if user_id not in successful_device_ids:
                # find any successful response to use its message_id
                for check_response in fcm_response.get("response", []):
                    if check_response.get("success") and user_info:
                        success_device_token = next(
                            (
                                device
                                for device in user_devices
                                if device.device_token == token
                            ),
                            None,
                        )
                        successful_device_ids[user_id] = {
                            "message_id": check_response["message_id"],
                            "device_id": success_device_token.id,  # type: ignore
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
                    None
                    if all_failed
                    else device_info["message_id"] if device_info else None
                ),
                device_id=(device_info["device_id"] if device_info else None),
                data=data,
                image=image,
                is_sent=not all_failed,
            )
        )

    save_notifications_bulk(session=session, notifications=notifications)


def save_notifications_bulk(
    session: Session,
    notifications: list[Notification],
):
    session.bulk_save_objects(notifications)
