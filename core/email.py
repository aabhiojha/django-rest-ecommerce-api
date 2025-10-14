from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string


def welcome_mail(user):
    subject = "Welcome to the site!"
    message = f"Hi, {user.get_full_name()},\n\nThanks for signing up. Glad to have you!\n\nBest regards,\nThe Team"
    from_email = settings.DEFAULT_FROM_EMAIL
    recepient_list = [user.email]

    send_mail(
        subject,
        message,
        from_email,
        recepient_list,
        fail_silently=False,
    )


def send_payment_receipt(user, order, payment):
    
    subject = f'Payment Receipt - Order #{order.id}'

    # items_details = ""
    # for order_item in order.order_items.all():
    #     items_details += f"- {order_item.item.product.name} x {order_item.quantity} = {order.total_amount}\n"

    # HTML version
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>Payment Receipt</h2>
        <p>Hi {user.get_full_name()},</p>
        <p>Thank you for your purchase! Your payment has been successfully processed.</p>
        
        <h3>Order Details</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Order ID:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{order.id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Order Date:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{order.created_at.strftime('%B %d, %Y at %I:%M %p')}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Status:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">{order.status.upper()}</td>
            </tr>
        </table>
        
        <h3>Items Purchased</h3>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background-color: #f4f4f4;">
                    <th style="padding: 8px; text-align: left; border-bottom: 2px solid #ddd;">Item</th>
                    <th style="padding: 8px; text-align: center; border-bottom: 2px solid #ddd;">Quantity</th>
                    <th style="padding: 8px; text-align: right; border-bottom: 2px solid #ddd;">Price</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f'''
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item.item.product.name}</td>
                    <td style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd;">{item.quantity}</td>
                    <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">${item.total_price:.2f}</td>
                </tr>
                ''' for item in order.order_items.all()])}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="2" style="padding: 8px; text-align: right; border-top: 2px solid #ddd;"><strong>Total:</strong></td>
                    <td style="padding: 8px; text-align: right; border-top: 2px solid #ddd;"><strong>${payment.amount:.2f}</strong></td>
                </tr>
            </tfoot>
        </table>
        
        <h3>Payment Information</h3>
        <p><strong>Payment Status:</strong> {payment.status.upper()}</p>
        <p><strong>Transaction ID:</strong> {payment.stripe_payment_intent_id}</p>
        
        <p>If you have any questions, please contact our support team.</p>
        <p>Best regards,<br>The Team</p>
    </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    email = EmailMultiAlternatives(subject, html_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)