from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction


User = get_user_model()


def get_or_create_google_user(user_data):
    google_sub = (user_data.get("sub") or "").strip()
    email = (user_data.get("email") or "").strip().lower()
    full_name = (user_data.get("name") or "").strip()
    avatar_url = (user_data.get("picture") or "").strip()

    if not google_sub:
        raise ValueError("Google account did not return a subject id")
    if not email:
        raise ValueError("Google account did not return an email")

    try:
        with transaction.atomic():
            user = User.objects.filter(google_sub=google_sub).first()
            if user is None:
                user = User.objects.filter(email=email).first()

            created = False
            if user is None:
                user = User.objects.create_user(
                    email=email,
                    full_name=full_name,
                    avatar_url=avatar_url,
                    google_sub=google_sub,
                )
                created = True
            else:
                changed_fields = []
                if not user.google_sub:
                    user.google_sub = google_sub
                    changed_fields.append("google_sub")
                if full_name and user.full_name != full_name:
                    user.full_name = full_name
                    changed_fields.append("full_name")
                if avatar_url and user.avatar_url != avatar_url:
                    user.avatar_url = avatar_url
                    changed_fields.append("avatar_url")
                if changed_fields:
                    changed_fields.append("updated_at")
                    user.save(update_fields=changed_fields)

            return user, created
    except IntegrityError as e:
        raise ValueError(f"Database error while signing in with Google: {str(e)}")
