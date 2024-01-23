from django.shortcuts import render, redirect

# Create your views here.

def customer_form(request):
    if request.method == "POST":
        email = request.POST.get('email')
        return redirect('customer', email_id=email)
    return render(request, "chat/customer_form.html")

def customer(request, email_id):
    return render(request, "chat/customer.html", {"email_id": email_id})