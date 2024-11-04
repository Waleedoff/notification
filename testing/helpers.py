from datetime import datetime

from app.common.enums import UserGroup


def get_seed_data():
    return {
        "users": [
            {
                "id": "b6e74e7f-3266-4abc-b0a1-0de7c4ce6ccb",
                "name": "VC_JOBSEEKER",
                "role": UserGroup.VC_JOBSEEKER.value,
                "email": "vc@hotmail.sa",
                "mobile": "553478947",
                "username": "huhud_user_name",
                "created_by": "test",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
            },
            {
                "id": "bae74e7fc-3265-4ab4-b0a3-0de7c4ce6ccc",
                "name": "VC_ADMIN",
                "role": UserGroup.VC_ADMIN.value,
                "email": "vc2@hotmail.sa",
                "mobile": "553478948",
                "username": "waleed",
                "created_by": "test",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),

            },
            {
                "id": "bae74e7fc-3265-4ab4-b0a3-0de7c4ce6ccf",
                "name": "VC_COMPANY",
                "role": UserGroup.VC_COMPANY.value,
                "email": "vc3@hotmail.sa",
                "mobile": "553478949",
                "username": "safcsp",
                "created_by": "test",
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),

            },
        ]
    }
