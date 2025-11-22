/**
 * Copilot Companion Script
 * Extracts the 'companion' parameter from URL and injects it into chat context
 */

(function() {
    'use strict';
    
    console.log('🐾 Copilot Companion Script loaded');
    
    // Extract companion parameter from URL
    function getCompanionFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const companion = urlParams.get('companion');
        
        // Validate companion
        const validCompanions = ['dog', 'cat', 'eagle', 'raccoon', 'panda', 'dragon'];
        
        if (companion && validCompanions.includes(companion)) {
            console.log(`🎯 Companion detected: ${companion}`);
            return companion;
        }
        
        // Check localStorage as fallback
        try {
            const stored = localStorage.getItem('mh_companion_animal');
            if (stored && validCompanions.includes(stored)) {
                console.log(`💾 Companion from storage: ${stored}`);
                return stored;
            }
        } catch (e) {
            console.warn('Could not access localStorage:', e);
        }
        
        console.log('🐶 Using default companion: dog');
        return 'dog';
    }
    
    // Inject companion into Chainlit context
    function injectCompanion() {
        const companion = getCompanionFromURL();
        
        // Store in localStorage for persistence
        try {
            localStorage.setItem('mh_companion_animal', companion);
        } catch (e) {
            console.warn('Could not save to localStorage:', e);
        }
        
        // Attempt to inject into window context for backend access
        window.MENTAL_HEALTH_COMPANION = companion;
        
        // Listen for Chainlit ready event and inject companion
        document.addEventListener('chainlit-ready', function() {
            console.log('🔗 Chainlit ready, companion:', companion);
            
            // Try to inject companion into session
            if (window.Chainlit) {
                try {
                    // This will be accessible in the session metadata
                    window.Chainlit.companion = companion;
                } catch (e) {
                    console.warn('Could not set Chainlit.companion:', e);
                }
            }
        });
    }
    
    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectCompanion);
    } else {
        injectCompanion();
    }
})();
