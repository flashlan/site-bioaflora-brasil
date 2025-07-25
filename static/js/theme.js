// Theme Toggle Functionality
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        // Aplicar tema salvo
        this.applyTheme(this.theme);
        
        // Criar botão de alternância
        this.createToggleButton();
        
        // Event listeners
        this.bindEvents();
    }

    createToggleButton() {
        const button = document.createElement('button');
        button.className = 'theme-toggle';
        button.setAttribute('aria-label', 'Alternar tema');
        button.innerHTML = this.theme === 'dark' ? '☀️' : '🌙';
        
        document.body.appendChild(button);
        this.toggleButton = button;
    }

    bindEvents() {
        this.toggleButton.addEventListener('click', () => {
            this.toggleTheme();
        });

        // Detectar preferência do sistema
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addListener((e) => {
            if (!localStorage.getItem('theme')) {
                this.applyTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(this.theme);
        localStorage.setItem('theme', this.theme);
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        if (this.toggleButton) {
            this.toggleButton.innerHTML = theme === 'dark' ? '☀️' : '🌙';
        }

        // Atualizar meta theme-color para mobile
        let themeColorMeta = document.querySelector('meta[name="theme-color"]');
        if (!themeColorMeta) {
            themeColorMeta = document.createElement('meta');
            themeColorMeta.name = 'theme-color';
            document.head.appendChild(themeColorMeta);
        }
        
        const primaryColor = theme === 'dark' ? '#111827' : '#10b981';
        themeColorMeta.content = primaryColor;

        // Animação suave na transição
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        
        this.theme = theme;
    }
}

// Page Loader
window.addEventListener('load', function() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('fade-out');
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }, 1000); // Show loader for at least 1 second
    }
});

// Analytics helper functions
function trackPageScroll() {
    let scrollPercentage = 0;
    let maxScroll = 0;
    let scrollTimer = null;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const currentPercentage = Math.round((scrollTop / docHeight) * 100);
        
        if (currentPercentage > maxScroll) {
            maxScroll = currentPercentage;
            
            // Track milestone scrolls
            if ([25, 50, 75, 90].includes(currentPercentage) && currentPercentage > scrollPercentage) {
                scrollPercentage = currentPercentage;
                
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'scroll', {
                        'event_category': 'engagement',
                        'event_label': `${currentPercentage}%`,
                        'value': currentPercentage
                    });
                }
                
                if (typeof dataLayer !== 'undefined') {
                    dataLayer.push({
                        'event': 'scroll_depth',
                        'scroll_percentage': currentPercentage,
                        'page_location': window.location.pathname
                    });
                }
            }
        }
    });
}

function trackTimeOnPage() {
    const startTime = Date.now();
    
    // Track time milestones
    [30, 60, 120, 300].forEach(seconds => {
        setTimeout(() => {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'time_on_page', {
                    'event_category': 'engagement',
                    'event_label': `${seconds}s`,
                    'value': seconds
                });
            }
        }, seconds * 1000);
    });
    
    // Track total time on page unload
    window.addEventListener('beforeunload', function() {
        const timeSpent = Math.round((Date.now() - startTime) / 1000);
        
        if (typeof navigator.sendBeacon !== 'undefined' && typeof gtag !== 'undefined') {
            gtag('event', 'page_view_duration', {
                'event_category': 'engagement',
                'value': timeSpent,
                'transport_type': 'beacon'
            });
        }
    });
}

function trackNavigation() {
    // Track all navigation clicks
    document.querySelectorAll('nav a, .navbar a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const text = this.textContent.trim();
            
            if (typeof gtag !== 'undefined') {
                gtag('event', 'navigation_click', {
                    'event_category': 'navigation',
                    'event_label': text,
                    'link_url': href
                });
            }
            
            if (typeof dataLayer !== 'undefined') {
                dataLayer.push({
                    'event': 'navigation_click',
                    'link_text': text,
                    'link_url': href,
                    'click_location': 'main_navigation'
                });
            }
        });
    });
    
    // Track footer link clicks
    document.querySelectorAll('footer a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const text = this.textContent.trim();
            
            if (typeof gtag !== 'undefined') {
                gtag('event', 'footer_link_click', {
                    'event_category': 'navigation',
                    'event_label': text,
                    'link_url': href
                });
            }
        });
    });
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
    
    // Initialize analytics tracking
    trackPageScroll();
    trackTimeOnPage();
    trackNavigation();
});

// Animações e efeitos adicionais
document.addEventListener('DOMContentLoaded', () => {
    // Parallax effect no hero
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            heroSection.style.transform = `translateY(${parallax}px)`;
        });
    }

    // Animação de entrada para cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observar elementos para animação
    document.querySelectorAll('.card, .product-item, .stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Smooth scroll para links internos
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // WhatsApp Button Functionality
    const whatsappButton = document.getElementById('whatsappButton');
    if (whatsappButton) {
        whatsappButton.addEventListener('click', function() {
            // Configurações do WhatsApp
            const phoneNumber = '5542999575280'; // Número da Agronanobio
            const message = encodeURIComponent(
                'Olá! Vim através do site do Projeto Bio Aflora da Agronanobio. Gostaria de saber mais sobre o sistema agroflorestal com erva-mate nativa.'
            );
            
            // Detectar se é mobile ou desktop
            const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            let whatsappURL;
            if (isMobile) {
                // Para mobile - abre o app do WhatsApp
                whatsappURL = `whatsapp://send?phone=${phoneNumber}&text=${message}`;
            } else {
                // Para desktop - abre WhatsApp Web
                whatsappURL = `https://web.whatsapp.com/send?phone=${phoneNumber}&text=${message}`;
            }
            
            // Abrir WhatsApp em nova aba
            window.open(whatsappURL, '_blank');
            
            // Analytics tracking
            if (typeof gtag !== 'undefined') {
                gtag('event', 'whatsapp_click', {
                    'event_category': 'engagement',
                    'event_label': 'whatsapp_button',
                    'value': 1
                });
            }
            
            // Track via dataLayer for GTM
            if (typeof dataLayer !== 'undefined') {
                dataLayer.push({
                    'event': 'whatsapp_contact',
                    'contact_method': 'whatsapp',
                    'button_location': 'floating_button'
                });
            }
        });

        // Mostrar/esconder botão baseado no scroll
        let lastScrollTop = 0;
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > 300) {
                whatsappButton.style.opacity = '1';
                whatsappButton.style.visibility = 'visible';
            } else {
                whatsappButton.style.opacity = '0.7';
            }
            
            lastScrollTop = scrollTop;
        });
    }

    // Newsletter Functionality
    const newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = document.getElementById('newsletterEmail').value.trim();
            const button = newsletterForm.querySelector('.newsletter-btn');
            const buttonText = button.querySelector('.newsletter-text');
            const buttonLoading = button.querySelector('.newsletter-loading');
            
            // Validar email
            if (!email || !isValidEmail(email)) {
                showNewsletterAlert('Por favor, insira um email válido', 'error');
                return;
            }
            
            // Show loading state
            buttonText.style.display = 'none';
            buttonLoading.style.display = 'inline-block';
            button.disabled = true;
            
            // Enviar para o backend
            fetch('/newsletter/cadastrar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `email=${encodeURIComponent(email)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Success animation
                    buttonText.textContent = 'Inscrito! ✓';
                    buttonText.style.display = 'inline-block';
                    buttonLoading.style.display = 'none';
                    button.classList.add('btn-outline-success');
                    button.classList.remove('btn-success');
                    
                    // Reset form
                    newsletterForm.reset();
                    
                    // Show success message
                    showNewsletterAlert(data.message, 'success');
                    
                    // Analytics tracking - Newsletter signup success
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'newsletter_signup', {
                            'event_category': 'lead_generation',
                            'event_label': 'footer_newsletter',
                            'value': 1
                        });
                        
                        gtag('event', 'generate_lead', {
                            'currency': 'BRL',
                            'value': 10.0 // Estimated lead value
                        });
                    }
                    
                    // Track via dataLayer for GTM
                    if (typeof dataLayer !== 'undefined') {
                        dataLayer.push({
                            'event': 'newsletter_subscription',
                            'subscription_type': 'email_newsletter',
                            'form_location': 'footer',
                            'user_email_domain': email.split('@')[1]
                        });
                    }
                    
                    // Reset button after 3 seconds
                    setTimeout(() => {
                        buttonText.textContent = 'Inscrever-se';
                        button.classList.remove('btn-outline-success');
                        button.classList.add('btn-success');
                        button.disabled = false;
                    }, 3000);
                } else {
                    // Error handling
                    showNewsletterAlert(data.message, 'error');
                    resetNewsletterButton();
                    
                    // Analytics tracking - Newsletter signup error
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'newsletter_signup_error', {
                            'event_category': 'form_error',
                            'event_label': 'footer_newsletter',
                            'error_message': data.message
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showNewsletterAlert('Erro ao processar inscrição. Tente novamente.', 'error');
                resetNewsletterButton();
            });
            
            function resetNewsletterButton() {
                buttonText.style.display = 'inline-block';
                buttonLoading.style.display = 'none';
                button.disabled = false;
            }
        });
    }
    
    function showNewsletterAlert(message, type) {
        // Remove alertas existentes
        const existingAlerts = document.querySelectorAll('.newsletter-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Criar novo alerta
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} mt-3 newsletter-alert`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        const newsletterForm = document.getElementById('newsletterForm');
        newsletterForm.appendChild(alertDiv);
        
        // Remove alert after 8 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 8000);
    }

    // Scroll to Top Button
    const scrollToTopBtn = document.getElementById('scrollToTop');
    if (scrollToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });

        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Search Functionality
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = searchInput.value.trim();
            
            if (query) {
                // Simple client-side search implementation
                performSearch(query);
            }
        });
    }
});

// Search functionality
function performSearch(query) {
    // Search content mapping
    const searchContent = {
        'erva-mate': { page: 'saiba_mais', title: 'Saiba Mais sobre Erva-Mate' },
        'chimarrão': { page: 'saiba_mais', title: 'Como preparar Chimarrão' },
        'sustentabilidade': { page: 'sobre_nos', title: 'Nosso Compromisso Sustentável' },
        'produtos': { page: 'inicio', title: 'Nossos Produtos' },
        'contato': { page: 'contato', title: 'Entre em Contato' },
        'sobre': { page: 'sobre_nos', title: 'Sobre Nós' },
        'blog': { page: 'blog', title: 'Blog Sustentável' },
        'orgânico': { page: 'saiba_mais', title: 'Produtos Orgânicos' },
        'premium': { page: 'inicio', title: 'Produtos Premium' },
        'mata atlântica': { page: 'sobre_nos', title: 'Preservação Ambiental' }
    };

    // Find best match
    const lowerQuery = query.toLowerCase();
    let bestMatch = null;
    
    for (const [key, value] of Object.entries(searchContent)) {
        if (lowerQuery.includes(key) || key.includes(lowerQuery)) {
            bestMatch = value;
            break;
        }
    }

    if (bestMatch) {
        // Show loading state
        const searchBtn = document.querySelector('.search-btn');
        const originalHTML = searchBtn.innerHTML;
        searchBtn.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
        
        // Analytics tracking - Successful search
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search', {
                'search_term': query,
                'result_found': true,
                'result_page': bestMatch.page
            });
        }
        
        // Track via dataLayer for GTM
        if (typeof dataLayer !== 'undefined') {
            dataLayer.push({
                'event': 'site_search',
                'search_term': query,
                'search_results': 1,
                'result_page': bestMatch.page
            });
        }
        
        // Simulate search delay and redirect
        setTimeout(() => {
            window.location.href = `/${bestMatch.page}`;
        }, 500);
    } else {
        // Show no results message
        showSearchAlert(`Nenhum resultado encontrado para "${query}". Tente termos como: erva-mate, chimarrão, sustentabilidade, produtos.`);
        
        // Analytics tracking - No results search
        if (typeof gtag !== 'undefined') {
            gtag('event', 'search', {
                'search_term': query,
                'result_found': false
            });
        }
        
        // Track via dataLayer for GTM
        if (typeof dataLayer !== 'undefined') {
            dataLayer.push({
                'event': 'site_search',
                'search_term': query,
                'search_results': 0
            });
        }
    }
}

function showSearchAlert(message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 1050; max-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}