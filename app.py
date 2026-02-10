from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from models import db, Service, Media, Booking, ContactMessage
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)

# ---------------- Routes ----------------
@app.route('/')
def index():
    services = Service.query.all()
    carousel_images = Media.query.filter_by(usage='carousel').all()
    hero_image = Media.query.filter_by(usage='hero').first()
    return render_template('index.html',
                          services=services,
                          carousel_images=carousel_images,
                          hero_image=hero_image)

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/about')
def about():
    carousel_images = Media.query.filter_by(usage='carousel').all()
    return render_template('about.html', carousel_images=carousel_images)

@app.route('/booking', methods=['POST'])
def booking():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    date = request.form.get('date')
    time = request.form.get('time')
    service_type = request.form.get('service_type')
    message = request.form.get('message')
    if name and email and phone and date and time and service_type:
        booking = Booking(
            name=name,
            email=email,
            phone=phone,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            time=time,
            service_type=service_type,
            message=message
        )
        db.session.add(booking)
        db.session.commit()
        flash('Бронирование успешно отправлено!', 'success')
    return redirect(url_for('index'))

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')
    if name and email and message:
        msg = ContactMessage(name=name, email=email, phone=phone, message=message)
        db.session.add(msg)
        db.session.commit()
        flash('Сообщение отправлено!', 'success')
    return redirect(url_for('index'))

# ---------------- Admin Routes ----------------
@app.route('/admin')
def admin_dashboard():
    return redirect(url_for('admin_services'))

@app.route('/admin/services', methods=['GET', 'POST'])
def admin_services():
    if request.method == 'POST':
        s = Service(
            title=request.form['title'],
            short_desc=request.form['short_desc'],
            long_desc=request.form['long_desc'],
            icon=request.form['icon']
        )
        db.session.add(s)
        db.session.commit()
        flash('Услуга добавлена!', 'success')
        return redirect(url_for('admin_services'))
    services = Service.query.all()
    return render_template('admin/services.html', services=services)

@app.route('/admin/media', methods=['GET', 'POST'])
def admin_media():
    if request.method == 'POST':
        file = request.files.get('file')
        usage = request.form.get('usage', 'other')
        alt_text = request.form.get('alt_text', '')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_name = f"{name}_{int(datetime.now().timestamp())}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            file.save(filepath)
            media = Media(filename=unique_name, alt_text=alt_text, usage=usage)
            db.session.add(media)
            db.session.commit()
            flash('Изображение загружено!', 'success')
            return redirect(url_for('admin_media'))
    media_items = Media.query.order_by(Media.created_at.desc()).all()
    return render_template('admin/media.html', media_items=media_items)

@app.route('/admin/media/delete/<int:media_id>', methods=['POST'])
def delete_media(media_id):
    media = Media.query.get_or_404(media_id)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], media.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(media)
    db.session.commit()
    flash('Изображение удалено.', 'success')
    return redirect(url_for('admin_media'))

@app.route('/admin/bookings')
def admin_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'POST':
        service.title = request.form['title']
        service.short_desc = request.form['short_desc']
        service.long_desc = request.form['long_desc']
        service.icon = request.form['icon']
        db.session.commit()
        flash('Услуга обновлена!', 'success')
        return redirect(url_for('admin_services'))
    return render_template('admin/edit_service.html', service=service)

@app.route('/admin/services/delete/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash('Услуга удалена.', 'success')
    return redirect(url_for('admin_services'))

@app.route('/admin/contacts')
def admin_contacts():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/contacts.html', messages=messages)

# ---------------- Init DB ----------------
with app.app_context():
    db.create_all()
    if Service.query.count() == 0:
        db.session.add(Service(
            title="Звукозапись",
            short_desc="Профессиональная запись вокала и инструментов в акустически подготовленном помещении.",
            long_desc="...",
            icon="fa-microphone"
        ))
        db.session.add(Service(
            title="Сведение",
            short_desc="Профессиональное сведение треков для идеального баланса.",
            long_desc="...",
            icon="fa-sliders-h"
        ))
        db.session.add(Service(
            title="Мастеринг",
            short_desc="Финальная обработка трека для выпуска на всех платформах.",
            long_desc="...",
            icon="fa-wave-square"
        ))
        db.session.commit()

    if Media.query.count() == 0:
        db.session.add(Media(filename="studio_1.jpg", alt_text="Основная студия", usage="carousel"))
        db.session.add(Media(filename="control_room.jpg", alt_text="Контрольная комната", usage="carousel"))
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


