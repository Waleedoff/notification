
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Union

import firebase_admin
import googleapiclient.discovery
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from google.auth.exceptions import RefreshError
from google.oauth2 import service_account
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError


from app.common.logging import logger
from app.config import config


class GoogleClient(object):
    def __init__(self):
        self.config = config
        
    def _handle_google_response_or_abort_on_error(self, response):
        """
        Handles Google Calendar API and Firebase errors and raises exceptions if errors occur.

        Args:
            response (dict): The response received from the Google Calendar API or Firebase.

        Returns:
            dict: The response JSON if successful.
            dict: Error information if an error occurred.
        """

        if isinstance(response, RefreshError):
            error_elements = {"message": str(response)}
            logger.exception(
                f"RefreshError: {error_elements.get('message')}",
                exc_info=error_elements,
            )
            return error_elements
        elif isinstance(response, HttpError):
            error_info = {
                "reason": response.resp.reason,
                "status_code": response.resp.status,
                "error_details": response._get_reason(),
            }
            if response.content:
                content_str = response.content.decode("utf-8")
                error_info["content"] = json.loads(content_str)
            logger.exception(
                f"HttpError: {error_info.get('reason')}", exc_info=error_info
            )
            return error_info
        elif isinstance(response, FirebaseError):
            error_info = {
                "message": str(response),
                "code": response.code,
                "status_code": response.http_response.status_code,
            }

            logger.exception(
                f"FirebaseError: {error_info['message']}", exc_info=response
            )
            return error_info
        else:
            logger.exception(response)
            return response
        
    def _get_credentials_file_path(self):
        credentials_file = Path(__file__).resolve().parent / "google_credentials.json"
        if not credentials_file.exists():
            self._create_credentials_file(credentials_file)
        return str(credentials_file)

    def _create_credentials_file(self, credentials_file):
        try:
            configurations = {
                "type": config.GOOGLE_TYPE,
                "project_id": config.GOOGLE_PROJECT_ID,
                "private_key_id": config.GOOGLE_PRIVATE_KEY_ID,
                "private_key": config.GOOGLE_PRIVATE_KEY,
                "client_email": config.GOOGLE_CLIENT_EMAIL,
                "client_id": config.GOOGLE_CLIENT_ID,
                "auth_uri": config.GOOGLE_AUTH_URI,
                "token_uri": config.GOOGLE_TOKEN_URI,
                "auth_provider_x509_cert_url": config.GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
                "client_x509_cert_url": config.GOOGLE_CLIENT_X509_CERT_URL,
                "universe_domain": config.GOOGLE_UNIVERSE_DOMAIN,
            }
            with open(credentials_file, "w") as json_file:
                json.dump(configurations, json_file, indent=4)
                logger.info("service created successfully.")
        except Exception as e:
            logger.exception(f"Failed to create credentials file: {e}")
            self._remove_credentials_file(credentials_file)
            return
        
    def _initialize_firebase_app(self):
        try:
            if not firebase_admin._apps:
                credentials_file = self._get_credentials_file_path()
                cred = credentials.Certificate(credentials_file)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase app initialized successfully.")
                self._remove_credentials_file(credentials_file)
        except Exception as e:
            self._remove_credentials_file(credentials_file)
            self._handle_google_response_or_abort_on_error(e)
    
    
    def send_messages_to_multiple_devices(
            self,
            title: str,
            body: str,
            tokens: list[str],
            data: dict[str, str] | None = {},  # (key: string, value: string)
            image: str | None = None,
        ):
            """
            Sends a push notification via Firebase Cloud Messaging (FCM) to multiple devices.

            Args:
                title (str): The notification title.
                body (str): The notification body.
                tokens (list[str]): The recipient devices' FCM tokens.
                data (dict): An object containing a list of "key": value pairs for the message payload.
                image (str, optional): URL of the image to be displayed in the notification.

            Returns:
                list: A list of objects containing success status, token, and response ID (or error).
            """
            self._initialize_firebase_app()
            message = messaging.MulticastMessage(
                data=data,
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image,
                ),
                tokens=tokens,
            )

            try:
                response = messaging.send_each_for_multicast(message)
                response_details = []

                for idx, resp in enumerate(response.responses):
                    if resp.success:
                        response_details.append(
                            {
                                "success": True,
                                "token": tokens[idx],
                                "message_id": resp.message_id,
                            }
                        )
                    else:
                        response_details.append(
                            {
                                "success": False,
                                "token": tokens[idx],
                                "error": str(resp.exception),
                            }
                        )
                return dict(response=response_details)
            except Exception as e:
                return self._handle_google_response_or_abort_on_error(e)
            
            
    def _remove_credentials_file(self, credentials_file):
        if os.path.exists(credentials_file):
            os.remove(credentials_file)
            logger.info(f"Removed credentials file: {credentials_file}")