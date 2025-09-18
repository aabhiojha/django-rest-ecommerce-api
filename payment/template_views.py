from django.shortcuts import render


def successful_payment(request):
    return render(request, "payment/success.html")


def failed_payment(request):
    return render(request, "payment/failed.html")
