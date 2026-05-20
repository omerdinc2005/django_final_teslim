from django.shortcuts import render
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from core.models import Document
from contact.models import Message

#


def index(request):
    """Render the main index page."""
    return render(request, 'index.html')


def contact_form(request):
    """Handle contact form: validate, save to db, send email, and respond."""
    if request.method == 'POST':
        # Alanlar görseldeki modele uygun olarak (name, subject dahil) güncellendi.
        # HTML formundaki input 'name' değerlerinin bunlarla eşleştiğinden emin ol.
        name = request.POST.get('name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()



        errors = []
        if not name:
            errors.append('Ad alanı zorunludur.')
        if not last_name:
            errors.append('Soyad alanı zorunludur.')
        if not email:
            errors.append('Email alanı zorunludur.')
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Geçerli bir e-posta adresi giriniz.')
        if not subject:
            errors.append('Konu alanı zorunludur.')
        if not message:
            errors.append('Mesaj alanı zorunludur.')

        if errors:
            resp = {'success': False, 'message': ' '.join(errors)}
            return JsonResponse(resp, status=400)

        # 1. VERİTABANINA KAYIT İŞLEMİ (Görselden eklenen kısım)
        try:
            Message.objects.create(
                name=name,
                last_name=last_name,
                email=email,
                subject=subject,
                message=message
            )

        except Exception as e:
            resp = {'success': False, 'message': 'Mesaj veritabanına kaydedilirken bir hata oluştu.'}
            print('DB create error:', e)
            return JsonResponse(resp, status=500)

        # 2. E-POSTA GÖNDERME İŞLEMİ (Senin orijinal kodun)
        mail_subject = f"Site Contact: {name} - {subject}"
        body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', email)
        to_email = [getattr(settings, 'DEFAULT_FROM_EMAIL', 'admin@example.com')]

        try:
            send_mail(mail_subject, body, from_email, to_email, fail_silently=False)
        except Exception as e:
            resp = {'success': False, 'message': 'E-posta gönderilirken bir hata oluştu.'}
            print('send_mail error:', e)
            return JsonResponse(resp, status=500)

        # Her iki işlem de başarılıysa dönecek cevap
        data = {'success': True, 'message': 'Contact form sent successfully.'}
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(data)
        return render(request, 'contact.html', data)

    # GET -> render empty contact page with documents
    return render(request, 'contact.html')