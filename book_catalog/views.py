from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book, Author, Genre
from .forms import BookForm, AuthorForm, GenreForm
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from django.utils import timezone

def is_librarian_or_admin(user):
    return user.role in ['LIBRARIAN', 'ADMIN']

@login_required
def book_list(request):
    books = Book.objects.all().order_by('title')
    return render(
        request, 'book_catalog/book_list.html', {'books': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_catalog/book_detail.html', {'book': book})

@login_required
@user_passes_test(is_librarian_or_admin)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, 'Book created successfully.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    context = {
        'form': form,
        'action': 'Create'
    }
    return render(request, 'book_catalog/book_form.html', context)

@login_required
@user_passes_test(is_librarian_or_admin)
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    context = {
        'form': form,
        'action': 'Edit'
    }
    return render(request, 'book_catalog/book_form.html', context)


@login_required
@user_passes_test(is_librarian_or_admin)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    context = {
        'book': book
    }
    return render(request, 'book_catalog/book_confirm_delete.html', context)

@login_required
def author_list(request):
    authors = Author.objects.all().order_by('name')
    return render(request, 'book_catalog/author_list.html', {'authors': authors})

@login_required
def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'book_catalog/author_detail.html', {'author': author})

@login_required
@user_passes_test(is_librarian_or_admin)
def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, 'Author added successfully.')
            return redirect('author_detail', pk=author.pk)
    else:
        form = AuthorForm()
    return render(request, 'book_catalog/author_form.html', {'form': form, 'action': 'Add'})

@login_required
@user_passes_test(is_librarian_or_admin)
def author_edit(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, 'Author updated successfully.')
            return redirect('author_detail', pk=author.pk)
    else:
        form = AuthorForm(instance=author)
    return render(request, 'book_catalog/author_form.html', {
        'form': form,
        'action': 'Edit'
    })

@login_required
@user_passes_test(is_librarian_or_admin)
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        author.delete()
        messages.success(request, 'Author deleted successfully.')
        return redirect('author_list')
    return render(request, 'book_catalog/author_confirm_delete.html', {
        'author': author
    })

@login_required
def genre_list(request):
    genres = Genre.objects.all().order_by('name')
    return render(request, 'book_catalog/genre_list.html', {'genres': genres})

@login_required
@user_passes_test(is_librarian_or_admin)
def genre_create(request):
    if request.method == 'POST':
        form = GenreForm(request.POST)
        if form.is_valid():
            genre = form.save()
            messages.success(request, 'Genre added successfully.')
            return redirect('genre_list')
    else:
        form = GenreForm()
    return render(request, 'book_catalog/genre_form.html', {'form': form, 'action': 'Add'})

@login_required
def author_pdf(request, pk):
    author = get_object_or_404(Author, pk=pk)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="author_{author.pk}.pdf"'
    
    # Create the PDF object using ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#4e73df')
    )
    
    # Add content to the PDF
    elements.append(Paragraph(f"Author Profile: {author.name}", title_style))
    
    # Basic Information
    elements.append(Paragraph("Basic Information", heading_style))
    elements.append(Paragraph(f"<b>Name:</b> {author.name}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Birth Date:</b> {author.birth_date or 'Unknown'}", styles["Normal"]))
    if author.death_date:
        elements.append(Paragraph(f"<b>Death Date:</b> {author.death_date}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    # Biography
    if author.biography:
        elements.append(Paragraph("Biography", heading_style))
        elements.append(Paragraph(author.biography, styles["Normal"]))
        elements.append(Spacer(1, 12))
    
    # Books
    elements.append(Paragraph("Books", heading_style))
    if author.books.exists():
        for book in author.books.all():
            elements.append(Paragraph(f"• {book.title} ({book.publication_date.year if book.publication_date else 'Year unknown'})", styles["Normal"]))
    else:
        elements.append(Paragraph("No books available for this author.", styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
def book_pdf(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="book_{book.pk}.pdf"'
    
    # Create the PDF object using ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#4e73df')
    )
    
    # Add content to the PDF
    elements.append(Paragraph(f"Book Details: {book.title}", title_style))
    
    # Basic Information
    elements.append(Paragraph("Basic Information", heading_style))
    elements.append(Paragraph(f"<b>Title:</b> {book.title}", styles["Normal"]))
    elements.append(Paragraph(f"<b>ISBN:</b> {book.isbn}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Language:</b> {book.get_language_display()}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Publication Date:</b> {book.publication_date}", styles["Normal"]))
    if book.edition:
        elements.append(Paragraph(f"<b>Edition:</b> {book.edition}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    # Authors
    elements.append(Paragraph("Authors", heading_style))
    for author in book.authors.all():
        elements.append(Paragraph(f"• {author.name}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    # Genres
    elements.append(Paragraph("Genres", heading_style))
    for genre in book.genres.all():
        elements.append(Paragraph(f"• {genre.name}", styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    # Summary
    if book.summary:
        elements.append(Paragraph("Summary", heading_style))
        elements.append(Paragraph(book.summary, styles["Normal"]))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response

@login_required
def book_list_pdf(request):
    books = Book.objects.all().order_by('title')
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="book_list_{timezone.now().strftime("%Y%m%d")}.pdf"'
    
    # Create the PDF object using ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          leftMargin=50, rightMargin=50, 
                          topMargin=50, bottomMargin=50)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=30,
        textColor=colors.HexColor('#1a237e'),
        alignment=1,  # Center alignment
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=1,  # Center alignment
        spaceAfter=30,
        fontName='Helvetica-Oblique'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=20,
        spaceBefore=15,
        spaceAfter=15,
        textColor=colors.HexColor('#1976d2'),
        fontName='Helvetica-Bold'
    )
    
    book_title_style = ParagraphStyle(
        'BookTitle',
        parent=styles['Heading3'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#2196f3'),
        fontName='Helvetica-Bold'
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=5,
        fontName='Helvetica'
    )
    
    # Add header content
    elements.append(Paragraph("Library Book Catalog", title_style))
    elements.append(Paragraph(f"Complete Book Collection - Generated on {timezone.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style))
    
    # Add separator line
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1976d2'), spaceAfter=30))
    
    # Add book count
    elements.append(Paragraph(f"Total Books: {books.count()}", heading_style))
    elements.append(Spacer(1, 20))
    
    # Add book list with enhanced formatting
    for book in books:
        # Book container with border
        book_content = []
        
        # Book title with icon
        book_content.append(Paragraph(f"📚 {book.title}", book_title_style))
        
        # Book details with icons and better formatting
        book_content.extend([
            Paragraph(f"🔖 <b>ISBN:</b> {book.isbn}", info_style),
            Paragraph(f"🌐 <b>Language:</b> {book.get_language_display()}", info_style),
            Paragraph(f"✍️ <b>Authors:</b> {', '.join([author.name for author in book.authors.all()])}", info_style),
            Paragraph(f"🏷️ <b>Genres:</b> {', '.join([genre.name for genre in book.genres.all()])}", info_style)
        ])
        
        if book.publication_date:
            book_content.append(Paragraph(f"📅 <b>Published:</b> {book.publication_date.strftime('%B %d, %Y')}", info_style))
        
        # Add book content to elements
        for content in book_content:
            elements.append(content)
            
        # Add separator between books
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(
            width="90%", 
            thickness=0.5, 
            color=colors.HexColor('#e0e0e0'), 
            spaceBefore=10, 
            spaceAfter=10
        ))
    
    # Add footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#666666'),
        alignment=1  # Center alignment
    )
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("© Library Management System", footer_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
