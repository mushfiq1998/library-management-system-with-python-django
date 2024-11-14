from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import barcode
from barcode.writer import ImageWriter

'''
    A genre is a category or classification that describes the type or style of a book.
'''
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('AR', 'Arabic'),
        ('BA', 'Bengali'),
        ('UR', 'Urdu'),
        ('HI', 'Hindi'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(
        Author, related_name='books')
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    genres = models.ManyToManyField(
        Genre, related_name='books')
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=100, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default='EN')
    barcode = models.ImageField(upload_to='barcodes/', blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate barcode
        if not self.barcode:
            EAN = barcode.get_barcode_class('ean13')
            ean = EAN(self.isbn, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            self.barcode.save(
                f'barcode_{self.isbn}.png', File(buffer), save=False)

        # Generate QR code
        if not self.qr_code:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f'Book: {self.title}\nISBN: {self.isbn}')
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            self.qr_code.save(f'qr_{self.isbn}.png', File(buffer), save=False)

        super().save(*args, **kwargs)
