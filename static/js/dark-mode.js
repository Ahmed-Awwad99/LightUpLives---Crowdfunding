document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateToggleIcon(true);
    }

    // Add click event to the dark mode toggle
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            toggleDarkMode();
        });
    }
});

function toggleDarkMode() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    updateToggleIcon(isDarkMode);
}

function updateToggleIcon(isDarkMode) {
    const toggleIcon = document.querySelector('.dark-mode-toggle i');
    if (toggleIcon) {
        toggleIcon.className = isDarkMode ? 'fas fa-moon' : 'fas fa-sun';
    }
} 