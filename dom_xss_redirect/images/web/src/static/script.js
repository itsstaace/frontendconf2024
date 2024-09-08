document.addEventListener('DOMContentLoaded', function () {
    initializeRedirectButton();
    handleRedirectParam();
});

/**
 * Инициализирует кнопку перенаправления, добавляя ей соответствующий URL.
 */
function initializeRedirectButton() {
    const redirectButton = document.getElementById('redirectButton');

    redirectButton.addEventListener('click', function () {
        window.location.href = '/survey';
    });
}

/**
 * Обрабатывает параметр redirect из URL и перенаправляет на указанный в нем URL.
 */
function handleRedirectParam() {
    const urlParams = new URLSearchParams(window.location.search);
    let redirectParam = urlParams.get('redirect');
    
    if (window.location.pathname === '/survey') {
        if (!redirectParam) {
            const defaultRedirectUrl = new URL('/survey', window.location.origin);
            redirectParam = defaultRedirectUrl.toString();
        }
        
    }
    
    if (redirectParam){
        window.location.replace(redirectParam);
    }
    
}