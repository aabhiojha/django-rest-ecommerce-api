from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponseBadRequest


@csrf_exempt
def payment_webhook(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method.")

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON payload.")

    # Perform different actions based on the event type
    event_type = data.get("event_type")

    if event_type == "payment_success":
        handle_payment_success(data)
    elif event_type == "payment_failure":
        handle_payment_failure(data)
    else:
        return HttpResponseBadRequest("Unhandled event type.")

    # Acknowledge receipt of the webhook
    return JsonResponse({"status": "success"})


def handle_payment_success(data):
    # Extract payment details and update your models or perform required actions
    transaction_id = data["transaction_id"]
    amount = data["amount"]
    # Logic to update the database or notify the user
    print(f"Payment succeeded with ID: {transaction_id} for amount: {amount}")


def handle_payment_failure(data):
    # Handle payment failure logic
    transaction_id = data["transaction_id"]
    reason = data["failure_reason"]
    # Logic to update the database or notify the user
    print(f"Payment failed with ID: {transaction_id}. Reason: {reason}")
