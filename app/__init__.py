from importlib import import_module

APP_MODELS = [
    "app.api.auth.models",
    "app.api.notification.models"

]

for model in APP_MODELS:
    import_module(model)
