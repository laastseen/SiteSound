// Carousel
let currentSlideIndex = 0;
const track = document.getElementById('carouselTrack');
const dotsContainer = document.getElementById('carouselDots');

if (track && dotsContainer) {
    const slides = document.querySelectorAll('.carousel-slide');
    const totalSlides = slides.length;

    // Create dots if not exists
    if (dotsContainer.children.length === 0) {
        for (let i = 0; i < totalSlides; i++) {
            const dot = document.createElement('span');
            dot.className = 'carousel-dot';
            if (i === 0) dot.classList.add('active');
            dot.onclick = () => currentSlide(i);
            dotsContainer.appendChild(dot);
        }
    }

    const dots = document.querySelectorAll('.carousel-dot');

    function showSlide(index) {
        if (index >= totalSlides) index = 0;
        if (index < 0) index = totalSlides - 1;
        track.style.transform = `translateX(-${index * 100}%)`;
        dots.forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
        currentSlideIndex = index;
    }

    function nextSlide() { showSlide(currentSlideIndex + 1); }
    function prevSlide() { showSlide(currentSlideIndex - 1); }
    function currentSlide(index) { showSlide(index); }

    setInterval(nextSlide, 5000);

    window.prevSlide = prevSlide;
    window.nextSlide = nextSlide;
    window.currentSlide = currentSlide;
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            window.scrollTo({
                top: target.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// Sticky header
window.addEventListener('scroll', () => {
    const header = document.querySelector('header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(0, 0, 0, 0.98)';
        header.style.boxShadow = '0 5px 20px rgba(0, 0, 0, 0.3)';
    } else {
        header.style.background = 'rgba(0, 0, 0, 0.95)';
        header.style.boxShadow = 'none';
    }
});

// Set min date
const todayInput = document.getElementById('bookingDate');
if (todayInput) {
    const today = new Date().toISOString().split('T')[0];
    todayInput.min = today;
}