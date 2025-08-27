/**
 * Form Enhancements for UniShowTime
 * Adds animations and interactive effects to form elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Target all form input fields, textareas, and select elements
    const formElements = document.querySelectorAll('input:not([type="radio"]):not([type="checkbox"]), textarea, select');
    const formButtons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    // Add floating label effect and focus animations
    formElements.forEach(element => {
        // Add transition effects
        element.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        // Focus effect with ripple
        element.addEventListener('focus', function() {
            this.classList.add('form-field-focus');
            createRippleEffect(this);
        });
        
        // Remove focus class
        element.addEventListener('blur', function() {
            this.classList.remove('form-field-focus');
        });
        
        // Add typing animation
        if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
            element.addEventListener('input', function() {
                if (this.value.length > 0) {
                    this.classList.add('has-content');
                } else {
                    this.classList.remove('has-content');
                }
            });
            
            // Check initial state
            if (element.value.length > 0) {
                element.classList.add('has-content');
            }
        }
    });
    
    // Add button animations
    formButtons.forEach(button => {
        button.addEventListener('mouseover', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 10px 25px rgba(84, 119, 146, 0.4)';
        });
        
        button.addEventListener('mouseout', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px rgba(84, 119, 146, 0.1)';
        });
        
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(0)';
            createButtonPressEffect(this);
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-3px)';
        });
    });
    
    // Enhance radio buttons and checkboxes
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                createRadioSelectEffect(this);
            }
        });
    });
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            createCheckboxToggleEffect(this);
        });
    });
    
    // Add form submission animation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Don't prevent form submission, just add animation
            const button = this.querySelector('button[type="submit"], input[type="submit"]');
            if (button) {
                createFormSubmitEffect(button);
            }
        });
    });
    
    // Create ripple effect on input focus
    function createRippleEffect(element) {
        const rect = element.getBoundingClientRect();
        const ripple = document.createElement('div');
        
        ripple.className = 'form-field-ripple';
        ripple.style.position = 'absolute';
        ripple.style.width = '5px';
        ripple.style.height = '5px';
        ripple.style.borderRadius = '50%';
        ripple.style.backgroundColor = '#94B4C1';
        ripple.style.opacity = '0.6';
        ripple.style.transform = 'scale(1)';
        ripple.style.left = rect.width / 2 + 'px';
        ripple.style.top = '50%';
        
        // Position the ripple relative to the input
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        // Animate the ripple
        anime({
            targets: ripple,
            scale: [1, 15],
            opacity: [0.6, 0],
            duration: 800,
            easing: 'easeOutExpo',
            complete: function() {
                ripple.remove();
            }
        });
    }
    
    // Create button press effect
    function createButtonPressEffect(button) {
        anime({
            targets: button,
            scale: [1, 0.95],
            duration: 100,
            easing: 'easeInOutQuad',
            complete: function() {
                anime({
                    targets: button,
                    scale: [0.95, 1],
                    duration: 300,
                    easing: 'easeOutElastic(1, .5)'
                });
            }
        });
    }
    
    // Create radio button selection effect
    function createRadioSelectEffect(radio) {
        const parentLabel = radio.closest('label');
        if (parentLabel) {
            anime({
                targets: parentLabel,
                scale: [1, 1.05, 1],
                duration: 400,
                easing: 'easeOutElastic(1, .5)'
            });
        }
    }
    
    // Create checkbox toggle effect
    function createCheckboxToggleEffect(checkbox) {
        const label = checkbox.nextElementSibling;
        if (label) {
            anime({
                targets: label,
                translateX: [0, 5, 0],
                duration: 300,
                easing: 'easeOutElastic(1, .5)'
            });
        }
    }
    
    // Create form submit effect
    function createFormSubmitEffect(button) {
        // Add a subtle pulse animation
        anime({
            targets: button,
            scale: [1, 1.05, 1],
            opacity: [1, 0.8, 1],
            duration: 600,
            easing: 'easeInOutQuad'
        });
    }
    
    // Add password strength indicator for password fields
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        // Create strength indicator
        const strengthIndicator = document.createElement('div');
        strengthIndicator.className = 'password-strength-indicator';
        strengthIndicator.style.height = '3px';
        strengthIndicator.style.width = '0%';
        strengthIndicator.style.backgroundColor = '#94B4C1';
        strengthIndicator.style.transition = 'all 0.3s ease';
        strengthIndicator.style.marginTop = '5px';
        strengthIndicator.style.borderRadius = '3px';
        
        // Insert after password field
        field.parentNode.insertBefore(strengthIndicator, field.nextSibling);
        
        // Add event listener to update strength
        field.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updateStrengthIndicator(strengthIndicator, strength);
        });
    });
    
    // Calculate password strength (simple version)
    function calculatePasswordStrength(password) {
        if (!password) return 0;
        
        let strength = 0;
        
        // Length check
        if (password.length >= 8) strength += 25;
        
        // Contains lowercase
        if (/[a-z]/.test(password)) strength += 25;
        
        // Contains uppercase
        if (/[A-Z]/.test(password)) strength += 25;
        
        // Contains number or special char
        if (/[0-9!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 25;
        
        return strength;
    }
    
    // Update strength indicator
    function updateStrengthIndicator(indicator, strength) {
        indicator.style.width = strength + '%';
        
        // Change color based on strength
        if (strength < 25) {
            indicator.style.backgroundColor = '#ff4d4d'; // Red
        } else if (strength < 50) {
            indicator.style.backgroundColor = '#ffa64d'; // Orange
        } else if (strength < 75) {
            indicator.style.backgroundColor = '#ffff4d'; // Yellow
        } else {
            indicator.style.backgroundColor = '#4dff4d'; // Green
        }
    }
});